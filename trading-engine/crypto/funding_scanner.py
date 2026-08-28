#!/usr/bin/env python3
"""
Funding-carry scanner for Binance (global).

Ranks delta-neutral carry opportunities: hold spot, short the matching
USDT-M perpetual, collect funding. Optionally reads your own spot balances
so it only ranks coins you ALREADY hold -- which is the point: the spot
leg exists, so no new capital is needed.

Run it where Binance is reachable (NOT from the cloud research session).

    python3 funding_scanner.py                 # public data, top opportunities
    python3 funding_scanner.py --mine          # only coins you hold (needs keys)
    python3 funding_scanner.py --hold-days 30 --hedge-frac 0.5

Keys (read-only is enough; NEVER enable withdrawal):
    export BINANCE_API_KEY=...
    export BINANCE_API_SECRET=...

NOT financial advice, and NOT tested against the live API from the research
environment -- exchange domains are egress-blocked there. Verify the first
numbers it prints against the Binance UI before trusting any of them.
"""
import argparse, hashlib, hmac, json, os, statistics, time, urllib.parse, urllib.request

FAPI = "https://fapi.binance.com"
SAPI = "https://api.binance.com"

# VIP 0 with BNB fee discount. CHECK THESE against your own account page --
# a wrong fee assumption is exactly what invalidated the earlier analysis.
SPOT_FEE = 0.00075     # 0.10% * 0.75  (BNB discount 25%)
PERP_FEE = 0.00018     # 0.02% maker * 0.90 (BNB discount 10%)

def get(url, params=None, key=None, secret=None):
    params = dict(params or {})
    if secret:
        params["timestamp"] = int(time.time() * 1000)
        params["recvWindow"] = 5000
        q = urllib.parse.urlencode(params)
        params["signature"] = hmac.new(secret.encode(), q.encode(), hashlib.sha256).hexdigest()
    q = urllib.parse.urlencode(params)
    req = urllib.request.Request(f"{url}?{q}" if q else url)
    if key:
        req.add_header("X-MBX-APIKEY", key)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read())

def funding_intervals():
    """symbol -> funding interval in hours. Default 8; some symbols use 4 or 1.
    Annualizing a 4h rate as if it were 8h would DOUBLE the reported APR."""
    out = {}
    try:
        for f in get(f"{FAPI}/fapi/v1/fundingInfo"):
            h = f.get("fundingIntervalHours")
            if h:
                out[f["symbol"]] = float(h)
    except Exception as e:
        print(f"  ! fundingInfo unavailable ({e}); assuming 8h for all symbols")
    return out

def history(symbol, limit=90):
    try:
        rows = get(f"{FAPI}/fapi/v1/fundingRate", {"symbol": symbol, "limit": limit})
        return [float(r["fundingRate"]) for r in rows]
    except Exception:
        return []

