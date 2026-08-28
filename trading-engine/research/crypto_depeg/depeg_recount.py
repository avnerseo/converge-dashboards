import csv, datetime as dt, statistics as stt, collections

ENTRY=0.9992      # amended: derived from 0.04% round trip x2 = 0.08% gross
PAR   =1.0000     # exit at par
COST  =0.0004     # 0.02% taker x2, conservative
MAXH  =30         # days to repeg

def load(p):
    r=[(dt.date.fromisoformat(x['timestamp']), float(x['close'])) for x in csv.DictReader(open(p))]
    return sorted(r)

def episodes(rows):
    eps=[]; i=0; n=len(rows)
    while i<n:
        if rows[i][1]<=ENTRY:
            ent_d,ent_p=rows[i]
            j=i+1; out=None
            while j<n and (rows[j][0]-ent_d).days<=MAXH:
                if rows[j][1]>=PAR: out=rows[j]; break
                j+=1
            if out:
                eps.append((ent_d,ent_p,out[0],(out[0]-ent_d).days, PAR/ent_p-1-COST, True))
                # next episode only after the repeg
                i=rows.index(out)+1
            else:
                # unresolved within MAXH -> counted as failure at the pre-set rule
                eps.append((ent_d,ent_p,None,None, None, False))
                i=j if j>i else i+1
        else:
            i+=1
    return eps

def report(name, path):
    rows=load(path); eps=episodes(rows)
    yrs=(rows[-1][0]-rows[0][0]).days/365.25
    ok=[e for e in eps if e[5]]
    print(f"\n=== {name} ===  {rows[0][0]} .. {rows[-1][0]}  ({yrs:.2f} yrs, {len(rows)} bars)")
    print(f"  min close: {min(c for _,c in rows):.5f}")
    print(f"  episodes (entry close <= {ENTRY}): {len(eps)}   = {len(eps)/yrs:.1f}/yr")
    if not eps: return
    print(f"  repegged to par within {MAXH}d: {len(ok)}/{len(eps)} = {100*len(ok)/len(eps):.1f}%   [gate: >90%]")
    if ok:
        pr=[e[4] for e in ok]
        print(f"  net profit/episode: median {100*stt.median(pr):.4f}%   mean {100*stt.mean(pr):.4f}%   [gate: median>0]")
        print(f"  days to repeg: median {stt.median([e[3] for e in ok])}")
        tot=sum(pr)
        print(f"  sum of net profit over period: {100*tot:.3f}%  ->  {100*tot/yrs:.3f}%/yr if fully deployed each time")
    byyr=collections.Counter(e[0].year for e in eps)
    print("  by year:", dict(sorted(byyr.items())))
    last=rows[-1][0]; lo=last-dt.timedelta(365)
    t12=[e for e in eps if e[0]>=lo]
    print(f"  TRAILING 12M ({lo}..{last}): {len(t12)} episodes   [gate: >=8]")

report("USDT/USD","usdt_daily.csv")
report("DAI/USD","dai_daily.csv")
