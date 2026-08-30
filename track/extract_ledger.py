import subprocess, re, json, sys
from collections import OrderedDict

REPO = "/home/user/converge-dashboards"
def git(*a):
    return subprocess.run(["git","-C",REPO,*a], capture_output=True, text=True).stdout

commits = [l.split("\x1f") for l in
           git("log","--reverse","--format=%H\x1f%ad\x1f%s","--date=iso-strict","--","index.html").strip().split("\n") if l]

CARD = re.compile(r'<div class="stock-card"([^>]*)>(.*?)(?=<div class="stock-card"|</div></section>|$)', re.S)
ATTR = lambda s,k: (re.search(rf'data-{k}="([^"]*)"', s) or [None,None])[1]
PRICE = re.compile(r'class="price ltr">\s*\$?([\d,]+\.\d{2})\s*([+-][\d.]+%)?[^<]*<')
SCORE = re.compile(r'class="chip score2?">\s*([^<]{0,40})<')
TIER1 = re.compile(r'<section id="tier1".*?(?=<section id=)', re.S)

rows, skipped = [], 0
for sha, date, subj in commits:
    html = git("show", f"{sha}:index.html")
    if not html:
        skipped += 1; continue
    m = TIER1.search(html)
    if not m:
        skipped += 1; continue
    block = m.group(0)
    for attrs, body in CARD.findall(block):
        t = ATTR(attrs, "ticker")
        if not t: continue
        p = PRICE.search(body); s = SCORE.search(body)
        rows.append(OrderedDict(
            date=date[:10], sha=sha[:7], ticker=t,
            name=ATTR(attrs,"name"), sector=ATTR(attrs,"sector"),
            price=float(p.group(1).replace(",","")) if p else None,
            chg=p.group(2) if p and p.group(2) else None,
            conviction=s.group(1).strip() if s else None,
        ))

# de-dup: keep last commit of each day (the day's final published state)
by_day = OrderedDict()
for r in rows: by_day.setdefault(r["date"], {})[r["sha"]] = None
final = {d: list(sh)[-1] for d, sh in by_day.items()}
ledger = [r for r in rows if final.get(r["date"]) == r["sha"]]

out = "/home/user/converge-dashboards/track/tier1_ledger.jsonl"
with open(out,"w") as f:
    for r in ledger: f.write(json.dumps(r, ensure_ascii=False)+"\n")

print(f"commits scanned : {len(commits)}")
print(f"no tier1/parse  : {skipped}")
print(f"picks captured  : {len(ledger)} rows across {len(final)} publication days")
print(f"written         : {out}\n")

days = sorted(final)
print("PICKS PER DAY")
for d in days:
    ts = [r['ticker'] for r in ledger if r['date']==d]
    print(f"  {d}  n={len(ts):<2} {' '.join(ts)}")

print("\nHOLDING PERIOD PER TICKER (days it appeared in tier-1)")
seen = {}
for r in ledger: seen.setdefault(r['ticker'], []).append(r['date'])
for t, ds in sorted(seen.items(), key=lambda x:-len(x[1])):
    print(f"  {t:<6} {len(ds)}d  first={ds[0]}  last={ds[-1]}  price_first={[r['price'] for r in ledger if r['ticker']==t][0]}")