def spot_balances(key, secret):
    acct = get(f"{SAPI}/api/v3/account", key=key, secret=secret)
    out = {}
    for b in acct["balances"]:
        total = float(b["free"]) + float(b["locked"])
        if total > 0:
            out[b["asset"]] = total
    return out

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mine", action="store_true", help="only coins you already hold")
    p.add_argument("--hold-days", type=float, default=30.0)
    p.add_argument("--hedge-frac", type=float, default=0.5, help="fraction of the spot position to hedge")
    p.add_argument("--max-leverage", type=float, default=2.0, help="leverage cap on the short leg")
    p.add_argument("--top", type=int, default=15)
    p.add_argument("--min-hist", type=int, default=30, help="min funding periods of history required")
    a = p.parse_args()

    key, secret = os.getenv("BINANCE_API_KEY"), os.getenv("BINANCE_API_SECRET")

    print("Fetching funding rates ...")
    prem = get(f"{FAPI}/fapi/v1/premiumIndex")
    iv = funding_intervals()

    held = None
    if a.mine:
        if not (key and secret):
            raise SystemExit("--mine needs BINANCE_API_KEY / BINANCE_API_SECRET")
        held = spot_balances(key, secret)
        print(f"  spot assets with a balance: {', '.join(sorted(held))}\n")

    rows = []
    for d in prem:
        sym = d["symbol"]
        if not sym.endswith("USDT"):
            continue
        base = sym[:-4]
        if held is not None and base not in held:
            continue
        try:
            rate = float(d["lastFundingRate"]); mark = float(d["markPrice"])
        except (KeyError, ValueError):
            continue
        if mark <= 0:
            continue
        hours = iv.get(sym, 8.0)
        per_year = (24.0 / hours) * 365.0
        apr = rate * per_year

        # a snapshot is not a signal -- require history and score on its stability
        h = history(sym)
        if len(h) < a.min_hist:
            continue
        h_apr = statistics.mean(h) * per_year
        pos_frac = sum(1 for x in h if x > 0) / len(h)

        # fee drag, annualized over the intended holding period
        fee_rt = 2 * (SPOT_FEE + PERP_FEE)
        fee_apr = fee_rt * 365.0 / a.hold_days
        net_apr = h_apr - fee_apr

        rows.append({
            "sym": sym, "base": base, "hours": hours, "spot_now_apr": apr,
            "hist_apr": h_apr, "pos_frac": pos_frac, "net_apr": net_apr,
            "mark": mark, "n": len(h),
            "qty": (held or {}).get(base),
        })
        time.sleep(0.05)   # stay well inside the weight limits

    if not rows:
        raise SystemExit("no symbols passed the filters")

    rows.sort(key=lambda r: r["net_apr"], reverse=True)
    print(f"{'SYMBOL':<14}{'ivl':>4}{'now APR':>10}{'hist APR':>10}{'%pos':>7}"
          f"{'net APR':>10}{'  verdict'}")
    print("-" * 72)
    for r in rows[:a.top]:
        ok = r["net_apr"] > 0 and r["pos_frac"] >= 0.80
        print(f"{r['sym']:<14}{r['hours']:>3.0f}h{100*r['spot_now_apr']:>9.2f}%"
              f"{100*r['hist_apr']:>9.2f}%{100*r['pos_frac']:>6.0f}%"
              f"{100*r['net_apr']:>9.2f}%{'  OK' if ok else '  -- fails stability/net'}")

    if held:
        print("\n" + "=" * 72)
        print(f"HEDGE SIZING for coins you hold  (hedge {100*a.hedge_frac:.0f}%, "
              f"max {a.max_leverage:g}x on the short leg)")
        print("=" * 72)
        for r in rows:
            if not r["qty"]:
                continue
            value = r["qty"] * r["mark"]
            if value < 10:
                continue
            notional = value * a.hedge_frac
            margin = notional / a.max_leverage
            # short liquidates on the way UP; rough distance ignoring maint. margin
            liq_move = 100.0 / a.max_leverage
            exp = notional * r["hist_apr"] * a.hold_days / 365.0
            cost = notional * 2 * (SPOT_FEE + PERP_FEE)
            print(f"\n  {r['base']}: hold {r['qty']:.6g} = ${value:,.2f}")
            print(f"    hedge notional      ${notional:,.2f}")
            print(f"    margin to post      ${margin:,.2f}   (liquidation needs ~+{liq_move:.0f}% move)")
            print(f"    expected funding    ${exp:,.2f} over {a.hold_days:.0f}d")
            print(f"    round-trip fees     ${cost:,.2f}")
            print(f"    NET                 ${exp - cost:,.2f}"
                  f"{'   <-- below cost, do not open' if exp <= cost else ''}")

    print("\nReminders:")
    print("  * Hedging removes upside as well as downside. That is a choice, not a free lunch.")
    print("  * A delta hedge does NOT hedge exchange failure. All of this sits at one venue.")
    print("  * Verify SPOT_FEE / PERP_FEE against your own fee page before trusting the net column.")

if __name__ == "__main__":
    main()
