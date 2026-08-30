---
name: daily-research-brief
description: Produce a structured, multi-role research brief on a stock/ETF/crypto ticker using Alpha Vantage (data layer) and Bigdata.com (news/sentiment layer). Use when the user asks to "research", "analyze", or "brief" a ticker, or invokes /daily-research-brief <TICKER>. Never used to recommend or execute real-money trades — research and paper-trading only.
---

# Daily Research Brief

Produces a one-page research memo on a ticker by running three analyst "roles" in
sequence, grounded entirely in data pulled live from Alpha Vantage and Bigdata.com —
never from memory or assumption.

## Hard rules

- Never skip the data-pull step. If a tool call fails, say so explicitly in the brief
  rather than filling in the gap from memory.
- Never recommend a real-money trade or give position sizing. This produces research
  output only, for paper-trading evaluation.
- Every claim in the brief must trace back to a specific data point or headline pulled
  in this session.
- Log every brief (see "Logging" below) so results can be checked against outcomes later.

## Workflow

### Step 0: Get the ticker and horizon
If not given, ask: which ticker, and what time horizon (day trade / swing / long-term
thesis) — the bull/bear case differs a lot by horizon.

### Step 1: Data pull (context layer — Alpha Vantage)
Pull, at minimum:
- `GLOBAL_QUOTE` or `TIME_SERIES_DAILY_ADJUSTED` — current price, recent trend
- `EARNINGS` and/or `EARNINGS_CALENDAR` — last reported results, next date
- `COMPANY_OVERVIEW` — fundamentals (P/E, margins, sector)
- Relevant technicals if the horizon is short-term (e.g. `RSI`, `SMA`/`EMA`, `MACD`)

### Step 2: News & sentiment pull (Bigdata.com)
- `bigdata_search` or `bigdata_sentiment_tearsheet` for the ticker — recent news,
  analyst sentiment shifts, notable events in the last 1–4 weeks
- `bigdata_company_tearsheet` if a fuller picture is needed

### Step 3: Three-role analysis (analyst layer)
Using ONLY the data gathered above, reason through three roles explicitly, in order:

1. **Macro analyst** — sector/macro backdrop: rates, sector rotation, relevant
   macro releases (CPI, Fed, etc. via Alpha Vantage economic indicators if relevant).
2. **Company analyst** — company-specific: earnings quality, growth, valuation vs.
   peers, recent news/catalysts.
3. **Risk reviewer** — actively looks for reasons the bull case could be wrong:
   what would invalidate the thesis, what's the key risk, what data point to watch.

Do not let one role's conclusion bleed into another uncritically — the risk reviewer's
job is specifically to challenge the first two.

### Step 4: Produce the brief
Output in exactly this format:

```
# Research Brief: <TICKER> — <DATE>
Horizon: <day/swing/long-term>

## Current market context
...

## Recent earnings / news
...

## Bull case
...

## Bear case
...

## Key risks
...

## What would change the thesis
...

## Confidence rating: <Low/Medium/High> — <one-line reason>

## Data sources used this session
- Alpha Vantage: <which endpoints>
- Bigdata.com: <which endpoints>

⚠️ Research/paper-trading use only. Not financial advice. No trade recommendation.
```

### Step 5: Logging
Append the brief (or a link to it) plus date and ticker to `research-log.md` in the
project directory, so it can later be compared against what actually happened. If that
file doesn't exist yet, create it with a simple table: Date | Ticker | Horizon |
Confidence | Outcome (fill in later).

## What this skill deliberately does NOT do

- No broker connection, no order placement, no position sizing.
- No blending of Webull or Kepler (per current project scope).
- No treating this as investment advice for the user or anyone else.
