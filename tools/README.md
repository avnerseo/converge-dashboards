# tools

The dashboards used to be their own database: every number lived inside
`index.html` / `crypto.html`, so a partially written file lost data outright
(27.8.2026 took four rebuild commits), and "carried forward from yesterday"
survived only as a sentence in a commit message.

These three scripts turn each dashboard into **data + presentation**, and make
staleness an explicit field instead of prose. Standard library only — nothing to
install, which matters when this runs unattended.

| script | what it does |
| --- | --- |
| `extract.py` | parses the HTML into `data/<dashboard>/<as_of>.json` (+ `latest.json`) |
| `validate.py` | refuses a dashboard that is truncated, inconsistent, or silently stale |
| `selftest.py` | damages today's dashboard seven ways and asserts the validator catches each |
| `domlite.py` | ~90-line tolerant HTML reader the other scripts share |

```sh
python3 tools/extract.py            # write the data layer
python3 tools/validate.py           # check both dashboards, exit 1 on error
python3 tools/validate.py --strict  # warnings fail too
python3 tools/selftest.py           # regression test for the checks themselves
```

## What validation catches

**Structure** — every required section exists and carries content; no table is
empty or ragged; every card has a ticker and its reasoning. A truncated write
fails here instead of reaching `main`.

**Consistency** — the headline numbers must still match the rows behind them:
unique tickers across tables א׳+ב׳+ג׳, tier-1 count, high-risk count. This is
what catches silent drift after a partial run.

**Freshness** — the run date is reported and flagged past three days. Any price
that is carried over must be dated, and any price that is missing must say why.
A page where nothing was fetched today says so out loud.

## Price fields

The single most useful thing the extractor does is turn a free-text price line
into an honest reading:

```json
"price": {
  "raw": "$199.77 −0.22% (28.8, לא עודכן היום)",
  "value": 199.77, "change_pct": -0.22,
  "available": true, "stale": true, "as_of": "28.8", "note": "לא עודכן היום"
}
```

`available: false` with a `note` is a quota failure; `stale: true` with an
`as_of` is yesterday's number, shown as yesterday's. Neither can be mistaken for
a live quote by anything reading the JSON.

## Data layout

```
data/stocks/2026-08-29.json   one file per run, keyed by the page's own run date
data/stocks/latest.json       copy of the newest run
data/crypto/…
```

Keeping every run is what makes day-over-day deltas possible later — a stock
entering or leaving tier 1, a risk flag raised.
