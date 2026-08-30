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
- `tier1_ledger.jsonl` — the recovered ledger. Every row carries the
  methodology version that produced it (`methodology_version`, plus the rule
  hash and a `carried_forward` flag).
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
5. **Methodology versioned.** Every pick is stamped with the rule set that
   produced it, resolved by publishing commit. See `../methodology/`.

## Blocker A — closed: the methodology is frozen

The rules the engine actually ran are written down in `../methodology/`, one
frozen file per rule state, each anchored to the commits that published under
it and quoting the clause in `index.html` that establishes it. Every ledger row
is stamped with the version that produced it.

What the reconstruction found: **eleven rule states in thirteen days** — nine of
the ten transitions changed something that could move which stocks qualify. The two that matter most for scoring:

- **v10 (08-29) added a carry-forward rule** — tier-1 persists between runs when
  nothing contradicts it. The 08-28 picks were republished on 08-29 with no new
  research behind them (Alpha Vantage returned 0 of 18 calls). The rule lasted
  exactly one run. `score.py` does not open a position from a carried-forward
  row.
- **v7 (08-26) has no methodology section at all** — six tier-1 picks published
  under rules that cannot be verified from the artifact. Recorded as
  `undocumented` rather than inheriting v6's rules, because inheriting rules
  nobody wrote down is manufacturing evidence.

`score.py` now reports the version mix beside every aggregate, so no performance
number can be quoted without showing how many definitions it spans. It does not
refuse to pool across versions — at n=14 there is nothing else to do — it
refuses to hide that it is pooling. The power gate is untouched.

## Open: eight publication days are not in the ledger

The extractor reads tickers from `data-ticker`, an attribute that only appears
from 2026-08-27. Every earlier commit marks its cards with `data-q` (a search
string) instead. Ten commits across **2026-08-18, 08-19, 08-20, 08-23, 08-24 and
08-26 carry a tier-1 section with 48 cards this parser cannot read.**

They were being dropped silently. `extract_ledger.py` now names them at the end
of every run. They are not lost — they are hash-chained in git and recoverable
whenever the parser is taught the older markup. They are also the *oldest*
picks, the ones with the most outcome runway, so recovering them is worth more
per pick than any future day.

One wrinkle for whoever does it: the ledger keeps the last commit of each day as
that day's published state, and 08-26's last commit (`7e28804`) is a truncated
rebuild whose tier-1 section is empty. Day-final is the wrong rule there.

## Blocker: no close-price store

`score.py` deliberately does not fetch prices ad hoc. Scoring needs a daily
close store (one write per symbol per day, backfillable), not live quote calls
against a rate-limited key — the 08-29 quota exhaustion is exactly that failure.

## Honest status

14 positions, 4 publication days, **0 of ~250 pick-months** required before any
number here carries meaning. Roughly 12–18 months of disciplined publishing.
That wait is not a weakness of the plan; it is the reason the result cannot be
copied by someone starting later.
