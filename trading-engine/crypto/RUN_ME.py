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
    return sorted(set(rows))

# ---------- grid simulation (verified against known-answer cases) ----------
def simulate(bars, lo, hi, n, capital):
    step=(hi-lo)/n
    levels=[lo+step*i for i in range(n+1)]
    per=capital/n
    held=0; real=0.0; trades=0; out=0
    prev=bars[0][3]
    for (_ts,h,l,c) in bars:
        if c<lo or c>hi: out+=1
        seq=(l,h,c) if abs(l-prev)<abs(h-prev) else (h,l,c)
        for p in seq:
            while p<prev-1e-12:
                b=[L for L in levels if L<prev-1e-12]
                if not b or max(b)<p: break
                if held*per<capital: held+=1
                prev=max(b)
            while p>prev+1e-12:
                a=[L for L in levels if L>prev+1e-12]
                if not a or min(a)>p: break
                lvl=min(a)
                if held>0:
                    held-=1; trades+=1
                    real += per*(step/lvl) - 2*FEE*per
                prev=lvl
            prev=p
    return trades, real, out/len(bars)

# ---------- main ----------
say("="*64)
say("GRID PARAMETER SCAN -- generated " + dt.datetime.now().isoformat(timespec="seconds"))
say("="*64)

for sym in SYMBOLS:
    print(f"\nDownloading {sym} ({MONTHS} months of 1-minute bars)...")
    bars = grab(sym)
    if len(bars) < 10000:
        say(f"\n{sym}: only {len(bars)} bars downloaded -- skipping"); continue
    px = bars[-1][3]; px0 = bars[0][3]
    days = (bars[-1][0]-bars[0][0])/86400000
    say("")
    say(f"### {sym}   {len(bars):,} minute bars, {days:.0f} days")
    say(f"    price {px0:.5f} -> {px:.5f}    BUY-AND-HOLD: {100*(px/px0-1):+.1f}%")
    say("")
    say(f"    {'range':>8}{'grids':>7}{'step':>8}{'$/ord':>7}{'trades':>8}{'profit':>9}{'APR':>8}{'outside':>9}")
    say("    " + "-"*56)
    best=None
    for w in (0.05,0.10,0.15,0.20,0.30,0.40):
        for n in (10,20,40,80,160):
            if CAPITAL/n < MIN_NOTIONAL: continue
            lo,hi = px*(1-w), px*(1+w)
            t,p,out = simulate(bars,lo,hi,n,CAPITAL)
            apr = 100*p/CAPITAL*365/days
            say(f"    {'+-'+str(int(100*w))+'%':>8}{n:>7}{200*w/n:>7.2f}%"
                f"{CAPITAL/n:>7.2f}{t:>8}{p:>9.2f}{apr:>7.1f}%{100*out:>8.0f}%")
            if best is None or apr>best[0]: best=(apr,w,n,200*w/n,t,out)
    if best:
        say("")
        say(f"    BEST: range +-{100*best[1]:.0f}%  ({px*(1-best[1]):.5f} - {px*(1+best[1]):.5f})")
        say(f"          {best[2]} grids, step {best[3]:.2f}%  ->  {best[0]:.1f}% APR")
        say(f"          {best[4]} trades, outside range {100*best[5]:.0f}% of the time")

say("")
say("CAVEAT: assumes every resting order fills at its level with no slippage.")
say("Treat the APR as an upper bound, and compare it to buy-and-hold above.")

p=os.path.join(os.path.dirname(os.path.abspath(__file__)),"RESULTS.txt")
open(p,"w",encoding="utf-8").write("\n".join(OUT))
print(f"\n\nSaved to: {p}")
print("Send that file back.")
input("\nPress Enter to close...")
