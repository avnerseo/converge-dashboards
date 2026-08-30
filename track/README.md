# Converge Track Record

The dashboard rewrites `index.html` every day. Tier-1 picks appear, then vanish,
and nothing records what happened to them. This directory closes that hole.

## Why it exists

Between 2026-08-27 and 2026-08-30 the tier-1 list turned over almost completely:

| date | tier-1 |
|---|---|
| 08-27 | MSFT, CMCSA, BMY |
| 08-28 | CVX, CAT, KO, GEV, BRK.B, NKE |
| 08-29 | *(carried forward — Alpha Vantage quota exhausted)* |
| 08-30 | V, MSFT, AMZN, CVX, LLY, GOOGL, JPM, KO |

CMCSA and BMY were "high conviction" for exactly one day and were never
mentioned again. CAT, GEV, BRK.B and NKE lasted two. An engine whose output is
never scored can never be wrong — which means it can never be shown to be right
either. That is the asset being destroyed daily.

## Files

- `extract_ledger.py` — replays every commit touching `index.html`, parses the
  tier-1 cards (`data-ticker` / `.price`), and writes one row per pick per day.
  Git is the audit trail: commits are hash-chained, so a pick provably existed
  before its outcome was known. That property cannot be retrofitted.
- `tier1_ledger.jsonl` — the recovered ledger.
- `score.py` — turns the ledger into benchmark-relative performance.
- `scorecard.json` — output.

## What makes a track record real

1. **Excess return, not absolute.** Scored against SPY and the sector ETF.
   Beating nothing in a bull market is not evidence.
2. **Horizons fixed in advance.** 1w / 1m / 3m / 6m / 12m, chosen before the
   outcome is known.
3. **A pick is an event.** Entry = first appearance in tier-1. Removing a
   ticker from the dashboard does not close the position, and never erases it.
4. **Losses published.** A scorecard that omits the misses is marketing.
5. **Methodology versioned.** See the blocker below.

## Blocker: the methodology is not frozen

Right now tier-1 is fully recomputed each run, so the criteria that produced
08-28's list are not provably the criteria that produced 08-30's. Nothing can be
scored across a moving definition. Before the ledger is worth anything:

- pin the selection rules as `methodology/vN.json`, referenced by every run
- record which version produced each pick
- change the version deliberately, never silently

## Blocker: no close-price store

`score.py` deliberately does not fetch prices ad hoc. Scoring needs a daily
close store (one write per symbol per day, backfillable), not live quote calls
against a rate-limited key — the 08-29 quota exhaustion is exactly that failure.

## Honest status

14 positions, 4 publication days, **0 of ~250 pick-months** required before any
number here carries meaning. Roughly 12–18 months of disciplined publishing.
That wait is not a weakness of the plan; it is the reason the result cannot be
copied by someone starting later.
