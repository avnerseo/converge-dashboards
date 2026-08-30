# Projects — parallel workstreams

Three directions are being developed in parallel, each in its own Claude session
and its own folder here. Everything a project produces — data, scripts, notes,
outputs — stays inside its own folder.

| # | folder | direction | pace |
|---|---|---|---|
| 01 | `01-track-record/` | Make Converge's stock engine falsifiable: a public, verified track record | slowest, most defensible |
| 02 | `02-data-video-engine/` | A machine that turns any data feed into a daily video; sell the machine | medium |
| 03 | `03-dubbing-arbitrage/` | Produce in Hebrew, export to many languages at the cost of one | fastest to revenue |
| 04 | `04-peluma/` | Live Shopify store: fix unit economics before any video spend | live business |

Each folder has a `BRIEF.md` that is self-contained — a session starting fresh
should be able to read only that file plus this one and begin work.

## Branch convention

Base branch: `claude/video-creation-capability-433k8w`.
Each project works on its own branch off that base, so the three sessions never
collide:

- `claude/track-record`
- `claude/data-video-engine`
- `claude/dubbing-arbitrage`
- `claude/peluma`

Never push to another project's branch.

## Verified asset inventory

Checked directly on 2026-08-30 — these are measured, not assumed.

### Generation
- **OpenArt** (`avnerseo@gmail.com`) — Plus plan, **10,000 credits**. Video from
  50 credits (PixVerse V6, 540p/5s) up to 400 (Seedance 2.0, Grok Imagine 1.5).
  Images from 10 (Kling 3 Omni) to 42 (GPT Image 2). Call `openart_model_cost`
  for a live quote before generating — price varies with resolution, duration
  and audio.
- **Motion** — connected but **0 credits**. Cheapest entry is Flex, $5 / 200
  credits (~1–2 videos). Do not buy without a reason OpenArt cannot cover.

### Local rendering (free, verified working)
- `ffmpeg` **is not on PATH**. Install with `pip install imageio-ffmpeg`, then
  `python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())"`.
  That build has libx264 / aac / libvpx / gif and was verified rendering h264.
- Playwright ships its own ffmpeg at `/opt/pw-browsers/ffmpeg-1011/ffmpeg-linux`
  — **it is stripped** (no libx264, no lavfi). Only good for Playwright's own
  screen recording. Do not use it to encode.
- Chromium is pre-installed (`PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`).
  Never run `playwright install`.

### Data
- **Alpha Vantage MCP** — rate limited to ~1 call/second, and the daily quota
  has been exhausted before (2026-08-29 run degraded because of it). Use
  `GLOBAL_QUOTE` per symbol. `REALTIME_BULK_QUOTES` is a **premium endpoint that
  returns fabricated sample data** on this key — never treat its output as real.
- **Bigdata.com MCP** — institutional unstructured content with entity
  resolution. Needs `rp_entity_id` from `find_securities` for tearsheets.

### Commerce (workstream 04)
- **Shopify** — store "Peluma", pelumapets.com, Basic plan, USD. Two products:
  Mist Grooming Brush ($29.90) and Paw Wash Cup ($16.90).
- **Zendrop** — store id `3546333`. 2026-06-01→08-30: **1 order, $29.90 revenue,
  $8.20 gross profit**. ~23.5% contribution after payment fees. Paid ads are not
  viable at that margin until pricing is fixed.

### Failing MCP servers
`COMPOSIO` and `openart_ai` returned 404 on connect. The working OpenArt server
is the one named `OPENART`.

## Two external constraints that shape all three projects

1. **YouTube "inauthentic content".** Policy renamed 2025-07-15; a coordinated
   enforcement sweep in January 2026 removed channels totalling ~35M subscribers
   and 4.7B lifetime views from the Partner Program. Three strikes: warning →
   90-day suspension → permanent removal. AI **as a tool** assisting human
   creative work stays monetizable; AI **replacing** creative input in
   mass-produced, template-driven output does not. Every output must clear this
   line.
2. **Israeli investment advice law** (חוק הסדרת העיסוק בייעוץ השקעות, התשנ"ה-1995).
   Personal investment advice for compensation is a licensed activity, and
   broker affiliate commissions structurally resemble "investment marketing"
   (שיווק השקעות), which is licensed in its own right. General educational
   content is usually outside it. Not settled — needs a lawyer before any
   money flows through project 01. Do not build a revenue model on affiliate
   commissions without that check.
