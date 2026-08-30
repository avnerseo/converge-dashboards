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
  tier-1 cards across both markup eras (`data-ticker` from 08-27, the rendered
  `.ticker` span before it), and writes one row per pick per day.
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

## Closed: six publication days were missing from the ledger

The extractor read tickers only from `data-ticker`, an attribute that first
appears on 2026-08-27. Every earlier commit writes the ticker as the rendered
`<span class="ticker ltr">` and puts a lowercased search string in `data-q`.
Six publication days — 08-18, 08-19, 08-20, 08-23, 08-24, 08-26 — were being
dropped without a word.

Teaching the parser the older markup took the ledger from 23 rows over 4 days to
**61 rows over 10 days, and from 14 opened positions to 29**. The recovered days
are the oldest ones, with the most outcome runway ahead of them.

The dashboard's truncated rebuilds (`7e28804`, `c4b0f28`) turn out to be
harmless: their tier-1 sections are empty, so they produce no rows and can never
win the day-final tiebreak. `extract_ledger.py` now reports any commit whose
tier-1 section holds cards it could not read — that count is zero today, and a
non-zero one means the markup changed again.

## The daily close store

`store.py` and `prices/`. One row per symbol per day, append-only: a close is
written once, and if the provider later returns a different value for a date
already stored, the disagreement goes to `revisions.jsonl` and the stored value
stands. A store that silently accepts restatements cannot support a track
record, because last month's numbers stop being last month's.

Alpha Vantage's adjusted endpoint is premium on this key, but `DIVIDENDS` and
`SPLITS` are not — so total return is reconstructed from raw closes plus the
event series rather than bought. A dividend payer scored on price return alone
looks worse than it was.

The free key allows ~25 calls/day against a 39-symbol universe (29 positions,
SPY, 9 sector ETFs), so a full pass does not fit in one day and is not meant to.
`store.py plan` names what to fetch next, benchmarks first: a position with no
benchmark series cannot be scored, so fetching it first buys nothing. Network
access lives in the MCP tool, not in the script, so a fetch is two steps — call
`TIME_SERIES_DAILY`, pipe the CSV to `store.py ingest`.

Coverage as of 2026-08-30: **17 of 39 symbols**, all ten benchmarks and the
seven positions first picked on 08-18.

### The card price is not the entry price

`store.py audit` compares the price printed on each tier-1 card against the real
close. **No card price equals the close of the day it was published.** Where the
store has the day, the card carries the *previous* trading day's close; 08-18's
cards are staler still, matching a close from before the stored window. Some
cards label the staleness ("+1.68% (28.8)"), most do not.

Entering positions at the card price would therefore enter every one of them at
a price the pick was never made at. The card price stays in the ledger as what
was published; entry comes from the store, dated to the publication date.

## Open: 12 positions have no entry price

Several runs shipped tier-1 cards with no price at all — 08-20 published
fourteen of them, with the Alpha Vantage quota gone. Those positions open on
their first appearance and stay unpriced; `score.py` will not score them and,
critically, will not postpone their entry to a later day that happens to carry a
price. Re-dating a pick to a more convenient entry is the same accounting hole
as pretending a dropped ticker was never picked.

They need the daily close store below. Nothing else unblocks them.

## Blocker: no close-price store

`score.py` deliberately does not fetch prices ad hoc. Scoring needs a daily
close store (one write per symbol per day, backfillable), not live quote calls
against a rate-limited key — the 08-29 quota exhaustion is exactly that failure.

## Honest status

14 positions, 4 publication days, **0 of ~250 pick-months** required before any
number here carries meaning. Roughly 12–18 months of disciplined publishing.
That wait is not a weakness of the plan; it is the reason the result cannot be
copied by someone starting later.
