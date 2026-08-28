#!/usr/bin/env python3
"""
Grid parameter optimiser on 1-minute bars.

The daily-bar simulator could not answer the step-size question: it
over-counted trades 2.5x against the live bot and was structurally biased
toward wide grids, because daily bars cannot see intraday oscillation.
Minute bars fix that.

    python3 fetch_klines.py XRPUSDT --months 18
    python3 grid_optimize.py xrpusdt_1m.csv --capital 200

Reports, for each candidate configuration: realised grid profit, trade
count, time spent outside the range, and -- critically -- the same
period's buy-and-hold return, because a grid that loses to holding is
not worth running.
"""
import argparse, csv, datetime as dt, statistics as st

FEE = 0.00075          # one-way spot fee, VIP0 with BNB discount. VERIFY.
MIN_NOTIONAL = 5.0     # Binance spot MIN_NOTIONAL filter. VERIFY per symbol.

def load(path):
    r=[]
    for x in csv.DictReader(open(path)):
        r.append((x["t"], float(x["o"]), float(x["h"]), float(x["l"]), float(x["c"])))
    r.sort()
    return r

def simulate(bars, lo, hi, n, capital):
    """Resting limit orders fill on wicks, so crossings use high/low.
    Within each minute the extreme ordering is chosen to minimise trades."""
    step_abs=(hi-lo)/n
    levels=[lo+step_abs*i for i in range(n+1)]
    per=capital/n
    held=0; realised=0.0; trades=0; out=0; maxheld=0
    prev=bars[0][4]
    for (_t,o,h,l,c) in bars:
        if c<lo or c>hi: out+=1
        for p in (l,h,c) if abs(l-prev)<abs(h-prev) else (h,l,c):
            while p<prev-1e-12:
                below=[L for L in levels if L<prev-1e-12]
                if not below or max(below)<p: break
                lvl=max(below)
                if held*per < capital:            # capital cap
                    held+=1; maxheld=max(maxheld,held)
                prev=lvl
            while p>prev+1e-12:
                above=[L for L in levels if L>prev+1e-12]
                if not above or min(above)>p: break
                lvl=min(above)
                if held>0:
                    held-=1; trades+=1
                    realised += per*(step_abs/lvl) - 2*FEE*per
                prev=lvl
            prev=p
    return trades, realised, out/len(bars), maxheld*per

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("csv"); ap.add_argument("--capital", type=float, default=200.0)
    a=ap.parse_args()
    bars=load(a.csv)
    px=bars[-1][4]; px0=bars[0][4]
    days=(dt.datetime.fromisoformat(bars[-1][0])-dt.datetime.fromisoformat(bars[0][0])).total_seconds()/86400
    hold=100*(px/px0-1)
    print(f"{a.csv}: {len(bars):,} minute bars, {days:.0f} days")
    print(f"price {px0:.5f} -> {px:.5f}   BUY-AND-HOLD over the period: {hold:+.1f}%\n")

    print(f"{'range':>10}{'grids':>7}{'step':>8}{'$/ord':>8}{'trades':>8}"
          f"{'profit':>9}{'APR':>8}{'out':>7}{'deployed':>10}")
    print("-"*76)
    best=[]
    for w in (0.05,0.10,0.15,0.20,0.30,0.40):
        for n in (10,20,40,80,160):
            lo, hi = px*(1-w), px*(1+w)
            per=a.capital/n
            if per < MIN_NOTIONAL:
                continue
            t,p,out,dep=simulate(bars,lo,hi,n,a.capital)
            apr=100*p/a.capital*365/days
            step=100*(hi-lo)/n/px
            print(f"{'+-'+str(int(100*w))+'%':>10}{n:>7}{step:>7.2f}%{per:>8.2f}"
                  f"{t:>8}{p:>9.2f}{apr:>7.1f}%{100*out:>6.0f}%{dep:>10.2f}")
            best.append((apr,w,n,step,t,out))
    if best:
        best.sort(reverse=True)
        apr,w,n,step,t,out=best[0]
        print(f"\nBEST: range +-{100*w:.0f}%, {n} grids, step {step:.2f}%  ->  {apr:.1f}% APR")
        print(f"      {t} trades, outside the range {100*out:.0f}% of the time")
        print(f"\nCompare against buy-and-hold {hold:+.1f}% over the same {days:.0f} days.")
        print("A grid that loses to holding is not worth running.")
        print("\nCAVEAT: this assumes every resting order fills at its level with no")
        print("slippage or queue position. Treat the APR as an upper bound.")

if __name__=="__main__":
    main()
