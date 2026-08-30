#!/usr/bin/env python3
"""
The daily close store.

Scoring needs a close series that can be re-checked, not a quote fetched once at
publish time and never seen again. The 2026-08-29 run — 0 of 18 quote calls
succeeded, so the previous day's picks were republished unchanged — is what
happens without one.

Three properties this store exists to have:

  * Append-only. A (symbol, date) close is written once. If the provider later
    returns a different value for a date already stored, the new value does NOT
    overwrite it: the disagreement is appended to revisions.jsonl and the
    original stands. A store that silently accepts restatements cannot support
    a track record, because last month's numbers stop being last month's.

  * Total return, not price return. Alpha Vantage's adjusted endpoint is
    premium on this key, but DIVIDENDS and SPLITS are not, so the adjustment is
    reconstructed from raw closes plus the event series rather than bought.
    A dividend payer scored on price return alone looks worse than it was.

  * Resumable. The free key allows ~25 calls/day against a 39-symbol universe,
    so a full refresh does not fit in one day and is not supposed to. Every
    fetch is logged, the manifest says what each symbol has, and `--plan` names
    what to fetch next in priority order. Benchmarks come first: without SPY and
    the sector ETF, no position can be scored at all.

Network access lives in the MCP tool, not in this file, so fetching is a two-step:
call TIME_SERIES_DAILY / DIVIDENDS / SPLITS, then pipe the CSV in here.

  python3 store.py ingest --symbol SPY --kind daily   < spy.csv
  python3 store.py plan                  what to fetch next, in order
  python3 store.py status                coverage per symbol
  python3 store.py close SPY 2026-08-28  one close, for spot-checking
  python3 store.py audit                 published card price vs the real close

ingest trims to the window in prices/window.json. That boundary is a floor the
store guarantees, not a ceiling it enforces: the provider keeps 20+ years, and
this keeps the span the picks live in so a hundred rows of irrelevant history do
not have to be moved by hand for every one of 39 symbols. It is a stated choice,
not an accident of what happened to be fetched, and widening it is a re-fetch
with a lower --since, which the append-only merge absorbs without disturbing
anything already stored.
"""
import json, os, sys, csv, io, argparse
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
STORE = os.path.join(HERE, "prices")
DAILY = os.path.join(STORE, "daily")
EVENTS = os.path.join(STORE, "events")
LEDGER = os.path.join(HERE, "tier1_ledger.jsonl")
MAP = os.path.join(STORE, "benchmarks.json")
WINDOW = os.path.join(STORE, "window.json")


def since():
    with open(WINDOW) as f:
        return json.load(f)["since"]

KINDS = ("daily", "dividends", "splits")


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _log(path, obj):
    os.makedirs(STORE, exist_ok=True)
    with open(os.path.join(STORE, path), "a") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def universe():
    """Symbols to cover: every position, plus SPY and the sector ETFs in use.

    Sector -> ETF comes from benchmarks.json, a file that is meant to be read
    and argued with. The dashboard's own sector label decides the benchmark, so
    a pick is measured against the sector it was published under.
    """
    with open(MAP) as f:
        m = json.load(f)
    rows = [json.loads(l) for l in open(LEDGER) if l.strip()]
    tickers, sectors = {}, set()
    for r in sorted(rows, key=lambda r: r["date"]):
        tickers.setdefault(r["ticker"], r["date"])
        if r.get("sector"):
            sectors.add(r["sector"])
    etfs = {m["market"]}
    for s in sectors:
        e = m["sectors"].get(s)
        if e:
            etfs.add(e)
    return tickers, sorted(etfs), m


def api_symbol(t, m):
    return m["symbol_overrides"].get(t, t)


def _path(kind, symbol):
    d = DAILY if kind == "daily" else EVENTS
    suffix = {"daily": ".csv", "dividends": ".divs.csv", "splits": ".splits.csv"}[kind]
    return os.path.join(d, symbol + suffix)


def read_series(kind, symbol):
    p = _path(kind, symbol)
    if not os.path.exists(p):
        return {}
    with open(p) as f:
        return {r["date"]: r for r in csv.DictReader(f)}


