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
| `render.py` | builds the HTML back from that JSON, with CSS/JS from `templates/` |
| `validate.py` | refuses a dashboard that is truncated, inconsistent, or silently stale |
| `roundtrip.py` | proves the renderer reproduces the page that is live today |
| `selftest.py` | damages today's dashboard seven ways and asserts the validator catches each |
| `domlite.py` | small tolerant HTML reader the other scripts share |

```sh
python3 tools/extract.py            # write the data layer
python3 tools/render.py stocks      # build the page from it (stdout)
python3 tools/validate.py           # check both dashboards, exit 1 on error
python3 tools/validate.py --strict  # warnings fail too
python3 tools/roundtrip.py          # renderer still matches the live pages
python3 tools/selftest.py           # regression test for the checks themselves
```

## The renderer

`render.py` is the half that removes the failure class rather than catching it:
the run produces data, and the page is assembled from it deterministically. CSS
and JS live in `templates/` and stop being rewritten on every run, so a partial
write cannot corrupt them.

`roundtrip.py` is its acceptance test, and it is deliberately two-sided —
either check alone can pass while something is quietly lost:

```
extract(render(data)) == data     nothing is dropped in transit
render(extract(page)) == page     the live page is reproducible
```

The page comparison re-parses both sides and re-serialises them with sorted
attributes, so attribute order, entity spelling and whitespace between tags
cannot cause a false failure — and a failure that does appear is real. One
difference is declared intentional: `crypto.html` carries two adjacent
`<style>` blocks and the renderer emits one.

Both dashboards pass both checks today. **Neither HTML file has been switched
over yet** — the pages in the repo are still the hand-written ones. Flipping
one is:

```sh
python3 tools/render.py stocks -o index.html
python3 tools/render.py crypto -o crypto.html
```

Until that happens, `roundtrip.py` running in CI is what keeps the renderer
honest: if a hand-written page grows a pattern the renderer cannot reproduce,
the check fails and says exactly where.

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
