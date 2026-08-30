# 03 — Findings

**Date:** 2026-08-30 · **Branch:** `claude/dubbing-arbitrage`
**Status:** vendor verification **blocked**; everything not requiring vendors is built.

**Recommendation: abandon as a standalone direction; do not buy any dubbing
tool.** The core of that recommendation is arithmetic on the brief's *own*
quoted numbers and needs no vendor access — see §4. Corroborating evidence from
search exists but is explicitly **not** treated as verification — see §5.

---

## 1. The blocker

The brief's first task was to read vendors' **actual current pricing pages** and
run a clip through two of them. Neither is possible in this container.

Egress is allowlisted and the dubbing vendors are not on the list. Measured, not
assumed — every one of these returns `EGRESS_BLOCKED` from the policy proxy:

`elevenlabs.io` · `api.elevenlabs.io` · `www.heygen.com` · `docs.heygen.com` ·
`www.rask.ai` · `www.veed.io` · `perso.ai` · `www.kapwing.com` ·
`support.google.com` · `en.wikipedia.org` (control)

The Wikipedia control confirms a blanket policy, not a vendor-specific block.
`WebFetch` uses the same policy, so it is not a way around it.

**A local Hebrew-ASR measurement was also attempted and is impossible here.**
`pypi.org` *is* reachable — `faster-whisper` installs fine — but every source of
model weights or Hebrew speech data is blocked: `huggingface.co`,
`hf-mirror.com`, `openaipublic.azureedge.net` (Whisper's own weight CDN) and
`commonvoice.mozilla.org` all return 403 at the tunnel. So even the one risk that
could have been measured without a vendor account — Hebrew word error rate — cannot
be measured here.

**There are no vendor credentials either.** No `ELEVENLABS_*`, `HEYGEN_*` or
`RASK_*` key exists in the environment, so tasks 2–4 would need a paid account
even with egress open.

| Brief task | Status |
|---|---|
| Read actual pricing pages | ❌ blocked → §2 asks you to do it |
| Run a Hebrew clip through two tools | ❌ blocked (no egress, no accounts) |
| Judge transcription / naturalness / numbers / timing | ❌ blocked → rubric frozen in advance, `RUBRIC.md` |
| Measured cost per finished minute | ❌ blocked → model built and parameterised, `tools/cost_model.py` |

---

## 2. What I need from you

**`VERIFICATION_REQUEST.md`** — exactly which pages to open, the exact question
on each, and a fill-in form. About 15 minutes.

The question to ask first, at every vendor, is not about price:

> **Is Hebrew supported as a SOURCE language?**

Every vendor lists Hebrew as a *target*, because English→Hebrew is the common
direction. This project needs the opposite, and that list is usually shorter. If
Hebrew is not a supported source, that vendor is out and its pricing is
irrelevant. This can end the project in 60 seconds and nothing else should be
read until it is answered.

---

## 3. What was built while blocked

Everything in the rewritten brief that does not need vendor access:

| Deliverable | What it is |
|---|---|
| `VERIFICATION_REQUEST.md` | The precise ask above |
| `tools/cost_model.py` | Cost model parameterised by rate × languages × minutes, both billing models, studio break-even. Confirmed numbers drop in via `--rate` |
| `source_clip/script_he.md` | 88s Hebrew market-update script, every line loaded with a specific failure mode |
| `source_clip/ground_truth.json` | Machine-readable ground truth: 6 segments, 4 tickers, 12 numbers, 4 gender-agreement forms, thresholds |
| `source_clip/RECORDING_INSTRUCTIONS.md` | How to record the human source clip |
| `tools/build_clip.py` | Builds the fixture from a recording, or a synthetic placeholder for pipeline debug; emits timecoded MP4 + transcript + SRT |
| `tools/retime.py` | Derives segment boundaries from measured duration |
| `tools/score.py` | Scores WER and critical-token survival against the ground truth |
| `RUBRIC.md` | Evaluation rubric, **frozen before any output exists** |

Two things the fixture work actually surfaced:

- **The first script was too long.** Estimated timings had five of six segments
  overrunning their slots — ~95s of content in a 78s frame, over the brief's 90s
  ceiling. Retimed from measured synthesis to 87.5s. Guessing at timings would
  have produced a fixture that silently failed dimension 4.
- **The scale traps work.** `tools/score.py` self-test: a Spanish output
  rendering `ארבעה טריליון` as "4 trillones" and `מאה ועשרה מיליארד` as
  "110 billones" trips the kill rule on both. Those are a 10⁶ error and a 10³
  error delivered in an authoritative voice. This is the specific risk the
  brief's "numbers don't change across languages" premise assumes away, and the
  fixture is built to catch it.

The synthetic placeholder in `source_clip/build/` is for pipeline debug **only**.
espeak-ng is a formant synthesiser; sending it to a vendor would produce a
failure that says nothing about real Hebrew speech.

---

## 4. What is established WITHOUT vendor access

This section needs no web source. It is arithmetic on the numbers the brief
itself quotes. Run `python3 tools/cost_model.py`.

### 4a. The AI-vs-studio comparison is not a comparison

Break-even against the cheapest studio quote ($5,000/hr/language) is
**$83.33 per finished minute**, and it is *independent of video length and
language count* — both sides scale identically, so the comparison collapses to
$/hour against $/minute.

The brief's own quoted AI range tops out at $3.00/min: **3.6% of break-even.**
AI dubbing beats studio by 150–455×. That was never in doubt and was never the
decision. The relevant comparison is against $0, not against studios.

### 4b. The billing question is too small to be a business

The entire prize — the gap between "billed per source minute" and "billed per
target language" — at the brief's own quoted rates, for a 10-minute video into 5
languages:

| $/min (unverified, from the brief) | per source minute | per target language | the gap |
|---|---|---|---|
| $0.10 | $1.00 | $5.00 | **$4** |
| $0.55 | $5.50 | $27.50 | **$22** |
| $2.40 | $24.00 | $120.00 | **$96** |
| $3.00 | $30.00 | $150.00 | **$120** |

**At the top of the brief's own range the entire founding question is worth $120
per video.** Confirming or refuting per-source-minute billing changes the
economics by an amount that does not decide anything. The brief put its weight
on this variable; the variable cannot carry it.

This holds whichever way the verification comes back. It is the strongest thing
in this document and the only part that is fully verified.

---

## 5. Unverified signals — NOT findings

Everything below came from `WebSearch`, which returns **secondhand summaries of
vendor pages, not the pages themselves**. Per `../README.md` that is not
verification and must not be recorded as if it were. It is logged here because
it is directionally consistent and because it tells you which questions in
`VERIFICATION_REQUEST.md` matter most — not because it settles anything.

**Confidence: low-to-moderate. Do not cite any of this as established.**

| Signal | Source grade | Bears on |
|---|---|---|
| HeyGen bills per target language — "5-min video × 5 languages ≈ 25 billable minutes" | third-party blogs | Directly contradicts the brief's premise. → HeyGen Q2 |
| Rask bills per target language — "5-min × 3 languages = 15 minutes, not 5"; lip-sync doubles it | third-party blogs | Same. → Rask Q2 |
| ElevenLabs 2,000–10,000 credits/min, per language | third-party blogs | Matches the brief's own expectation |
| YouTube ships free first-party auto-dubbing to all creators, Hebrew a supported source into English | trade press + YouTube blog | If true, the mechanic is free on the target platform |
| YouTube's routing is hub-and-spoke: 29 languages→English, English→20. Hebrew→Spanish/Portuguese not covered | trade press | → YouTube Studio Q1, the most authoritative check available to you |
| Hebrew is not in YouTube's 8 "Expressive Speech" languages | trade press | The free Hebrew→English dub would be the flat-affect version |
| Market CPM: Israel $14.08, US $32.75, blended Spanish ≈$3, blended Portuguese ≈$2 (Brazil $1.64) | **SEO aggregator sites — weakest evidence here** | Would invert the brief's RPM premise |
| Hebrew ASR is a documented low-resource weak point; a 2025 Interspeech paper built a 314-hour corpus because "Hebrew still lacks robust open-source solutions", beating stock Whisper by up to 29% | peer-reviewed | The strongest-graded source in this table, and it bears on the risk upstream of everything |

⚠️ Several vendor "comparison" pages surfaced in these searches are **published
by Perso and by HeyGen themselves.** The vendor-incentive problem the brief
flagged is not hypothetical — it is visibly present in the top results.

### If these signals are true, what they imply

Stated conditionally, because they are unverified:

*If* the CPM figures hold, the export routes split badly: the only route paying
more than the home market (→English, 2.3×) is the one YouTube covers free, while
every route you would pay for (→Spanish, →Portuguese) lands in markets 5–9×
*below* Israel's CPM. Israel would be a high-CPM market — the brief treats Hebrew
as a low-value origin to escape, and that would be backwards.

The volume counter-argument is real: Spanish has ~55× more speakers at ~0.2× the
CPM. But that changes the thesis from "same content, higher RPM" to "same
content, far lower RPM, betting on volume" — as an unknown channel with a
synthetic voice, in a saturated market, unable to read its own comments. That is
a different and worse bet than the one the brief describes.

**None of this is needed for the recommendation.** §4 stands alone.

---

## 6. An unconsidered risk

`../README.md` flags Israeli investment-advice law. Exporting Hebrew financial
content **outward** does not escape it — it adds to it. Content published in
English, Spanish or Portuguese and targeted at those audiences may engage the
financial-promotion regimes of the US, UK and EU on top of the Israeli one.
Dubbing multiplies regulatory surface at the same rate it multiplies audience.

Not researched, blocks nothing today, belongs in the lawyer conversation project
01 already needs.

---

## 7. Recommendation

**Abandon as a standalone direction. Buy nothing.**

Grounds, in descending order of how well established they are:

1. **Verified arithmetic (§4).** The billing question is worth ≤$120 per video at
   the top of the brief's own quoted range, and the studio comparison it anchors
   on is off by a factor of 28. The project's founding question cannot carry a
   business regardless of how it resolves.
2. **Unverified but consistent (§5).** The mechanic appears not to exist at the
   named tools; where it does exist YouTube appears to give it away; and the
   export economics appear to run backwards.
3. **Untested and upstream (§5, peer-reviewed).** Hebrew ASR is the weak link and
   sits before everything else in the pipeline. Hebrew-as-source is also the
   direction these tools are worst at — all of them are built and benchmarked on
   English→X.

**What to keep — a checkbox, not a project.** When 01/02 ship a Hebrew video,
upload it and enable the free auto-dubbed English track, reviewing before
approving. Cost $0, policy risk none (YouTube's own feature on your own original
content), and the manual approval step is both the quality gate for §3's
number-mangling risk and the human creative judgement that keeps the output clear
of the inauthenticity line.

**Do not reallocate effort here from 01, 02 or 04.** The brief calls this "the
fastest path to revenue." On the evidence it is a $0 feature of whatever 01 and
02 produce. The bottleneck was always the content.

---

## 8. What would change my mind

Ranked. These are falsifiable and the fixtures are built to test them.

1. **HeyGen or Rask turns out to bill per source minute after all.** Direct hit on
   §5, and it would mean the mechanic is real. It would still have to clear §4 —
   at the brief's rates the gap is ≤$120/video — but it would justify running the
   clip test. → `VERIFICATION_REQUEST.md`, HeyGen Q2 / Rask Q2.
2. **Your YouTube Studio offers Spanish and Portuguese for a Hebrew video.** Then
   even the narrow paid opening closes, and the checkbox in §7 captures the whole
   thesis for free. → YouTube Q1.
3. **A vendor does not support Hebrew as a source at all.** Removes it entirely,
   whatever its pricing. → every vendor's Q1.
4. **The clip test passes cleanly** — kill rule intact across English *and*
   Spanish, natural output, timing within 300ms. That would refute §7's third
   ground and make this a quality-adequate but low-value direction rather than a
   dead one. Needs egress + one paid account; `RUBRIC.md` is frozen so the
   judgement cannot be fitted afterwards.

The cheapest decisive experiment is **rubric dimension 5**: dub the fixture into
one language, note the credit balance, dub into a second, note it again. If the
second is free, the brief's claim holds. Five minutes, one account, and it
settles the founding question without reading a pricing page correctly.

---

## 9. Sources

All §5 material is secondary; vendor primary pages were unreachable (§1).
Retrieved 2026-08-30 via search, snippets only.

**Per-language billing:** [eesel on HeyGen pricing](https://www.eesel.ai/blog/heygen-pricing) ·
[fluxnote HeyGen translation guide](https://fluxnote.io/guides/heygen-video-translation-guide) ·
[HeyGen Help Center](https://help.heygen.com/en/articles/10029081-how-to-get-started-with-video-translation) ·
[geckodub on Rask pricing](https://www.geckodub.com/en/blog/rask-ai-pricing-plans-alternatives) ·
[geckodub on ElevenLabs dubbing pricing](https://blog.geckodub.com/elevenlabs-ai-dubbing-pricing) ·
[Flexprice ElevenLabs breakdown](https://flexprice.io/blog/elevenlabs-pricing-breakdown)

⚠️ Vendor-published, treat as marketing: [Perso on Rask](https://perso.ai/blog/rask-ai-dubbing-review-2026-features-pricing-how-it-compares) ·
[HeyGen vs Rask vs Maestra vs Kapwing, published by HeyGen](https://www.heygen.com/blog/heygen-vs-rask-ai-vs-maestra-vs-kapwing)

**YouTube auto-dubbing:** [Use automatic dubbing — YouTube Help](https://support.google.com/youtube/answer/15569972?hl=en) *(primary; blocked, not read)* ·
[YouTube Blog: auto dubbing](https://blog.youtube/news-and-events/auto-dubbing-on-youtube/) ·
[YouTube Blog: expressive speech](https://blog.youtube/news-and-events/youtube-auto-dubbing-expressive-speech/) ·
[Metricool](https://metricool.com/youtube-multi-language-audio-tracks-now-available-for-more-creators/) ·
[sync. labs](https://sync.so/blog/youtube-auto-dubbing) ·
[eMarketer](https://www.emarketer.com/content/youtube-creators-now-dub-videos-eight-languages)

**Market CPM — weakest sources in this document:** [Upgrowth by country](https://upgrowth.in/youtube-cpm-by-country-global-comparison-2026/) ·
[Upgrowth by niche](https://upgrowth.in/youtube-cpm-overview-highest-paying-niches/) ·
[NoteLM](https://www.notelm.ai/blog/youtube-cpm-rates-2026) ·
[MilX](https://milx.app/en/cases/in-what-countries-cpm-are-the-highest) ·
[fluxnote](https://fluxnote.io/guides/youtube-earnings-by-country-comparison)
— aggregator estimates, not audited data. They agree on ordering and rough
magnitude; no individual figure should be treated as precise.

**Hebrew ASR (peer-reviewed):** [Building an Accurate Open-Source Hebrew ASR System through Crowdsourcing, Interspeech 2025](https://www.isca-archive.org/interspeech_2025/marmor25_interspeech.pdf) ·
[Bar-Ilan record](https://cris.biu.ac.il/en/publications/building-an-accurate-open-source-hebrew-asr-system-through-crowds/)
