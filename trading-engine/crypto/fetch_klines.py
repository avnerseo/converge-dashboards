#!/usr/bin/env python3
"""
Download Binance 1-minute klines. Run where Binance is reachable
(NOT the cloud research session -- exchange domains are egress-blocked there).

Two sources, tried in order:
  1. data.binance.vision  -- free monthly ZIP dumps, no key, fastest
  2. api.binance.com/api/v3/klines -- REST, paginated, no key, fills the
     current partial month that the dumps do not cover yet

    python3 fetch_klines.py XRPUSDT --months 18
    python3 fetch_klines.py TRXUSDT --months 18 --out trx_1m.csv

Output: CSV  t,o,h,l,c,v  with t = ISO-8601 UTC minute.

Untested against the live endpoints from the research environment.
Check the first and last rows against the Binance chart before relying on it.
"""
import argparse, csv, datetime as dt, io, os, sys, time, urllib.request, zipfile

VISION = "https://data.binance.vision/data/spot/monthly/klines/{s}/1m/{s}-1m-{ym}.zip"
REST   = "https://api.binance.com/api/v3/klines"

def month_list(n):
    today = dt.date.today().replace(day=1)
    out=[]
    for i in range(n, 0, -1):
        y, m = today.year, today.month - i
        while m <= 0: m += 12; y -= 1
        out.append(f"{y:04d}-{m:02d}")
    return out

def from_vision(sym, ym):
    url = VISION.format(s=sym.upper(), ym=ym)
    try:
        with urllib.request.urlopen(url, timeout=90) as r:
            blob = r.read()
    except Exception as e:
        print(f"    {ym}: vision miss ({getattr(e,'code',e)})")
        return []
    rows=[]
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        with z.open(z.namelist()[0]) as f:
            for line in io.TextIOWrapper(f, "utf-8"):
                p = line.split(",")
                if not p or not p[0].strip().rstrip('-').isdigit():
                    continue                      # skip a header row if present
                ts = int(p[0])
                if ts > 1e12 * 10: ts //= 1000    # some dumps are microseconds
                rows.append((ts, p[1], p[2], p[3], p[4], p[5]))
    print(f"    {ym}: {len(rows):,} bars")
    return rows

def from_rest(sym, start_ms):
    """Fill from start_ms to now, 1000 bars per call."""
    out=[]; cur=start_ms
    now=int(time.time()*1000)
    while cur < now:
        url=f"{REST}?symbol={sym.upper()}&interval=1m&startTime={cur}&limit=1000"
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                data=__import__("json").loads(r.read())
        except Exception as e:
            print(f"    rest stopped: {e}"); break
        if not data: break
        for k in data:
            out.append((int(k[0]), k[1], k[2], k[3], k[4], k[5]))
        cur = int(data[-1][0]) + 60_000
        time.sleep(0.25)                          # stay inside the weight limit
    print(f"    rest: {len(out):,} bars")
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("symbol")
    ap.add_argument("--months", type=int, default=12)
    ap.add_argument("--out", default=None)
    a=ap.parse_args()
    out = a.out or f"{a.symbol.lower()}_1m.csv"

    print(f"Downloading {a.symbol} 1m klines, {a.months} months")
    rows=[]
    for ym in month_list(a.months):
        rows += from_vision(a.symbol, ym)
        time.sleep(0.2)
    if rows:
        rows += from_rest(a.symbol, max(r[0] for r in rows)+60_000)
    else:
        print("  vision gave nothing; falling back to REST for 30 days")
        rows = from_rest(a.symbol, int((time.time()-30*86400)*1000))

    rows = sorted(set(rows))
    if not rows:
        sys.exit("no data downloaded -- check the symbol and your connection")
    with open(out,"w",newline="") as f:
        w=csv.writer(f); w.writerow(["t","o","h","l","c","v"])
        for ts,o,h,l,c,v in rows:
            w.writerow([dt.datetime.utcfromtimestamp(ts/1000).isoformat(),o,h,l,c,v])
    span=(rows[-1][0]-rows[0][0])/86400000
    print(f"\nwrote {out}: {len(rows):,} minute bars over {span:.0f} days")
    print(f"  first {dt.datetime.utcfromtimestamp(rows[0][0]/1000)}")
    print(f"  last  {dt.datetime.utcfromtimestamp(rows[-1][0]/1000)}")
    print("\nSanity-check these two timestamps and the last close against the app.")

if __name__=="__main__":
    main()
