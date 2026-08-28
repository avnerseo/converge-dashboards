#!/usr/bin/env python3
"""
Funding-carry scanner for Binance (global).

Ranks delta-neutral carry opportunities: hold spot, short the matching
USDT-M perpetual, collect funding. Optionally reads your own spot balances
so it only ranks coins you ALREADY hold -- which is the point: the spot
leg exists, so no new capital is needed.

    python3 funding_scanner.py                 # public data, top opportunities
    python3 funding_scanner.py --mine          # only coins you hold (needs keys)
    python3 funding_scanner.py --hold-days 30 --hedge-frac 0.5

Keys (read-only is enough; NEVER enable withdrawal):
    export BINANCE_API_KEY=...
    export BINANCE_API_SECRET=...

VERIFIED against the live API on 2026-08-28 from a machine Binance is
reachable from. The first version was written blind in an egress-blocked
cloud session; every field name it guessed turned out correct, but the
UNIVERSE it scanned did not. See NOTES-ON-THE-FIX at the bottom.

NOT financial advice. Verify the first numbers against the Binance UI.
"""
import argparse, hashlib, hmac, json, os, statistics, sys, time
import urllib.error, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor

# Binance lists symbols with CJK names -- 币安人生USDT, 我踏马来了USDT, 龙虾USDT are
# real, tradeable, and spot-listed. Printing them killed the script outright on
# a cp1255 (Hebrew Windows) console. Never let a coin name crash the scan.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

FAPI = "https://fapi.binance.com"
SAPI = "https://api.binance.com"

# VIP 0 with BNB fee discount. CHECK THESE against your own account page --
# a wrong fee assumption is exactly what invalidated the earlier analysis.
SPOT_FEE = 0.00075     # 0.10% * 0.75  (BNB discount 25%)
PERP_FEE = 0.00018     # 0.02% maker * 0.90 (BNB discount 10%)

# Binance settles funding on one of these cadences. Measured gaps get snapped
# to the nearest one. Verified live: of 767 symbols carrying a published
# interval, 441 are 4h, 324 are 8h, 2 are 1h.
CADENCES = (1.0, 2.0, 4.0, 8.0)

# Perp symbols that quote a multiple of the underlying (1000PEPEUSDT is priced
# per 1000 PEPE). Longest prefix first.
MULTIPLIER_PREFIXES = (("1000000", 1_000_000.0), ("1000", 1000.0),
                       ("1M", 1_000_000.0), ("1B", 1_000_000_000.0))


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
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


# ---------------------------------------------------------------- universe

def universe():
    """Symbols where this trade can ACTUALLY be put on: a live perpetual with
    a live spot pair to hold against it.

    premiumIndex alone is not that list. Verified live 2026-08-28: it returns
    836 USDT-suffixed symbols, but fapi exchangeInfo says 130 of those are
    SETTLING (delisted -- their last funding print is months old) and 180 are
    TRADIFI_PERPETUAL tokenised equities (AAPLUSDT, ADBEUSDT) with no Binance
    spot leg at all. Scanning premiumIndex ranks contracts you cannot trade,
    on funding you cannot collect.

    Returns ({perp_symbol: (spot_base_asset, units_per_contract_unit)}, skipped).
    """
    perps = get(f"{FAPI}/fapi/v1/exchangeInfo")["symbols"]
    spot = get(f"{SAPI}/api/v3/exchangeInfo")["symbols"]

    spot_bases = {s["baseAsset"] for s in spot
                  if s["status"] == "TRADING" and s["quoteAsset"] == "USDT"
                  and s.get("isSpotTradingAllowed")}

    out, no_spot = {}, []
    for p in perps:
        if (p["status"] != "TRADING" or p.get("contractType") != "PERPETUAL"
                or p["quoteAsset"] != "USDT"):
            continue
        base = p["baseAsset"]
        # Try the raw base FIRST. 1000CAT is genuinely its own spot asset, so
        # blind prefix-stripping would map it to a different coin.
        if base in spot_bases:
            out[p["symbol"]] = (base, 1.0)
            continue
        for pref, mult in MULTIPLIER_PREFIXES:
            if base.startswith(pref) and base[len(pref):] in spot_bases:
                out[p["symbol"]] = (base[len(pref):], mult)
                break
        else:
            no_spot.append(p["symbol"])
    return out, no_spot


# ---------------------------------------------------------------- funding

