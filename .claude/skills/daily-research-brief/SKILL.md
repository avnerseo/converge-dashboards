---
name: daily-research-brief
description: Produce a structured, multi-role research brief on a US-listed stock or ETF using Alpha Vantage (data layer) and Bigdata.com (news/sentiment layer), ending in a mechanical, scoreable prediction that is logged before the outcome is known. Use when the user asks to "research", "analyze", or "brief" a ticker, or invokes /daily-research-brief <TICKER>. Research and paper-trading only — never a real-money recommendation.
---

# Daily Research Brief

A one-page memo on a ticker, produced by three analyst roles, grounded only in data
pulled live in this session — never from memory.

**What makes this version different from a generic research prompt:** it ends in a
*falsifiable prediction*, logged with a reference price *before* the outcome exists,
and it is scored later by a script rather than by the model that wrote it.

## Why the prediction block is mandatory

A brief with a bull case, a bear case and a confidence rating cannot be wrong. Every
loss becomes "the thesis changed" and every win becomes "as expected". That shape was
rejected in `research/BORA_PROMPT_REVIEW_2026-08-29.md`, and the same standard applies
here: **a confidence number graded by the model that produced the analysis is a mood,
not a measurement — unless something outside the model scores it later.**

`research/tools/score_briefs.py` is that outside thing.

## Hard rules

- **Never skip the data pull.** If a tool call fails, say so in the brief. Do not fill
  the gap from memory.
- **Validate the instrument before trusting a field.** Before using any data field,
  state what it actually measures. Precedent: in `INSIDER_CLUSTER_CHECK_2026-08-29.md`,
  13 of 13 records flagged "acquisition" were board grants at price 0.0 — the field did
  not mean what its name said.
- **Every claim traces to a data point pulled in this session.** No unsourced numbers.
- **No real-money recommendation, no position sizing.**
- **Mandate scope:** US-listed common stock and equity ETFs, daily bars, holding period
  in days. No crypto (separate track), no options, no leverage.
- **The log is append-only.** Never edit a logged row. A record that can be edited is
  not a record.

## Workflow

### Step 0 — Ticker and horizon
If not given, ask for the ticker and the horizon in **trading days** (the default is 21).
The bull/bear case differs by horizon, and the horizon is what gets scored.

### Step 1 — Data pull (Alpha Vantage)
At minimum:
- `TIME_SERIES_DAILY_ADJUSTED` — the reference close, and recent trend
- `EARNINGS` / `EARNINGS_CALENDAR` — last result, next date
- `COMPANY_OVERVIEW` — sector, valuation, margins
- Technicals only if they will be cited as evidence (`RSI`, `SMA`/`EMA`, `MACD`)

Also pull `TIME_SERIES_DAILY_ADJUSTED` for **SPY** — the benchmark reference close is
part of the logged row and cannot be reconstructed later.

*Budget note:* the cloud key is free tier, 25 requests per day, total. Plan the calls.

### Step 2 — News and sentiment (Bigdata.com)
- `bigdata_search` or `bigdata_sentiment_tearsheet` — recent news, sentiment shifts
- `bigdata_company_tearsheet` for a fuller picture

### Step 3 — Three roles, in order
Using **only** what Steps 1–2 returned:

1. **Macro analyst** — rates, sector rotation, macro releases.
2. **Company analyst** — earnings quality, growth, valuation, catalysts.
3. **Risk reviewer** — argues actively against the first two. What would invalidate
   the thesis? Which single data point would settle it?

The risk reviewer's job is to challenge, not to summarise. If it agrees with the first
two roles, it has not done its job — say what evidence would have changed its mind.

### Step 4 — The brief

```
# Research Brief: <TICKER> — <YYYY-MM-DD>
Horizon: <N> trading days

## Current market context
## Recent earnings / news
## Bull case
## Bear case
## Key risks
## What would change the thesis

## Prediction — mechanical, scored later
Direction:        UP | DOWN | NO-EDGE
Horizon:          <N> trading days
Reference close:  <ticker close on brief date>
Benchmark close:  <SPY close on brief date>
Invalidation:     <price level that ends the thesis>
Confidence:       Low | Medium | High

## Data sources used this session
- Alpha Vantage: <endpoints>
- Bigdata.com: <endpoints>
- Failed calls: <list, or "none">

Research / paper-trading only. Not financial advice. No trade recommendation.
```

**NO-EDGE is a real answer and is scored like any other.** It is correct when the
ticker moves with the benchmark inside the cost band. Refusing to act is a prediction
here, not an abstention — which is the point.

### Step 5 — Log it, then commit it
Append one row to `trading-engine/research/briefs/research-log.csv`:

```
date,ticker,horizon_days,direction,confidence,ref_close,bench_close,invalidation,brief_path,outcome_close,bench_outcome_close
```

Leave the two outcome columns empty — they are filled only after the horizon elapses.
Write the full brief to `trading-engine/research/briefs/<DATE>-<TICKER>.md`.

**Then commit and push, in the same session.** The git timestamp is what makes the
reference price a pre-registration rather than a claim.

## Scoring — the rule, fixed now, before any brief exists

`research/tools/score_briefs.py` scores a row as correct when the ticker's excess
return over the benchmark, across the horizon, exceeds the measured round-trip cost in
the predicted direction. NO-EDGE is correct when the excess return stays inside the
cost band.

**Scoring requires the measured round-trip cost**, which the shakedown produces from
2026-09-01. Until that number exists, briefs are **logged but not scored** — the script
refuses rather than substituting a guess. Nothing is lost by starting to log today.

### The pre-registered decision on the confidence field

> After **30 scored briefs**, if the hit rate of *High* confidence does not exceed the
> hit rate of *Low* confidence by at least **15 percentage points**, the confidence
> field is removed from this skill.

Written 2026-08-30, before the first brief. Not to be revised after seeing the numbers.

## What this skill deliberately does not do

- No broker connection, no order placement, no position sizing.
- No crypto, options, leverage, or non-US listings.
- No investment advice, for the user or anyone else.
