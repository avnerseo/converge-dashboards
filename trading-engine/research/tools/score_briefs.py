#!/usr/bin/env python3
"""Score research briefs against what actually happened.

The brief is written by a model.  The confidence rating in it is written by the
same model that just built the argument, so it will track how convincing the
argument felt, not how likely it was.  This script is the part that lives
outside the model: it takes rows that were committed before the outcome existed
and asks whether the confidence field predicted anything at all.

Scoring rule, fixed in the skill before the first brief was written:

    excess = ticker return - benchmark return, over the horizon
    UP      correct when  excess >  +cost
    DOWN    correct when  excess <  -cost
    NO-EDGE correct when  |excess| <= cost

NO-EDGE is scored, not skipped.  Refusing to act is a prediction here, and a
system that cannot be wrong about its abstentions cannot be measured.

`cost` is the measured round-trip cost.  There is no default: the shakedown
that measures it opens 2026-09-01, and substituting a guess for it would make
every result unfalsifiable in exactly the way this script exists to prevent.

Usage:
    score_briefs.py --cost-bps 12            score everything scoreable
    score_briefs.py --due                     list rows whose horizon elapsed
    score_briefs.py --integrity               flag rows edited after logging
"""
import argparse, csv, datetime as dt, subprocess, sys, os

LOG = os.path.join(os.path.dirname(__file__), "..", "briefs", "research-log.csv")
DECISION_N, DECISION_GAP = 30, 15.0      # pre-registered 2026-08-30

def rows():
    with open(LOG, newline="") as f:
        return [r for r in csv.DictReader(f) if r.get("date")]

def elapsed_trading_days(start):
    """Weekdays since `start`.  US holidays are not handled — this only decides
    when to *ask* for a quote, never how a brief is scored."""
    d, n = dt.date.fromisoformat(start), 0
    today = dt.date.today()
    while d < today:
        d += dt.timedelta(days=1)
        if d.weekday() < 5:
            n += 1
    return n

def score(r, cost):
    tick = float(r["outcome_close"]) / float(r["ref_close"]) - 1
    bench = float(r["bench_outcome_close"]) / float(r["bench_close"]) - 1
    excess = tick - bench
    d = r["direction"].strip().upper()
    if d == "UP":
        ok = excess > cost
    elif d == "DOWN":
        ok = excess < -cost
    elif d == "NO-EDGE":
        ok = abs(excess) <= cost
    else:
        raise ValueError(f"{r['ticker']} {r['date']}: unknown direction {d!r}")
    return excess, ok

def report_due():
    for r in rows():
        if r["outcome_close"]:
            continue
        need = elapsed_trading_days(r["date"]) - int(r["horizon_days"])
        if need >= 0:
            print(f"DUE  {r['date']}  {r['ticker']:6s} h={r['horizon_days']:>3s}  "
                  f"quote needed for {r['ticker']} and SPY")

def report_integrity():
    """A logged row must never change.  git blame tells us whether any line was
    touched after the commit that introduced it."""
    out = subprocess.run(["git", "blame", "--line-porcelain", LOG],
                         capture_output=True, text=True)
    if out.returncode:
        print("git blame unavailable:", out.stderr.strip()); return
    first, edited = {}, []
    sha = summary = None
    for line in out.stdout.splitlines():
        if line and line[0].isalnum() and len(line.split()[0]) == 40:
            sha = line.split()[0]
        elif line.startswith("summary "):
            summary = line[8:]
        elif line.startswith("\t"):
            body = line[1:]
            if body.startswith("date,") or not body.strip():
                continue
            key = ",".join(body.split(",")[:2])          # date,ticker
            if key in first and first[key] != sha:
                edited.append((key, summary))
            first.setdefault(key, sha)
    if edited:
        print("!! rows touched by more than one commit — the record is not clean:")
        for k, s in edited:
            print(f"   {k}   last touched by: {s}")
    else:
        print("integrity ok: every logged row belongs to exactly one commit")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--cost-bps", type=float,
                   help="measured round-trip cost in basis points (no default by design)")
    p.add_argument("--due", action="store_true")
    p.add_argument("--integrity", action="store_true")
    a = p.parse_args()

    if a.due:
        return report_due()
    if a.integrity:
        return report_integrity()
    if a.cost_bps is None:
        sys.exit("refusing to score without a measured round-trip cost.\n"
                 "The shakedown (SHAKEDOWN_PREREG_2026-09-01.md) produces it. "
                 "Pass --cost-bps once it exists; do not guess it.")

    cost = a.cost_bps / 10_000
    buckets = {}
    for r in rows():
        if not (r["outcome_close"] and r["bench_outcome_close"]):
            continue
        excess, ok = score(r, cost)
        b = buckets.setdefault(r["confidence"].strip().title(), [0, 0])
        b[0] += ok; b[1] += 1
        print(f"{r['date']}  {r['ticker']:6s} {r['direction']:8s} "
              f"{r['confidence']:6s} excess={excess:+7.2%}  {'HIT' if ok else 'miss'}")

    total = sum(n for _, n in buckets.values())
    print(f"\ncost floor: {a.cost_bps:.1f} bps    scored: {total}")
    for name in ("High", "Medium", "Low"):
        h, n = buckets.get(name, (0, 0))
        if n:
            print(f"  {name:6s} {h}/{n} = {100*h/n:5.1f}%")

    hi, nhi = buckets.get("High", (0, 0))
    lo, nlo = buckets.get("Low", (0, 0))
    print()
    if total < DECISION_N:
        print(f"decision pending: {total}/{DECISION_N} briefs scored")
    elif not (nhi and nlo):
        print("decision blocked: need both High and Low briefs to compare")
    else:
        gap = 100*hi/nhi - 100*lo/nlo
        verdict = "KEEP" if gap >= DECISION_GAP else "REMOVE"
        print(f"High - Low = {gap:+.1f} pts vs the {DECISION_GAP:.0f} pt bar "
              f"set on 2026-08-30  ->  {verdict} the confidence field")

if __name__ == "__main__":
    main()
