import subprocess, re, json, sys, os
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "methodology"))
import resolve as meth

REPO = "/home/user/converge-dashboards"
def git(*a):
    return subprocess.run(["git","-C",REPO,*a], capture_output=True, text=True).stdout

commits = [l.split("\x1f") for l in
           git("log","--reverse","--format=%H\x1f%ad\x1f%s","--date=iso-strict","--","index.html").strip().split("\n") if l]

CARD = re.compile(r'<div class="stock-card"([^>]*)>(.*?)(?=<div class="stock-card"|</div></section>|$)', re.S)
ATTR = lambda s,k: (re.search(rf'data-{k}="([^"]*)"', s) or [None,None])[1]
PRICE = re.compile(r'class="price ltr">\s*\$?([\d,]+\.\d{2})\s*([+-][\d.]+%)?[^<]*<')
SCORE = re.compile(r'class="chip score2?">\s*([^<]{0,60})<')
TIER1 = re.compile(r'<section id="tier1".*?(?=<section id=)', re.S)

# Two markup eras. From 2026-08-27 the cards carry data-ticker/data-name; before
# that the ticker only exists as the rendered <span class="ticker ltr"> and the
# data attribute is data-q, a lowercased search string. Reading the span is not
# a fallback of convenience — it is the only place the older ticker was ever
# written, and skipping it is what kept eight publication days out of the ledger.
SPAN_TICKER = re.compile(r'class="ticker ltr">\s*([A-Z.\-]{1,6})\s*<')
SPAN_NAME = re.compile(r'class="company-name">\s*([^<]*?)\s*<')


def read_card(attrs, body):
    t = ATTR(attrs, "ticker")
    src = "data-ticker"
    if not t:
        m = SPAN_TICKER.search(body)
        if not m:
            return None
        t, src = m.group(1), "ticker-span"
    name = ATTR(attrs, "name")
    if not name:
        m = SPAN_NAME.search(body)
        # the older span is "Broadcom Inc. · טכנולוגיה" — the sector is its own field
        name = m.group(1).split(" · ")[0] if m else None
    return t, name, src

VERSIONS = meth.load_all()

rows, skipped, unparsed = [], 0, []
for sha, date, subj in commits:
    html = git("show", f"{sha}:index.html")
    if not html:
        skipped += 1; continue
    m = TIER1.search(html)
    if not m:
        skipped += 1; continue
    block = m.group(0)
    before = len(rows)
    for attrs, body in CARD.findall(block):
        card = read_card(attrs, body)
        if not card: continue
        t, name, src = card
        p = PRICE.search(body); s = SCORE.search(body)
        rows.append(OrderedDict(
            date=date[:10], sha=sha[:7], ticker=t,
            name=name, sector=ATTR(attrs,"sector"),
            price=float(p.group(1).replace(",","")) if p else None,
            chg=p.group(2) if p and p.group(2) else None,
            conviction=s.group(1).strip() if s else None,
            ticker_source=src,
        ))
    # A tier-1 section that yields no tickers is a hole in the record, not a
    # no-op. Say so per commit instead of letting it vanish into a counter.
    if len(rows) == before:
        cards = len(re.findall(r'<div class="stock-card"', block))
        if cards:
            unparsed.append((sha[:7], date[:10], cards))

# de-dup: keep last commit of each day (the day's final published state)
by_day = OrderedDict()
for r in rows: by_day.setdefault(r["date"], {})[r["sha"]] = None
final = {d: list(sh)[-1] for d, sh in by_day.items()}
ledger = [r for r in rows if final.get(r["date"]) == r["sha"]]

# Stamp every pick with the rule set that produced it. Resolution is by commit,
# never by date: 2026-08-19 published two different methodology versions, so a
# date lookup for that day is genuinely ambiguous. A commit no version claims
# gets a null stamp — an invented version is worse than an admitted gap,
# because it silently licenses pooling picks made under different rules.
for r in ledger:
    vid = meth.version_for_commit(r["sha"], VERSIONS)
    v = VERSIONS.get(vid)
    r["methodology_version"] = vid
    r["methodology_rule_hash"] = v["rule_hash"] if v else None
    # Under a carry-forward version the row is a re-publication of an earlier
    # run's pick, not a fresh entry event. score.py must not treat it as one.
    r["carried_forward"] = bool(v and v["selection"]["carry_forward"]["enabled"]) if v else None

out = os.path.join(HERE, "tier1_ledger.jsonl")
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
    vid = next(r['methodology_version'] for r in ledger if r['date']==d)
    cf = " (carried forward)" if next(r['carried_forward'] for r in ledger if r['date']==d) else ""
    print(f"  {d}  {vid or 'UNCLAIMED':<4} n={len(ts):<2} {' '.join(ts)}{cf}")

print("\nHOLDING PERIOD PER TICKER (days it appeared in tier-1)")
seen = {}
for r in ledger: seen.setdefault(r['ticker'], []).append(r['date'])
for t, ds in sorted(seen.items(), key=lambda x:-len(x[1])):
    print(f"  {t:<6} {len(ds)}d  first={ds[0]}  last={ds[-1]}  price_first={[r['price'] for r in ledger if r['ticker']==t][0]}")

unstamped = [r for r in ledger if r["methodology_version"] is None]
if unstamped:
    print(f"\nUNSTAMPED: {len(unstamped)} rows whose commit no methodology version "
          f"claims. Register the version before scoring them.")

if unparsed:
    total = sum(n for _,_,n in unparsed)
    print(f"\nNOT IN THE LEDGER: {len(unparsed)} commits carry a tier-1 section with "
          f"{total} cards this parser cannot read. Investigate before trusting a count.")
    for sha, d, n in unparsed:
        print(f"  {d}  {sha}  {n} tier-1 cards unread")