def write_series(kind, symbol, rows):
    p = _path(kind, symbol)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    cols = {"daily": ["date", "open", "high", "low", "close", "volume", "first_seen"],
            "dividends": ["date", "amount", "first_seen"],
            "splits": ["date", "factor", "first_seen"]}[kind]
    with open(p, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for d in sorted(rows):
            w.writerow({c: rows[d].get(c, "") for c in cols})


def parse(kind, text):
    """Provider CSV -> {date: row}. Unknown columns are dropped, not guessed."""
    out = {}
    rd = csv.DictReader(io.StringIO(text.strip().replace("\r\n", "\n")))
    for r in rd:
        if kind == "daily":
            d = r.get("timestamp") or r.get("date")
            if not d:
                continue
            out[d] = {"date": d, "open": r["open"], "high": r["high"],
                      "low": r["low"], "close": r["close"], "volume": r["volume"]}
        elif kind == "dividends":
            d = r.get("ex_dividend_date")
            if not d or d == "None":
                continue
            out[d] = {"date": d, "amount": r["amount"]}
        else:
            d = r.get("effective_date") or r.get("ex_date") or r.get("date")
            if not d or d == "None":
                continue
            out[d] = {"date": d, "factor": r.get("split_factor") or r.get("factor")}
    return out


def ingest(kind, symbol, text, cutoff=None):
    have = read_series(kind, symbol)
    incoming = {d: r for d, r in parse(kind, text).items()
                if not cutoff or d >= cutoff}
    added, revisions = 0, []
    for d, row in incoming.items():
        if d not in have:
            row["first_seen"] = _now()
            have[d] = row
            added += 1
            continue
        # Already stored. Compare on the fields that carry meaning; a
        # disagreement is recorded and the original value is kept.
        keys = {"daily": ("close",), "dividends": ("amount",), "splits": ("factor",)}[kind]
        for k in keys:
            old, new = str(have[d].get(k, "")), str(row.get(k, ""))
            if old and new and old != new:
                revisions.append({"ts": _now(), "symbol": symbol, "kind": kind,
                                  "date": d, "field": k, "stored": old,
                                  "provider_now": new})
    write_series(kind, symbol, have)
    for r in revisions:
        _log("revisions.jsonl", r)
    _log("fetch_log.jsonl", {"ts": _now(), "symbol": symbol, "kind": kind,
                             "since": cutoff,
                             "rows_in": len(incoming), "rows_added": added,
                             "revisions": len(revisions), "total_rows": len(have)})
    return added, len(incoming), revisions


def manifest():
    tickers, etfs, m = universe()
    out = {}
    for s in list(tickers) + etfs:
        api = api_symbol(s, m)
        e = {"api_symbol": api, "role": "position" if s in tickers else "benchmark"}
        if s in tickers:
            e["first_pick"] = tickers[s]
        for k in KINDS:
            ser = read_series(k, api)
            e[k] = {"rows": len(ser), "latest": max(ser) if ser else None}
        out[s] = e
    return out


def plan(limit):
    """What to fetch next. Benchmarks before positions: a position with no
    benchmark series cannot be scored, so fetching it first buys nothing."""
    man = manifest()
    todo = []
    for kind, weight in (("daily", 0), ("dividends", 1), ("splits", 2)):
        for sym, e in man.items():
            if e[kind]["rows"] == 0:
                todo.append((weight, 0 if e["role"] == "benchmark" else 1,
                             e.get("first_pick", ""), sym, e["api_symbol"], kind))
    todo.sort()
    return todo[:limit]


def audit():
    """Compare the price printed on each tier-1 card against the actual close.

    The dashboard prints a live quote at publish time, and it is not the close
    of the day the pick was made — it is the previous trading day's close, and
    on some runs staler than that. Scoring off the card price would therefore
    enter every position at a price the pick was never made at. Entry comes
    from this store, dated to the publication date; the card price is kept in
    the ledger as what was published, not as what was paid.
    """
    rows = [json.loads(l) for l in open(LEDGER) if l.strip()]
    _, _, m = universe()
    out, lags, unmatched = [], {}, []
    for r in sorted(rows, key=lambda r: (r["date"], r["ticker"])):
        if r["price"] is None:
            continue
        s = read_series("daily", api_symbol(r["ticker"], m))
        if not s:
            continue
        days = sorted(s)
        hit = [d for d in days if abs(float(s[d]["close"]) - r["price"]) < 0.005]
        same = s.get(r["date"], {}).get("close")
        if hit:
            src = hit[-1]
            lag = days.index(r["date"]) - days.index(src) if r["date"] in s else None
            if lag is not None:
                lags.setdefault(lag, []).append(r["ticker"])
        else:
            src = "not in window"
            unmatched.append((r["date"], r["ticker"], r["price"]))
        out.append((r["date"], r["ticker"], r["price"],
                    float(same) if same else None, src))

    print(f"{'pick date':<11} {'ticker':<6} {'card':>10} {'close that day':>15}  "
          f"{'card price is the close of'}")
    print("-" * 78)
    for d, t, card, same, src in out:
        print(f"{d:<11} {t:<6} {card:>10.2f} "
              f"{(f'{same:.2f}' if same else 'no close'):>15}  {src}")
    print("\nlag between the published price and the pick date, in trading days:")
    for k in sorted(lags):
        print(f"  {k}: {len(lags[k])} row(s)  ({' '.join(sorted(set(lags[k])))})")
    if unmatched:
        print(f"\n{len(unmatched)} row(s) whose card price matches no close in the "
              f"stored window — a staler quote than the window reaches:")
        for d, t, c in unmatched:
            print(f"  {d} {t} {c}")
    print("\nNo row's card price equals the close of the day it was published. "
          "Entry price must come from this store, not from the card.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("ingest"); i.add_argument("--symbol", required=True)
    i.add_argument("--kind", required=True, choices=KINDS)
    i.add_argument("--since", default=None,
                   help="default: the window boundary in prices/window.json")
    p = sub.add_parser("plan"); p.add_argument("--limit", type=int, default=20)
    sub.add_parser("status")
    c = sub.add_parser("close"); c.add_argument("symbol"); c.add_argument("date")
    sub.add_parser("audit")
    ns = ap.parse_args()

    if ns.cmd == "ingest":
        cutoff = ns.since or since()
        added, seen, revs = ingest(ns.kind, ns.symbol, sys.stdin.read(), cutoff)
        print(f"{ns.symbol} {ns.kind}: {seen} rows in (since {cutoff}), "
              f"{added} new, {len(revs)} revision(s)")
        for r in revs:
            print(f"  REVISION {r['date']} {r['field']}: stored {r['stored']}, "
                  f"provider now {r['provider_now']} — stored value kept")

    elif ns.cmd == "plan":
        rows = plan(ns.limit)
        if not rows:
            print("nothing missing — every symbol has all three series")
        for _, _, _, sym, api, kind in rows:
            print(f"{kind:<10} {sym:<7} api={api}")

    elif ns.cmd == "status":
        man = manifest()
        miss = 0
        for sym, e in sorted(man.items(), key=lambda kv: (kv[1]["role"], kv[0])):
            d = e["daily"]
            flag = "" if d["rows"] else "  <- no closes"
            if not d["rows"]:
                miss += 1
            print(f"{e['role']:<9} {sym:<7} closes={d['rows']:>4} "
                  f"latest={d['latest'] or '-':<11} "
                  f"divs={e['dividends']['rows']:>3} splits={e['splits']['rows']:>2}{flag}")
        print(f"\n{len(man) - miss}/{len(man)} symbols have closes")

    elif ns.cmd == "audit":
        audit()

    elif ns.cmd == "close":
        ser = read_series("daily", ns.symbol)
        r = ser.get(ns.date)
        print(f"{ns.symbol} {ns.date}: {r['close']} (first seen {r['first_seen']})"
              if r else f"{ns.symbol} {ns.date}: not in store")