def published_intervals():
    """symbol -> funding interval hours, as published. Incomplete on purpose:
    verified live, fundingInfo covers 767 of 836 symbols, and among the ones
    it omits are genuine 4h contracts. It is a cross-check, not the source."""
    try:
        return {f["symbol"]: float(f["fundingIntervalHours"])
                for f in get(f"{FAPI}/fapi/v1/fundingInfo")
                if f.get("fundingIntervalHours")}
    except Exception as e:
        print(f"  ! fundingInfo unavailable ({e}); using measured intervals only")
        return {}


def funding_window(symbol, days):
    """Every funding print in the last `days` days: [(ms, rate), ...].

    Windowed by TIME, not by row count. The old version asked for the last 90
    rows, which is 30 days on an 8h symbol but only 15 on a 4h one and under
    4 on a 1h one -- it was silently comparing different lookbacks against a
    single --min-hist threshold."""
    now = int(time.time() * 1000)
    rows = get(f"{FAPI}/fapi/v1/fundingRate",
               {"symbol": symbol, "startTime": now - int(days * 86400_000),
                "endTime": now, "limit": 1000})
    return [(int(r["fundingTime"]), float(r["fundingRate"])) for r in rows]


def current_cadence(times, fallback):
    """The interval IN FORCE NOW, plus the index where that run starts.

    This is the number the whole APR depends on. Getting it wrong scales every
    reported yield by an integer factor: treating a 4h symbol as 8h reports
    HALF the true APR. (The original comment here claimed it would double it
    -- wrong direction: fewer assumed periods per year means a smaller APR.)

    Binance changes a symbol's cadence mid-life. Verified live 2026-08-28:
    DEXEUSDT and ERAUSDT each ran 1h for most of the last 30 days and 4h now.
    A median over the whole window calls them 1h and reports ~4x their real
    yield, off history whose prints are not even the same size. So: read the
    cadence off the RECENT prints, then walk back only as far as it holds.
    Everything older is a different contract, in effect, and is discarded.

    Returns (hours, start_index, changed) -- slice the history at start_index.
    """
    if len(times) < 3:
        return fallback, 0, False
    gaps = [(times[i + 1] - times[i]) / 3600_000 for i in range(len(times) - 1)]
    recent = statistics.median(gaps[-10:])
    hours = min(CADENCES, key=lambda h: abs(h - recent))
    i = len(gaps)
    while i > 0 and abs(gaps[i - 1] - hours) <= 0.2 * hours:
        i -= 1
    return hours, i, i > 0


