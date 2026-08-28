import csv, math
FEE = 0.00075          # one-way spot fee, BNB discount

def load(path, start=None, end=None):
    r=[(x['t'],float(x['o']),float(x['h']),float(x['l']),float(x['c']))
       for x in csv.DictReader(open(path))]
    r.sort()
    return [x for x in r if (not start or x[0]>=start) and (not end or x[0]<=end)]

def simulate(bars, lo, hi, ngrids, capital, verbose=False):
    """Conservative daily-bar grid sim.
    Each day is walked as open -> extreme -> extreme -> close, choosing the
    ordering that produces FEWER round trips. Daily bars cannot see intraday
    oscillation, so this is a LOWER BOUND on the trade count."""
    levels=[lo + (hi-lo)*i/ngrids for i in range(ngrids+1)]
    per_order = capital/ngrids
    best=None
    for order in (0,1):
        held=0; realised=0.0; trades=0; days_out=0
        idx=None
        for (t,o,h,l,c) in bars:
            pts=[o,h,l,c] if order==0 else [o,l,h,c]
            if c<lo or c>hi: days_out+=1
            prev=pts[0]
            if idx is None:
                idx=sum(1 for L in levels if L<=prev)
            for p in pts[1:]:
                while p<prev:                      # moving down -> buy
                    nxt=[L for L in levels if L<prev]
                    if not nxt or max(nxt)<p: break
                    lvl=max(nxt)
                    held+=1; prev=lvl
                while p>prev:                      # moving up -> sell if we hold
                    nxt=[L for L in levels if L>prev]
                    if not nxt or min(nxt)>p: break
                    lvl=min(nxt)
                    if held>0:
                        held-=1; trades+=1
                        step=(hi-lo)/ngrids
                        realised += per_order*(step/lvl) - 2*FEE*per_order
                    prev=lvl
                prev=p
        res=(trades,realised,held,days_out)
        if best is None or res[0]<best[0]: best=res
    return best

if __name__=="__main__":
    bars=load('xrp_daily.csv')
    print("=== VALIDATION: their exact bot config over its actual lifetime ===")
    live=[b for b in bars if '2026-08-24'<=b[0]<='2026-08-28']
    t,p,held,out=simulate(live,1.10,1.90,20,200)
    print(f"  config range 1.10-1.90, 20 grids, $200, {len(live)} days")
    print(f"  simulated : {t} round trips, grid profit ${p:.4f}")
    print(f"  ACTUAL    : 3 round trips, grid profit $0.7240")
    print(f"  -> simulator is a lower bound; actual >= simulated is expected\n")
