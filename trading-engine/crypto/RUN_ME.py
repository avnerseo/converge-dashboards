#!/usr/bin/env python3
"""
One file, one command. Downloads Binance 1-minute history and finds the best
grid settings from it.

    python RUN_ME.py

Writes RESULTS.txt next to itself -- send that file back.
Needs nothing but Python. No API key, no account, read-only public data.
"""
import csv, datetime as dt, io, json, os, sys, time, urllib.request, zipfile

SYMBOLS = ["XRPUSDT", "TRXUSDT"]
MONTHS  = 18
CAPITAL = 200.0
FEE     = 0.00075      # VIP0 spot with BNB discount
MIN_NOTIONAL = 5.0

OUT = []
def say(s=""):
    print(s); OUT.append(str(s))

# ---------- download ----------
def months(n):
    d = dt.date.today().replace(day=1); r=[]
    for i in range(n,0,-1):
        y,m = d.year, d.month-i
        while m<=0: m+=12; y-=1
        r.append(f"{y:04d}-{m:02d}")
    return r

def grab(sym):
    rows=[]
    for ym in months(MONTHS):
        url=f"https://data.binance.vision/data/spot/monthly/klines/{sym}/1m/{sym}-1m-{ym}.zip"
        try:
            with urllib.request.urlopen(url, timeout=120) as r: blob=r.read()
            with zipfile.ZipFile(io.BytesIO(blob)) as z:
                with z.open(z.namelist()[0]) as f:
                    n=0
                    for line in io.TextIOWrapper(f,"utf-8"):
                        p=line.split(",")
                        if not p[0].strip().lstrip("-").isdigit(): continue
                        ts=int(p[0])
                        if ts>1e13: ts//=1000
                        rows.append((ts,float(p[2]),float(p[3]),float(p[4]))); n+=1
            print(f"    {ym}  {n:,} bars")
        except Exception as e:
            print(f"    {ym}  skipped ({getattr(e,'code',type(e).__name__)})")
        time.sleep(0.2)
    # the monthly archive lags, so fill the current partial month from REST
    if rows:
        start=max(r[0] for r in rows)+60_000
        now=int(time.time()*1000)
        n0=len(rows)
        while start < now:
            try:
                u=(f"https://api.binance.com/api/v3/klines?symbol={sym}"
                   f"&interval=1m&startTime={start}&limit=1000")
                with urllib.request.urlopen(u, timeout=30) as r:
                    d=json.loads(r.read())
            except Exception as e:
                print(f"    rest fill stopped: {type(e).__name__}"); break
            if not d: break
            for k in d:
                rows.append((int(k[0]), float(k[2]), float(k[3]), float(k[4])))
            start=int(d[-1][0])+60_000
            time.sleep(0.2)
        print(f"    current month via REST: {len(rows)-n0:,} bars")
    return sorted(set(rows))

# ---------- grid simulation ----------
def simulate(bars, lo, hi, n, capital):
    """Per-level slot model -- how a real grid bot actually works.

    A buy order rests at levels[j]. When it fills, a sell order is placed at
    levels[j+1]. That pair is what earns one step. Matching is PER LEVEL.

    An earlier version used a LIFO stack of buy prices; once the inventory
    cap bound during a long decline it started selling lots bought near the
    top of the range at prices near the bottom, which turned realised grid
    profit negative -- an impossible result that revealed the bug.
    """
    step=(hi-lo)/n
    levels=[lo+step*i for i in range(n+1)]
    q=capital/n
    hold=[False]*n
    filled=0; realised=0.0; trades=0; out=0

    def idx(p):
        if p<=lo: return 0
        if p>=hi: return n
        return min(n, max(0, int((p-lo)/step)))

    cur=idx(bars[0][3])
    for (_ts,h,l,c) in bars:
        if c<lo or c>hi: out+=1
        for p in ((l,h,c) if abs(l-bars[0][3])<abs(h-bars[0][3]) else (h,l,c)):
            tgt=idx(p)
            while cur>tgt:                       # crossing levels[cur] downward
                j=cur
                if j<n and not hold[j] and filled<n:
                    hold[j]=True; filled+=1; realised -= q*FEE
                cur-=1
            while cur<tgt:                       # crossing levels[cur+1] upward
                j=cur
                if j<n and hold[j]:
                    proceeds=q*(levels[j+1]/levels[j])
                    realised += (proceeds-q) - proceeds*FEE
                    hold[j]=False; filled-=1; trades+=1
                cur+=1
    final=bars[-1][3]
    unreal=sum(q*(final/levels[j]-1) for j in range(n) if hold[j])
    return trades, realised, unreal, realised+unreal, filled*q, out/len(bars)