# ---------------------------------------------------------------- account

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
    p.add_argument("--lookback-days", type=float, default=30.0,
                   help="funding history window used for the ranking")
    p.add_argument("--min-coverage", type=float, default=0.8,
                   help="fraction of the lookback window that must actually be covered")
    p.add_argument("--workers", type=int, default=8)
    a = p.parse_args()

    key, secret = os.getenv("BINANCE_API_KEY"), os.getenv("BINANCE_API_SECRET")

    print("Resolving the tradeable universe ...")
    uni, no_spot = universe()
    prem = {d["symbol"]: d for d in get(f"{FAPI}/fapi/v1/premiumIndex")}
    published = published_intervals()
    print(f"  {len(uni)} live USDT perps with a spot leg "
          f"({len(no_spot)} live perps skipped: no spot pair to hold)")

    held = None
    if a.mine:
        if not (key and secret):
            raise SystemExit("--mine needs BINANCE_API_KEY / BINANCE_API_SECRET")
        held = spot_balances(key, secret)
        uni = {s: v for s, v in uni.items() if v[0] in held}
        print(f"  spot assets with a balance: {', '.join(sorted(held))}")
        print(f"  {len(uni)} of them have a live perp to short")

    syms = sorted(uni)
    print(f"Fetching {a.lookback_days:.0f}d of funding history for {len(syms)} symbols ...")
    t0 = time.time()

    def pull(sym):
        try:
            return sym, funding_window(sym, a.lookback_days), None
        except Exception as e:
            return sym, None, e

    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        fetched = list(pool.map(pull, syms))
    print(f"  done in {time.time() - t0:.1f}s")

    now_ms = int(time.time() * 1000)
    rows, dropped = [], {"error": 0, "thin": 0, "stale": 0, "no_premium": 0}
    mismatches, cadence_changed = [], []

    for sym, hist, err in fetched:
        if err is not None:
            dropped["error"] += 1
            continue
        base, mult = uni[sym]
        d = prem.get(sym)
        if not d:
            dropped["no_premium"] += 1
            continue

        times = [t for t, _ in hist]
        hours, start, changed = current_cadence(times, published.get(sym, 8.0))
        pub = published.get(sym)
        if pub and len(times) >= 3 and abs(pub - hours) > 1e-9:
            mismatches.append((sym, pub, hours))

        # A contract can be listed and still be dead. Require a recent print.
        if not times or (now_ms - times[-1]) > 2.5 * hours * 3600_000:
            dropped["stale"] += 1
            continue

        # Keep only the prints settled at the cadence that is in force now.
        if changed:
            cadence_changed.append((sym, len(hist), len(hist) - start))
            hist = hist[start:]

        # And require the window to be genuinely covered, not one lucky print.
        expected = a.lookback_days * 24.0 / hours
        if len(hist) < a.min_coverage * expected:
            dropped["thin"] += 1
            continue

        try:
            rate = float(d["lastFundingRate"]); mark = float(d["markPrice"])
        except (KeyError, ValueError):
            dropped["no_premium"] += 1
            continue
        if mark <= 0:
            dropped["no_premium"] += 1
            continue

        per_year = (24.0 / hours) * 365.0
        h = [r for _, r in hist]
        h_apr = statistics.mean(h) * per_year
        pos_frac = sum(1 for x in h if x > 0) / len(h)

        # fee drag, annualized over the intended holding period
        fee_rt = 2 * (SPOT_FEE + PERP_FEE)
        fee_apr = fee_rt * 365.0 / a.hold_days

        rows.append({
            "sym": sym, "base": base, "mult": mult, "hours": hours,
            "spot_now_apr": rate * per_year, "hist_apr": h_apr,
            "pos_frac": pos_frac, "net_apr": h_apr - fee_apr,
            "mark": mark, "n": len(h),
            "qty": (held or {}).get(base),
        })

    print(f"  ranked {len(rows)}   dropped: {dropped['stale']} stale (no recent funding print), "
          f"{dropped['thin']} thin history, {dropped['error']} fetch errors, "
          f"{dropped['no_premium']} no mark price")
    if mismatches:
        print(f"  ! {len(mismatches)} symbols where the published interval disagrees with the "
              f"measured one; the measured one is used. e.g. "
              + ", ".join(f"{s} pub {p:g}h/meas {m:g}h" for s, p, m in mismatches[:4]))
    if cadence_changed:
        print(f"  ! {len(cadence_changed)} symbols changed funding cadence inside the window; "
              f"only prints at the current cadence are scored. e.g. "
              + ", ".join(f"{s} {k}/{n} prints kept" for s, n, k in cadence_changed[:4]))
    if not rows:
        raise SystemExit("no symbols passed the filters")

    breakeven = 2 * (SPOT_FEE + PERP_FEE) * 365.0 / a.hold_days
    rows.sort(key=lambda r: r["net_apr"], reverse=True)
    print(f"\nRanked on mean funding over the last {a.lookback_days:.0f}d, "
          f"net of {100*breakeven:.2f}% APR fee drag at a {a.hold_days:.0f}d hold.\n")
    print(f"{'SYMBOL':<16}{'ivl':>4}{'now APR':>10}{'hist APR':>10}{'%pos':>7}"
          f"{'net APR':>10}{'  verdict'}")
    print("-" * 74)
    for r in rows[:a.top]:
        ok = r["net_apr"] > 0 and r["pos_frac"] >= 0.80
        print(f"{r['sym']:<16}{r['hours']:>3.0f}h{100*r['spot_now_apr']:>9.2f}%"
              f"{100*r['hist_apr']:>9.2f}%{100*r['pos_frac']:>6.0f}%"
              f"{100*r['net_apr']:>9.2f}%{'  OK' if ok else '  -- fails stability/net'}")

    if held:
        print("\n" + "=" * 74)
        print(f"HEDGE SIZING for coins you hold  (hedge {100*a.hedge_frac:.0f}%, "
              f"max {a.max_leverage:g}x on the short leg)")
        print("=" * 74)
        for r in rows:
            if not r["qty"]:
                continue
            # mark is quoted per contract unit; 1000PEPEUSDT marks 1000 PEPE.
            value = r["qty"] * r["mark"] / r["mult"]
            if value < 10:
                continue
            notional = value * a.hedge_frac
            margin = notional / a.max_leverage
            # short liquidates on the way UP; rough distance ignoring maint. margin
            liq_move = 100.0 / a.max_leverage
            exp = notional * r["hist_apr"] * a.hold_days / 365.0
            cost = notional * 2 * (SPOT_FEE + PERP_FEE)
            note = f"  ({r['sym']} quotes {r['mult']:,.0f} {r['base']})" if r["mult"] != 1 else ""
            print(f"\n  {r['base']}: hold {r['qty']:.6g} = ${value:,.2f}{note}")
            print(f"    hedge notional      ${notional:,.2f}")
            print(f"    margin to post      ${margin:,.2f}   (liquidation needs ~+{liq_move:.0f}% move)")
            print(f"    expected funding    ${exp:,.2f} over {a.hold_days:.0f}d")
            print(f"    round-trip fees     ${cost:,.2f}")
            print(f"    NET                 ${exp - cost:,.2f}"
                  f"{'   <-- below cost, do not open' if exp <= cost else ''}")

    print("\nReminders:")
    print("  * Hedging removes upside as well as downside. That is a choice, not a free lunch.")
    print("  * A delta hedge does NOT hedge exchange failure. All of this sits at one venue.")
    print("  * Past funding is not future funding. %pos is stability, not a guarantee.")
    print("  * Verify SPOT_FEE / PERP_FEE against your own fee page before trusting the net column.")


