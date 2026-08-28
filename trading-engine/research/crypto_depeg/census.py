import csv, collections

ENTRY = 0.9900     # pre-registered: entry giving >=1.0% gross to par
REPEG = 0.9990     # pre-registered: episode ends on close >= 0.9990
PREM  = 1.0100     # pre-registered: premium side

def load(path):
    rows=[]
    with open(path) as f:
        for r in csv.DictReader(f):
            rows.append((r['timestamp'], float(r['low']), float(r['close']), float(r['high'])))
    rows.sort()                      # chronological
    return rows

def episodes(rows, key):
    """key: 'close' or 'low' trigger. Consecutive dips w/o a repeg = ONE episode."""
    eps=[]; inep=False; start=None; worst=None
    for ts, low, close, high in rows:
        trig = (close if key=='close' else low) <= ENTRY
        if trig and not inep:
            inep=True; start=ts; worst=(close if key=='close' else low)
        elif trig and inep:
            worst=min(worst, close if key=='close' else low)
        if inep and close >= REPEG:
            eps.append((start, ts, worst)); inep=False
    if inep: eps.append((start, rows[-1][0], worst))
    return eps

def report(name, rows):
    n=len(rows); first=rows[0][0]; last=rows[-1][0]
    yrs=n/365.25
    print(f"\n=== {name} ===")
    print(f"coverage {first} .. {last}   {n} daily bars   {yrs:.2f} years")
    mn_c=min(r[2] for r in rows); mn_c_d=[r[0] for r in rows if r[2]==mn_c][0]
    mn_l=min(r[1] for r in rows); mn_l_d=[r[0] for r in rows if r[1]==mn_l][0]
    print(f"min CLOSE {mn_c:.5f} on {mn_c_d}   -> max gross to par {100*(1/mn_c-1):.4f}%")
    print(f"min LOW   {mn_l:.5f} on {mn_l_d}")

    for key,label in (('close','EXECUTABLE (close<=0.99)'),('low','UPPER BOUND (low<=0.99, NOT executable)')):
        eps=episodes(rows,key)
        days=sum(1 for r in rows if (r[2] if key=='close' else r[1])<=ENTRY)
        byyr=collections.Counter(e[0][:4] for e in eps)
        print(f"\n  {label}: {len(eps)} episodes / {days} days  = {len(eps)/yrs:.2f} episodes/yr")
        print("   " + "  ".join(f"{y}:{byyr.get(y,0)}" for y in sorted({r[0][:4] for r in rows})))

    prem=[r for r in rows if r[2]>=PREM]
    print(f"\n  PREMIUM side (close>=1.01, needs inventory): {len(prem)} days"
          + (f", years " + ",".join(sorted({d[0][:4] for d in prem})) if prem else ""))

rows=load('dai_daily.csv')
report("DAI/USD  (Alpha Vantage daily)", rows)

# DAI regime split: pre-PSM vs post-PSM (Maker PSM launched 2020-12)
print("\n--- DAI split at 2021-01-01 (PSM era begins) ---")
report("DAI  pre-2021 (no 1:1 redemption mechanism at all)", [r for r in rows if r[0]<'2021-01-01'])
report("DAI  2021-01-01 onward (PSM era)", [r for r in rows if r[0]>='2021-01-01'])
