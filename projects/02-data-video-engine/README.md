# 02 — Data video engine

The first task from `BRIEF.md` is done: one command goes from JSON to a finished
vertical MP4, with Converge as customer zero and its own daily dashboard as the
feed. Marginal cost is compute only — no API is called during a render.

```bash
pip install playwright imageio-ffmpeg     # once; do NOT run `playwright install`
./render.sh                               # index.html -> out/converge-YYYY-MM-DD.mp4
```

## What it produces

`out/converge-2026-08-30.mp4` — 1080×1920, 22.1 s, 30 fps, h264 High yuv420p
with a silent AAC track, 1.75 MB. Built from the 30.8.2026 dashboard: intro,
KPI counters, the five highest-conviction tier-1 stocks, the day's three
sharpest movers, outro. All text in Hebrew, all numbers rendered from the feed.

## Measurements

Container: 4 vCPU, `chromium_headless_shell-1194`, `imageio-ffmpeg` 7.0.2.

| | |
|---|---|
| Render time | **78 s wall** for a 22.1 s video (663 frames) |
| Capture rate | 9.8 frames/s |
| Machine CPU | **265 core-seconds** = 0.074 CPU-hours |
| Output size | **1.75 MB** (584 kb/s) |
| Peak scratch disk | **0** — frames are piped, never written |
| API cost | **$0.00** — nothing but `file://` is loaded during a render |
| Compute cost | **≈ $0.003 / video** at $0.036 per vCPU-hour |

That is the number the whole direction rests on. A daily video for one customer
costs about a third of a cent; for a hundred customers, about thirty cents a
day. Against that, subscription pricing has essentially 100% gross margin, and
the render cost never becomes an argument for charging per video.

Two headroom notes: rendering is single-threaded per video, so a 4-vCPU box runs
four customers concurrently at the same wall time; and PNG frame transport was
the original bottleneck at 2.9 fps — JPEG q95 got it to 9.8 (see below).

## Pipeline

```
index.html ──▶ extract_feed.py ──▶ payload JSON ──▶ capture.py ──▶ MP4
  daily          feed adapter        the contract     scene + ffmpeg
  dashboard      (customer-specific) (generic)        (generic)
```

| file | role |
|---|---|
| `render.sh` | the one command |
| `scripts/extract_feed.py` | Converge dashboard → payload. **The only customer-specific file.** stdlib only |
| `scene/scene.html` `.css` `.js` | parameterised scene; `SCENE.init(payload)` / `SCENE.seek(t)` |
| `scene/fonts/` | Heebo, 4 weights, vendored (SIL OFL 1.1) |
| `scripts/capture.py` | headless Chromium capture, determinism enforcement, ffmpeg encode |
| `checks/bidi_check.py` | proves the Hebrew BiDi rule is needed |
| `checks/determinism_check.py` | renders twice, diffs frames and file bytes |
| `notes/` | the two findings worth keeping |

The payload boundary is real, not aspirational: `payload/example-ecommerce.json`
is a Peluma storefront feed, and `scripts/capture.py payload/example-ecommerce.json
-o out/example-ecommerce.mp4` renders a fully branded Peluma video with **zero
code changes**. Branding, colour, copy and rows all come from the JSON. A second
customer is a second adapter — roughly 150 lines — not a second engine.

## The two traps in the brief — both real, both handled

**Hebrew BiDi was genuinely broken.** `−9.75%` inside an RTL block renders
visually as `9.75%−`: the minus detaches and parks on the wrong side of the
number. Measured by reading back per-glyph bounding boxes, not by eyeballing a
screenshot. Three of five test strings were wrong. Every daily loss would have
shipped with a misplaced sign. Fixed by making every numeric run its own LTR
island in code. Fonts and line breaking were fine, but Heebo is vendored anyway
so the render does not depend on the host's fontconfig. → `notes/hebrew-rtl.md`

**Determinism is enforced, not promised.** The scene exposes `seek(t)` and every
visual property is a pure function of `t`, so a frame is defined by its index
rather than by when it was captured. The harness then aborts every non-`file://`
request, traps `Date`/`performance.now`/`Math.random`/`rAF`/timers and fails the
run if any were touched, verifies the font actually loaded, and hashes every
frame. Two consecutive runs produce **identical frame hashes and a bit-identical
MP4**. → `notes/determinism.md`

```
$ python3 checks/determinism_check.py
ok   all 663 frames identical
ok   mp4 bit-identical  sha256=6785583c5577fd06...
ok   no determinism violations
ok   no blocked requests
```

## Three things that cost real time, recorded so they cost nobody else any

- **`--deterministic-mode` hangs the capture.** The name is a trap: it enables
  begin-frame-control, so the compositor only draws when a client drives frames,
  which Playwright's screenshot path does not do. Every capture times out.
- **PNG screenshots were 100% of the bottleneck**, not rendering, not the CSS
  blur. Chromium's PNG encoder costs ~340 ms/frame. JPEG q95 measures 44.4 dB
  PSNR against the PNG reference and runs 6.5× faster; the residual is chroma
  subsampling, which yuv420p h264 applies regardless. Quality is unchanged in
  the final file. `--frame-format png` is still there for archival.
- **ffmpeg's stderr must not be a pipe.** Once 64 KB of decoder warnings fill
  it, ffmpeg stops reading stdin, the frame write blocks, and the render hangs
  forever. It goes to a temp file.

## Where the brief was imprecise

`../README.md` says to install ffmpeg via `pip install imageio-ffmpeg` — correct
and verified, and its libx264 is what encodes here. It also warns the
Playwright-bundled ffmpeg is stripped; also correct, and this pipeline never
touches it. But the inventory does not mention that the **pip `playwright`
package expects `chromium-1234` while the image ships `chromium-1194`**, so
`p.chromium.launch()` fails out of the box. Every entry point here passes an
explicit `executable_path`, overridable with `$CONVERGE_CHROME`. Worth adding to
the shared inventory for the other two projects.

## Not done yet

- No audio bed or voiceover — the track is silent by design for now.
- Publishing (YouTube/TikTok upload) is not wired; the pipeline ends at a file.
- One scene template only. A second customer currently gets Converge's layout
  with their data and branding.
- Determinism is guaranteed against a *pinned* Chromium build; different builds
  rasterise text fractionally differently. The build path is recorded in every
  manifest.