if __name__ == "__main__":
    main()

# --------------------------------------------------------------------------
# NOTES-ON-THE-FIX (2026-08-28, first run against the live API)
#
# Correct as guessed: every field name. symbol/markPrice/lastFundingRate on
# premiumIndex, fundingIntervalHours on fundingInfo, fundingRate/fundingTime
# on fundingRate, balances/free/locked on /api/v3/account. Nothing renamed.
#
# Wrong, and only visible against live data:
#
#  1. UNIVERSE -- the one that mattered. Scanned premiumIndex's 836
#     USDT-suffixed symbols. 130 are SETTLING delisted contracts still
#     quoting a months-old lastFundingRate, and 180 are TRADIFI_PERPETUAL
#     tokenised stocks (AAPLUSDT, ADBEUSDT) with no spot leg.
#
#     Consequence, measured by re-running the old logic: NINE of its top
#     TWELVE were dead contracts. It ranked RVVUSDT at 129% net APR with
#     96% positive stability -- last funding print 199 days ago. NEIROETH
#     at 124%, settled 336 days ago. LEVERUSDT at 94%, settled 359 days
#     ago. The scanner would have recommended a carry trade on contracts
#     that no longer exist, and the stability score made them look SAFEST.
#     Exactly the CRYPTO_STATE rule 5 pattern: the number looked great
#     because it was a bug.
#
#     Now: TRADING + PERPETUAL + a live USDT spot pair to hold = 361
#     symbols, plus a staleness filter requiring a print within 2.5
#     intervals. The 163 live perps with no spot pair are skipped by
#     design -- ESPORTSUSDT prints 119% APR and is perfectly live, but
#     Binance lists no ESPORTS spot, so the hedge cannot be built.
#
#  2. INTERVAL. fundingInfo covers 767 of 836 symbols and omits genuine 4h
#     ones (TONUSDT, SKATEUSDT, HIPPOUSDT), which then defaulted to 8h and
#     reported HALF their true APR. Now measured from the print timestamps.
#
#  3. CADENCE CHANGES. Binance moves a symbol between cadences mid-life.
#     DEXEUSDT and ERAUSDT each ran 1h for most of the last 30 days and 4h
#     now; a whole-window median calls them 1h and reports ~4x the real
#     yield off prints that are not even the same size. Now the cadence is
#     read off the recent prints and history is truncated to that run. Six
#     symbols hit this today; all six then failed coverage and were
#     dropped, which is the right answer -- there is no comparable history.
#
#  4. LOOKBACK. limit=90 rows is 30d at 8h but 15d at 4h and 3.75d at 1h,
#     all compared against one --min-hist. Now windowed by startTime.
#
#  5. SIZING. 1000PEPEUSDT marks per 1000 PEPE; hedge value was overstated
#     1000x for the 15 multiplier-prefixed perps. Note 1000CAT is its own
#     spot asset, so the raw base is tried before any prefix is stripped.
#
#  6. ENCODING. Binance lists 币安人生USDT, 我踏马来了USDT and 龙虾USDT --
#     real, spot-listed, and 币安人生USDT ranks in the top 12 today.
#     Printing it raised UnicodeEncodeError on a cp1255 console and killed
#     the run after the table had already started.
#
#  7. SPEED. 836 sequential requests, still unfinished after 18 minutes.
#     Now 361 in parallel: 24s.
# --------------------------------------------------------------------------
