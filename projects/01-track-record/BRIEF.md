# 01 — Make the engine falsifiable

Read `../README.md` first for the shared asset inventory and constraints.

## The finding

`index.html` is rewritten on every daily run. Tier-1 ("שכבה 1 — שכנוע גבוה")
picks appear and vanish, and nothing records what happened to them. Replaying
all 42 commits that touch `index.html` since 2026-08-18 gives:

| date | tier-1 picks | outcome |
|---|---|---|
| 08-27 | MSFT, CMCSA, BMY | CMCSA and BMY gone the next day, never mentioned again |
| 08-28 | CVX, CAT, KO, GEV, BRK.B, NKE | CAT, GEV, BRK.B, NKE gone within two days |
| 08-29 | *(carried forward)* | Alpha Vantage quota exhausted |
| 08-30 | V, MSFT, AMZN, CVX, LLY, GOOGL, JPM, KO | fully recomputed |

Median holding period of a "high conviction" pick: **two days**. None were ever
scored. An engine whose output is never measured cannot be wrong — so it can
never be shown to be right either.

## The thesis

Not better picks. **Be the only Hebrew-language screening engine that publishes
its scoreboard, including the losses.** A competitor starting in 2027 cannot
hold a verified 2026 record at any price. It is the one moat here that is
accumulated rather than bought.

Git strengthens it: commits are hash-chained, so a pick provably predates its
outcome. Screenshot track records are trivially faked; a commit chain is not.
This property cannot be added retroactively — every day without extraction is
lost.

## What already exists

In `track/`, committed as `909f412`:

- `extract_ledger.py` — replays every commit touching `index.html`, parses
  tier-1 cards (`data-ticker`, `.price`), writes one row per pick per day.
  Recovered **14 positions across 4 publication days**.
- `tier1_ledger.jsonl` — the recovered ledger.
- `score.py` — benchmark-relative excess return over horizons fixed in advance
  (1w/1m/3m/6m/12m). Deliberately **refuses to print a number** below ~250
  pick-months of statistical power, and currently reports `NO SIGNAL YET`.
- `README.md` — methodology and the rules that make a record real.

## Two blockers — this is the actual work

**A. The methodology is not frozen.** Tier-1 is fully recomputed each run, so
the criteria behind 08-28's list are not provably those behind 08-30's — the
dashboard's own transparency note admits this. Nothing can be scored across a
moving definition. Needed: `methodology/vN.json`, referenced by every run, every
pick stamped with the version that produced it, changed deliberately and never
silently.

**B. There is no daily close-price store.** Scoring needs a backfillable daily
close series, not ad-hoc quote calls against a rate-limited key — the 08-29
quota failure is exactly that symptom. One write per symbol per day, stored,
re-checkable.

## First task

Blocker A. Read the current selection logic out of `index.html` and the
methodology sections, write it down as an explicit versioned rule set, and make
the ledger record which version produced each pick. Do not change what the
engine picks — only make what it did legible and stable.

## Non-negotiables

1. Excess return vs SPY and the sector ETF. Absolute return in a bull market is
   not evidence.
2. Horizons fixed before the outcome is known.
3. A pick is an event. Removing a ticker from the dashboard does not close the
   position and never erases it.
4. Losses published as prominently as wins. A scorecard that omits misses is
   marketing.
5. Never report a performance number the sample cannot support. `score.py`
   enforces this; keep it that way.

## Honest risk

The likely outcome is that the engine does not beat the market — most selection
methods do not. That gets discovered publicly after a year of work. It is still
worth it: either the method is proven and uncopyable, or it is disproven with
real instrumentation instead of five more years of intuition, and the
measurement apparatus itself is a product for anyone who publishes forecasts.

## Timeline honesty

~250 pick-months are needed before any number means anything: roughly 12–18
months of disciplined publishing. That wait is the moat, not a flaw in the plan.