# ---------- main ----------
say("="*72)
say("GRID PARAMETER SCAN -- generated " + dt.datetime.now().isoformat(timespec="seconds"))
say("v2: full accounting. realised grid profit AND unsold inventory marked to market.")
say("="*72)

for sym in SYMBOLS:
    print(f"\nDownloading {sym} ({MONTHS} months of 1-minute bars)...")
    bars = grab(sym)
    if len(bars) < 10000:
        say(f"\n{sym}: only {len(bars)} bars -- skipping"); continue
    px = bars[-1][3]; px0 = bars[0][3]
    days = (bars[-1][0]-bars[0][0])/86400000
    bh = 100*(px/px0-1)
    say("")
    say(f"### {sym}   {len(bars):,} bars, {days:.0f} days, "
        f"{dt.datetime.utcfromtimestamp(bars[0][0]/1000).date()} -> "
        f"{dt.datetime.utcfromtimestamp(bars[-1][0]/1000).date()}")
    say(f"    price {px0:.5f} -> {px:.5f}    BUY-AND-HOLD: {bh:+.1f}%")
    say("")
    say(f"    {'range':>7}{'grids':>6}{'step':>7}{'trades':>8}{'grid$':>9}"
        f"{'stuck$':>9}{'TOTAL$':>9}{'TOT%':>8}{'vs hold':>9}{'out':>6}")
    say("    "+"-"*78)
    best=None
    for w in (0.05,0.10,0.15,0.20,0.30,0.40):
        for n in (10,20,40,80):
            if CAPITAL/n < MIN_NOTIONAL: continue
            lo,hi = px*(1-w), px*(1+w)
            t,r,u,tot,stuck,out = simulate(bars,lo,hi,n,CAPITAL)
            totpct=100*tot/CAPITAL
            say(f"    {'+-'+str(int(100*w))+'%':>7}{n:>6}{200*w/n:>6.2f}%"
                f"{t:>8}{r:>9.2f}{u:>9.2f}{tot:>9.2f}{totpct:>7.1f}%"
                f"{totpct-bh:>+8.1f}{100*out:>5.0f}%")
            if best is None or tot>best[0]: best=(tot,w,n,200*w/n,t,r,u,out)
    if best:
        tot,w,n,step,t,r,u,out=best
        say("")
        say(f"    BEST TOTAL: range +-{100*w:.0f}%  ({px*(1-w):.5f} - {px*(1+w):.5f}), {n} grids, step {step:.2f}%")
        say(f"      grid profit {r:+.2f}   unsold inventory {u:+.2f}   TOTAL {tot:+.2f} on ${CAPITAL:.0f}")
        say(f"      = {100*tot/CAPITAL:+.1f}%  vs buy-and-hold {bh:+.1f}%  ->  {100*tot/CAPITAL-bh:+.1f}pp")
        if 100*tot/CAPITAL < bh:
            say(f"      *** LOSES TO SIMPLY HOLDING. the grid is not worth running here. ***")

say("")
say("Reading this table:")
say("  grid$  = realised profit from completed buy-sell pairs")
say("  stuck$ = lots still held at the end, marked to the final price")
say("  TOTAL$ = what you would actually have. THIS is the number that matters.")
say("  vs hold = percentage points better/worse than just holding the coin.")
say("")
say("CAVEAT: assumes every resting order fills at its level with no slippage")
say("or queue position, so TOTAL is still an optimistic upper bound.")

try:
    base = os.path.dirname(os.path.abspath(__file__))
except NameError:
    base = os.path.expanduser("~")
p = os.path.join(base, "RESULTS.txt")
open(p, "w", encoding="utf-8").write("\n".join(OUT))
print("\n" + "="*72)
print(f"SAVED TO:  {p}")
print("="*72)
