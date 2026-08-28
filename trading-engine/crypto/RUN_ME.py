#!/usr/bin/env python3
"""
One file, one command. Downloads Binance 1-minute history and finds the best
grid settings from it.

    python RUN_ME.py

Writes RESULTS.txt next to itself -- send that file back.
Needs nothing but Python. No API key, no account, read-only public data.
"""
import csv, datetime as dt, io, json, os, sys, time, urllib.request, warnings, zipfile
warnings.filterwarnings('ignore')

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
    """Per-level slots, with the initial inventory a real grid bot buys.

    Binance seeds a spot grid by market-buying the lots needed to back the
    sell orders above the current price. Without that seed the model shows
    zero profit in any rising market, which is wrong.

    basis[j] = price paid for the lot occupying slot j (None = empty).
    Slot j is bought at levels[j] and sold at levels[j+1].
    """
    step=(hi-lo)/n
    levels=[lo+step*i for i in range(n+1)]
    q=capital/n
    basis=[None]*n
    realised=0.0; trades=0; out=0

    def idx(p):
        if p<=lo: return 0
        if p>=hi: return n
        return min(n, max(0, int((p-lo)/step)))

    p0=bars[0][3]
    for j in range(n):                     # seed: slots at or above spot
        if levels[j] >= p0:
            basis[j]=p0
            realised -= q*FEE
    cur=idx(p0)

    for (_ts,h,l,c) in bars:
        if c<lo or c>hi: out+=1
        for p in ((l,h,c) if abs(l-p0)<abs(h-p0) else (h,l,c)):
            tgt=idx(p)
            while cur>tgt:                 # crossing levels[cur] downward -> buy
                j=cur
                if j<n and basis[j] is None:
                    basis[j]=levels[j]; realised -= q*FEE
                cur-=1
            while cur<tgt:                 # crossing levels[cur+1] upward -> sell
                j=cur
                if j<n and basis[j] is not None:
                    proceeds=q*(levels[j+1]/basis[j])
                    realised += (proceeds-q) - proceeds*FEE
                    basis[j]=None; trades+=1
                cur+=1
    final=bars[-1][3]
    unreal=sum(q*(final/b-1) for b in basis if b is not None)
    filled=sum(1 for b in basis if b is not None)
    return trades, realised, unreal, realised+unreal, filled*q, out/len(bars)


def walk_forward(bars, w, n, capital, window_days=30, step_days=7):
    """No look-ahead. Each window sets its range from the price at the START
    of that window -- the only thing you could know when you press Create."""
    W=int(window_days*1440); S=int(step_days*1440)
    res=[]
    i=0
    while i+W <= len(bars):
        seg=bars[i:i+W]
        px0=seg[0][3]
        t,r,u,tot,_st,out = simulate(seg, px0*(1-w), px0*(1+w), n, capital)
        bh = 100*(seg[-1][3]/px0 - 1)
        res.append((100*tot/capital, bh, t, out))
        i+=S
    return res
# ---------- main ----------
import statistics as stt
say("="*78)
say("GRID SCAN v4 -- WALK-FORWARD, no look-ahead  " + dt.datetime.now().isoformat(timespec="seconds"))
say("Each 30-day window sets its range from the price at the START of that window.")
say("="*78)

for sym in SYMBOLS:
    print(f"\nDownloading {sym} ({MONTHS} months of 1-minute bars)...")
    bars = grab(sym)
    if len(bars) < 100000:
        say(f"\n{sym}: only {len(bars)} bars -- skipping"); continue
    days=(bars[-1][0]-bars[0][0])/86400000
    say("")
    say(f"### {sym}   {len(bars):,} bars, {days:.0f} days, "
        f"price {bars[0][3]:.5f} -> {bars[-1][3]:.5f}")
    say("")
    say(f"    {'range':>7}{'grids':>6}{'step':>7}{'wins':>6}{'med bot':>9}{'med hold':>10}"
        f"{'beat hold':>11}{'worst':>9}{'med trades':>11}")
    say("    "+"-"*76)
    rows=[]
    for w in (0.05,0.10,0.15,0.20,0.30):
        for n in (10,20,40):
            if CAPITAL/n < MIN_NOTIONAL: continue
            r=walk_forward(bars,w,n,CAPITAL)
            if len(r)<8: continue
            bot=[x[0] for x in r]; hold=[x[1] for x in r]
            beat=100*sum(1 for x in r if x[0]>x[1])/len(r)
            say(f"    {'+-'+str(int(100*w))+'%':>7}{n:>6}{200*w/n:>6.2f}%{len(r):>6}"
                f"{stt.median(bot):>8.2f}%{stt.median(hold):>9.2f}%{beat:>10.0f}%"
                f"{min(bot):>8.1f}%{stt.median([x[2] for x in r]):>11.0f}")
            rows.append((stt.median(bot)-stt.median(hold), beat, w, n, stt.median(bot),
                         stt.median(hold), min(bot)))
    if rows:
        rows.sort(reverse=True)
        d,beat,w,n,mb,mh,worst=rows[0]
        say("")
        say(f"    BEST vs HOLD: range +-{100*w:.0f}%, {n} grids, step {200*w/n:.2f}%")
        say(f"      median 30-day window: bot {mb:+.2f}%  vs hold {mh:+.2f}%  ->  {d:+.2f}pp")
        say(f"      beat hold in {beat:.0f}% of windows.  worst window {worst:.1f}%")
        if d<=0:
            say(f"      *** NO CONFIG BEATS HOLDING. do not run a grid on this coin. ***")

say("")
say("How to read this:")
say("  wins       = number of 30-day windows tested (overlapping, stepped 7 days)")
say("  med bot    = median total return of the grid over a window, INCLUDING")
say("               unsold inventory marked to market")
say("  med hold   = median return of simply holding the coin over the same window")
say("  beat hold  = share of windows where the grid did better than holding")
say("  worst      = worst single window for the grid")
say("")
say("The range is set from the price at the START of each window, so this is")
say("what you could actually have done -- no hindsight in the range choice.")
say("")
say("STILL OPTIMISTIC: assumes every resting order fills at its level with no")
say("slippage or queue position.")

try:
    base = os.path.dirname(os.path.abspath(__file__))
except NameError:
    base = os.path.expanduser("~")
p = os.path.join(base, "RESULTS.txt")
open(p, "w", encoding="utf-8").write("\n".join(OUT))
print("\n" + "="*78)
print(f"SAVED TO:  {p}")
print("="*78)
