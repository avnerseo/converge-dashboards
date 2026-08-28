import csv, datetime as dt, random, statistics as st

START='2016-01-01'   # matches CRYPTO_WEEKEND_RESULT's window; excludes pre-2016 microcap era

def easter(y):
    a=y%19; b=y//100; c=y%100; d=b//4; e=b%4; f=(b+8)//25; g=(b-f+1)//3
    h=(19*a+b-d-g+15)%30; i=c//4; k=c%4; l=(32+2*e+2*i-h-k)%7
    m=(a+11*h+22*l)//451; mo=(h+l-7*m+114)//31; da=((h+l-7*m+114)%31)+1
    return dt.date(y,mo,da)

def nth_wd(y,m,wd,n):           # n-th weekday (0=Mon) of month
    d=dt.date(y,m,1)
    d+=dt.timedelta((wd-d.weekday())%7)
    return d+dt.timedelta(7*(n-1))

def last_wd(y,m,wd):
    d=dt.date(y,m+1,1)-dt.timedelta(1) if m<12 else dt.date(y,12,31)
    return d-dt.timedelta((d.weekday()-wd)%7)

def observed(d):                # Sat -> Fri before, Sun -> Mon after
    if d.weekday()==5: return d-dt.timedelta(1)
    if d.weekday()==6: return d+dt.timedelta(1)
    return d

def nyse(y):
    """(full_closures, half_days) for year y."""
    full=set(); half=set()
    n=dt.date(y,1,1)
    if n.weekday()!=5: full.add(observed(n))          # Jan 1 on Sat is NOT observed
    full.add(nth_wd(y,1,0,3))                          # MLK
    full.add(nth_wd(y,2,0,3))                          # Presidents
    full.add(easter(y)-dt.timedelta(2))                # Good Friday
    full.add(last_wd(y,5,0))                           # Memorial
    if y>=2022: full.add(observed(dt.date(y,6,19)))    # Juneteenth
    full.add(observed(dt.date(y,7,4)))                 # Independence
    full.add(nth_wd(y,9,0,1))                          # Labor
    tg=nth_wd(y,11,3,4); full.add(tg)                  # Thanksgiving
    full.add(observed(dt.date(y,12,25)))               # Christmas
    half.add(tg+dt.timedelta(1))                       # day after Thanksgiving
    j4=dt.date(y,7,4)
    if j4.weekday() not in (5,6): half.add(j4-dt.timedelta(1))   # Jul 3
    x=dt.date(y,12,24)
    if x.weekday()<5: half.add(x)                                # Christmas Eve
    return full, half

FULL=set(); HALF=set()
for y in range(2016,2027):
    f,h=nyse(y); FULL|=f; HALF|=h
FULL |= {dt.date(2018,12,5), dt.date(2025,1,9)}   # ad-hoc closures: Bush, Carter funerals
FULL = {d for d in FULL if d.weekday()<5}          # weekday closures only
HALF -= FULL

def load(p):
    rows=[]
    for r in csv.DictReader(open(p)):
        if r['timestamp']>=START:
            rows.append((dt.date.fromisoformat(r['timestamp']), float(r['close'])))
    rows.sort()
    return [(rows[i][0], rows[i][1]/rows[i-1][1]-1) for i in range(1,len(rows))]

def run(name, path):
    rets=load(path)
    hol=[r for d,r in rets if d in FULL]
    strict=[r for d,r in rets if d in FULL and d.weekday() in (1,2,3)]
    ctrl=[r for d,r in rets if d.weekday()<5 and d not in FULL and d not in HALF]
    wknd=[r for d,r in rets if d.weekday()>=5]
    print(f"\n=== {name} ===  {rets[0][0]} .. {rets[-1][0]}   n={len(rets)}")
    print(f"  weekend        n={len(wknd):5d}  sd={st.stdev(wknd)*100:.3f}%  mean|r|={sum(map(abs,wknd))/len(wknd)*100:.3f}%")
    print(f"  ordinary wkday n={len(ctrl):5d}  sd={st.stdev(ctrl)*100:.3f}%  mean|r|={sum(map(abs,ctrl))/len(ctrl)*100:.3f}%")

    for lbl, grp in (("PRIMARY  (all weekday closures)", hol), ("STRICT   (Tue/Wed/Thu only)", strict)):
        sd=st.stdev(grp); ratio=sd/st.stdev(ctrl)
        random.seed(7)
        null=[]
        for _ in range(2000):
            null.append(st.stdev(random.sample(ctrl,len(grp)))/st.stdev(ctrl))
        pct=100*sum(1 for x in null if x<=ratio)/len(null)
        mid=len(rets)//2; cut=rets[mid][0]
        h1=[r for d,r in rets if d in FULL and d<cut and (lbl.startswith("STRICT")<=0 or d.weekday() in (1,2,3))]
        def half(sel, lo, hi):
            g=[r for d,r in rets if d in FULL and lo<=d<hi and (d.weekday() in (1,2,3) if lbl.startswith("STRICT") else True)]
            c=[r for d,r in rets if d.weekday()<5 and d not in FULL and d not in HALF and lo<=d<hi]
            return st.stdev(g)/st.stdev(c), len(g)
        r1,n1=half(None, rets[0][0], cut); r2,n2=half(None, cut, dt.date(2099,1,1))
        print(f"  {lbl}: n={len(grp):3d}  sd={sd*100:.3f}%  ratio={ratio:.3f}  "
              f"placebo pct={pct:.1f}  halves: {r1:.3f}(n={n1}) / {r2:.3f}(n={n2})")

run("BTC/USD","btc_daily.csv")
run("ETH/USD","eth_daily.csv")

print("\n\n===== POWER: what ratio would have been needed to clear the 5th percentile? =====")
import bisect
for name,path in (("BTC","btc_daily.csv"),("ETH","eth_daily.csv")):
    rets=load(path)
    ctrl=[r for d,r in rets if d.weekday()<5 and d not in FULL and d not in HALF]
    for lbl,n,obs in (("PRIMARY n=101",101,None),("STRICT  n=27",27,None)):
        random.seed(7)
        null=sorted(st.stdev(random.sample(ctrl,n))/st.stdev(ctrl) for _ in range(2000))
        p5=null[int(.05*len(null))]
        print(f"  {name} {lbl}: 5th-pctile of null = {p5:.3f}  "
              f"(i.e. holiday sd would have to be <= {p5*st.stdev(ctrl)*100:.3f}%)")
