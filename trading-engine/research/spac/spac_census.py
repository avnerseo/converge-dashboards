import csv, collections, datetime as dt

US={'NASDAQ','NYSE','NYSE MKT','AMEX'}
ARTIFACT={'2026-08-27'}     # 601 securities file-wide on one date = bulk refresh, not events
def d(s):
    try: return dt.date.fromisoformat(s)
    except Exception: return None

rows=list(csv.DictReader(open('delisted.csv')))
# flag any other suspicious bulk dates
allc=collections.Counter(r['delistingDate'] for r in rows)
susp={k for k,v in allc.items() if v>=40}
print("bulk-suspicious dates (>=40 delistings file-wide):", sorted(susp))

common=[]
for r in rows:
    if r['assetType']!='Stock' or r['exchange'] not in US: continue
    nm=r['name'].lower()
    if 'acquisition' not in nm: continue
    if any(k in nm for k in ('warrant','unit','right')): continue   # de-dup by NAME
    if r['delistingDate'] in ARTIFACT: continue
    ipo, de = d(r['ipoDate']), d(r['delistingDate'])
    if not ipo or not de: continue
    life=(de-ipo).days/365.25
    if not (0.5<=life<=5.0): continue
    common.append((r['symbol'], r['name'], ipo, de, life))

print(f"\nSPAC common shares meeting all pre-registered rules: {len(common)}")
byyr=collections.Counter(s[3].year for s in common)
print("\nterminations by year (UPPER BOUND on liquidations; 2026 excl. artifact date):")
for y in range(2016,2027):
    n=byyr.get(y,0)
    print(f"  {y}: {n:4d}  {'#'*min(n//3,60)}")

today=dt.date(2026,8,28)
for lbl,lo,hi in (("trailing 12m", dt.date(2025,8,28), today),
                  ("prior 12m",    dt.date(2024,8,28), dt.date(2025,8,28)),
                  ("12m before",   dt.date(2023,8,28), dt.date(2024,8,28))):
    print(f"{lbl:14s} {lo} .. {hi}: {sum(1 for s in common if lo<=s[3]<hi)}")
print(f"\nhistorical mean 2019-2025 (background only): {sum(byyr.get(y,0) for y in range(2019,2026))/7:.1f}/yr")
