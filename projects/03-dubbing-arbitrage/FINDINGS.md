# 03 — Findings: the dubbing arbitrage does not hold up

**Date of investigation:** 2026-08-30
**Status:** verification attempted, **partially blocked** — see §1 before reading anything else.
**Recommendation: abandon this as a standalone direction.** Keep one narrow piece of it
as a free feature of projects 01/02. Reasoning in §7.

> **Second pass, same day.** Two open unknowns from the first pass were closed (§3B, §3C).
> Both closed against the project. The RPM premise the whole direction rests on turns out to
> be **backwards** for Spanish and Portuguese. The recommendation is now firmer, and — see
> §7 — it no longer depends on the pricing-page verification that was blocked.

---

## 1. What I could not do, and why — read this first

The brief's first task was to read the **actual current pricing pages**, not summaries of
them, and then to push a real Hebrew clip through two tools. **Neither was possible in this
environment.** I am stating this plainly rather than substituting blog summaries and calling
it verification, because substituting summaries is the exact failure the brief warned about.

**Outbound network egress is closed for this session.** Every vendor domain returns
`EGRESS_BLOCKED` from the policy proxy:

| Domain attempted | Result |
|---|---|
| `elevenlabs.io` (pricing + `/docs/capabilities/dubbing`) | EGRESS_BLOCKED |
| `www.heygen.com/pricing`, `docs.heygen.com` | EGRESS_BLOCKED |
| `www.rask.ai/pricing` | EGRESS_BLOCKED |
| `www.veed.io/pricing` | EGRESS_BLOCKED |
| `perso.ai/pricing` | EGRESS_BLOCKED |
| `www.kapwing.com/pricing` | EGRESS_BLOCKED |
| `support.google.com` (YouTube auto-dubbing help) | EGRESS_BLOCKED |
| `api.elevenlabs.io` | EGRESS_BLOCKED |
| `en.wikipedia.org` (control test) | EGRESS_BLOCKED |

The Wikipedia control confirms this is a blanket egress policy, not a vendor-specific block.
Per the proxy documentation this is an organization policy denial that must be reported, not
routed around.

**A local Hebrew-ASR measurement was also attempted and is not possible.** PyPI *is*
reachable (`faster-whisper` installs fine), but every source of model weights or Hebrew
speech data is blocked: `huggingface.co`, `hf-mirror.com`,
`openaipublic.azureedge.net` (Whisper's own weight CDN) and `commonvoice.mozilla.org` all
return 403 at the tunnel. So even the one risk that could have been measured without a
vendor account — §5's Hebrew word error rate — cannot be measured here.

**There are also no credentials.** No `ELEVENLABS_*`, `HEYGEN_*`, `RASK_*` or any other
dubbing-service key exists in the environment. Even with egress open, tasks 2–4 need paid
accounts that do not exist yet.

**Therefore:**

| Brief task | Status |
|---|---|
| 1. Read actual pricing pages | ❌ Blocked. Substituted with clearly-labelled secondary evidence (§2). |
| 2. Run a Hebrew clip through two tools | ❌ Blocked. No egress, no accounts. **Not attempted, not simulated.** |
| 3. Judge transcription / naturalness / numbers / timing | ❌ Blocked — depends on task 2. |
| 4. Measured cost per finished minute | ❌ Blocked. §4 gives *modelled* cost from secondary figures, explicitly not measured. |

**Everything below §2 is secondary-source evidence at "moderate" confidence at best.** It is
consistent enough across independent sources to act on directionally, and it is enough to
support a recommendation — but it is not the primary-source verification the brief asked for.
§8 specifies exactly what would close the gap.

---

## 2. Finding 1 — the per-source-minute claim appears to be **false** for the tools named

The brief's load-bearing premise: *"most AI dubbing tools bill per source minute, regardless
of how many target languages you request — Perso, HeyGen, Rask and VEED are all described
this way, with ElevenLabs the exception."*

Secondary sources say the opposite, with concrete arithmetic, for two of the four:

**HeyGen — bills per target language.**
> "HeyGen's translations bill by source duration, where a 5-minute video × 5 languages = ~25
> billable minutes."

The stated rates are 2 credits/min for audio-only dubbing and 5 credits/min with lip-sync,
**multiplied by the number of target languages**. Max 10 languages per job.

**Rask.ai — bills per target language.**
> "A 5-minute video dubbed into Spanish, French, and German consumes 15 minutes, not 5. This
> pattern is consistent across all pricing tiers."

And lip-sync doubles it again: the same 3 languages with lip-sync consumes 30 minutes.

**ElevenLabs — per language, as the brief already expected.** Quoted at 2,000 credits/min
(automatic, watermarked) / 3,000 (automatic, unwatermarked) / 5,000 (Dubbing Studio,
watermarked) / 10,000 (Dubbing Studio, unwatermarked), with each target language a separate
dubbing job consuming credits accordingly.

**Perso and VEED — not established.** Perso's own domain is blocked and I found no
independent statement of their multi-language consumption model. Note that several of the
"comparison" pages that surface on this topic are **published by Perso and by HeyGen
themselves** — i.e. the vendor-incentive problem the brief flagged is not hypothetical; it is
visibly present in the top search results for these queries.

### Verdict on Finding 1

**Refuted, at moderate confidence, for HeyGen and Rask. Confirmed as expected for ElevenLabs.
Unresolved for Perso and VEED.** The "five languages for the price of one" mechanic does not
appear to exist at the two tools most likely to be used. The most probable origin of the
original claim is a misreading of the phrase *"billed by source duration"* — which means
"we measure the source, not the output" (a real and useful distinction: a 5-minute Hebrew
clip that becomes 6 minutes of English audio still bills as 5), **not** "we charge once
regardless of language count." Those are different claims and the marketing copy blurs them.

---

## 3. Finding 2 — the bigger problem: YouTube now gives this away for free

This is the finding that actually decides the project, and the brief did not account for it.

As of early 2026, **YouTube auto-dubbing is available to all creators, free, and on by
default for eligible channels.** As of July 2026 it dubs **into English from 29 source
languages**, and **from English into 20 languages**. Creators can preview, approve, reject or
hold each generated track.

**Hebrew is one of the supported source languages into English.**

So the exact mechanic this project was built to sell — take a Hebrew video, get an English
audio track on it — is a free platform feature on the platform this project targets. There is
no arbitrage to capture where the platform has already zeroed the price.

Two caveats that looked like a narrow opening:

1. **Topology.** "29 source languages → English" and "English → 20 languages" reads as
   hub-and-spoke through English — if so, Hebrew → Spanish/Portuguese is not covered.
   **Resolved in the second pass: confirmed hub-and-spoke (§3B). But §3C shows the uncovered
   routes are the ones not worth buying.**
2. **Quality.** YouTube's "Expressive Speech" — the mode that carries pitch, intonation and
   energy — covers 8 languages: English, French, German, Hindi, Indonesian, Italian,
   Portuguese, Spanish. **Hebrew is not among them.** The free Hebrew→English dub is
   therefore the flat-affect version, which matters for whether the output "sounds like a
   person" (brief task 3).

**Policy note, which is favourable:** auto-dubbing is YouTube's own first-party feature
applied to your own original upload. It sits on the safe side of the inauthentic-content line
by construction. Nothing in §3 creates strike risk.

---

## 3B. Finding 2b — the free/paid split falls exactly on the wrong side

Second pass closed the topology question from §3. YouTube's published language lists:

- **Into English, from 29 source languages** — Chinese, Dutch, French, German, **Hebrew**,
  Hindi, Indonesian, Italian, Japanese, Korean, Malayalam, Polish, Portuguese, Punjabi,
  Romanian, Russian, Spanish, Swahili, Tamil, Telugu, Thai, Turkish, Ukrainian, Urdu,
  Vietnamese, …
- **From English, into 20 languages** — Arabic, Bengali, Dutch, French, German, **Hebrew**,
  Hindi, Indonesian, Italian, Japanese, Korean, Malayalam, Polish, Portuguese, Punjabi,
  Russian, Spanish, Tamil, Telugu, Ukrainian.

The topology is **hub-and-spoke through English**, as suspected. So:

| Route | Free on YouTube? |
|---|---|
| Hebrew → English | ✅ Yes |
| English → Hebrew | ✅ Yes |
| **Hebrew → Spanish** | ❌ **No** |
| **Hebrew → Portuguese** | ❌ **No** |

This is what a first pass would call the opening: Spanish and Portuguese are not covered, so
a paid tool has a job. **§3C shows that job is not worth doing.**

---

## 3C. Finding 2c — the RPM premise is backwards

The brief's economic engine: *"Hebrew is ~9M speakers; English, Spanish and Portuguese
finance audiences are orders of magnitude larger with **materially higher RPM**."*

The second half is false for two of the three languages. CPM by market, two independent
secondary sources agreeing:

| Market | CPM | vs. Israel |
|---|---|---|
| United States (English) | $32.75 | **2.3× higher** |
| **Israel (Hebrew) — the starting point** | **$14.08** | — |
| Spain (Spanish) | $14.22 | ≈ parity |
| Portugal (Portuguese) | $10.32 | 0.7× |
| Mexico (Spanish) | $2–8 | 0.1–0.6× |
| Brazil (Portuguese) | $1.64–2.00 | **0.1× — 7–9× lower** |
| *Blended Spanish* | ≈$3.00 | **0.2×** |
| *Blended Portuguese* | ≈$2.00 | **0.14×** |

**Israel is a high-CPM market** — $14.08, top of tier 1-2, on par with Spain and ahead of
Portugal, driven by domestic tech/B2B/SaaS advertiser demand. The brief treated Hebrew as the
low-value origin to escape from. It is not.

And the blended figures are the ones that matter, because **you select a language, not a
country.** Dubbing to Spanish delivers you mostly to Latin America, not Spain; dubbing to
Portuguese delivers you to Brazil, which is ~95% of Portuguese-language YouTube volume at
$1.64 CPM. The high-CPM European tail is not addressable separately.

Put §3B and §3C together and the result is stark:

> **The one export route that pays more than the home market — English, 2.3× — is the exact
> route YouTube dubs for free. Every route you would have to pay a vendor for delivers into
> markets whose CPM is 5–9× *below* the Hebrew market you started in.**

The arbitrage is inverted. You would be paying money to move content from a $14 market into a
$2 market.

**The honest counter-argument, and why it does not rescue the project:** revenue is views ×
CPM, and Spanish has ~55× more speakers than Hebrew at ~0.21× the CPM — a theoretical ~11×
ceiling *if penetration were equal*. It will not be. In Hebrew finance you would be a
domestic voice in a thin, underserved niche. In Spanish finance you would be an unknown
channel with a synthetic voice competing against native creators in one of the most saturated
content markets on earth, unable to read your own comments. The thesis quietly changes from
"same content, higher RPM" to "same content, far lower RPM, betting on volume in the hardest
competitive market available." That is not the bet the brief described, and it is a much
worse one.

---

## 4. Finding 3 — the billing question was never the load-bearing one

Even taking the *unfavourable* per-language model as true, the arbitrage math barely moves.
Modelled from the secondary figures above (**modelled, not measured**):

Assume ElevenLabs Creator at $22/mo for 121,000 credits, automatic dubbing without watermark
at 3,000 credits/min → ≈40 minutes/month → **≈$0.55 per finished minute per language.**

| Scenario, 10-minute Hebrew source → 5 languages | Cost |
|---|---|
| Claimed model ("price of one") | ≈ $5.50 |
| Actual model (per target language) | ≈ $27.50 |
| **Penalty for the claim being wrong** | **≈ $22** |
| Studio dubbing, same job ($5k–15k/hr/language) | $4,165 – $12,500 |

The claim being false costs about **$22 per ten-minute video**. AI dubbing remains roughly
**150–450× cheaper than studio** *even under the per-language model*. Note also that the
brief's own quoted entry rate of "$0.55/minute" matches the per-language figure almost
exactly — the low end of the quoted range was already the per-language price.

**So: refuting Finding 1 does not, by itself, kill this project.** A 5× multiplier on an
input that costs tens of dollars is not what determines whether a content business works.
Distribution, retention and whether anyone watches the dubbed track determine that. The brief
put the weight on the wrong variable. What actually kills the project is §3 (the price is
zero at the platform) combined with §5 (the input quality is the real risk).

---

## 5. Finding 4 — Hebrew-as-source is the weak link, and it is the untested one

The direction-of-the-arrow argument is right that Hebrew→outward is the underserved
direction. It is also, for the same reason, **the direction these tools are worst at.** Every
one of them is built and benchmarked on English→X. Hebrew→X inverts that.

The entire pipeline is gated on the first step: Hebrew ASR. If the Hebrew transcript is
wrong, translation, voice and timing all faithfully reproduce the error.

Hebrew is a documented low-resource ASR case. A 2025 Interspeech paper from Bar-Ilan built a
314-hour crowdsourced Hebrew corpus specifically because *"Hebrew still lacks robust
open-source solutions"* given *"limited resources and rich morphology."* Their Hebrew-specific
Whisper model achieves **up to a 29% error-rate reduction versus existing Whisper solutions**
— which is another way of saying stock Whisper, the engine underneath most of these dubbing
products, has materially elevated Hebrew WER. Whisper's own paper reports WER correlating
with training hours at r²=0.83, halving per 16× more data; Hebrew sits far down that curve.

**Specific risks to the "numbers survive translation" premise — all untested:**

- Hebrew number morphology is gendered and irregular (שתי / שניים / שתיים), and construct
  forms shift with context. These are exactly the forms ASR degrades on.
- Scale words do not map cleanly: מיליארד → "billion" is fine for US English, but the
  European "milliard" sense and Hebrew טריליון usage need checking per target language.
- Ticker symbols spoken in Hebrew (e.g. "אנבידיה", or Latin letters read aloud) are a known
  ASR failure class and will not round-trip to "NVDA."
- Percentages, currency order (₪/$ before or after), and decimal separators differ by locale.

The brief asserts that financial content is ideal cargo *because* numbers do not change
across languages. **That premise is plausible but unverified, and the failure modes above are
concentrated precisely where the brief assumes safety.** Testing it was task 3, and task 3
was blocked.

---

## 6. Finding 5 — an unconsidered risk introduced by the direction of the arrow

`../README.md` flags Israeli investment-advice law (חוק הסדרת העיסוק בייעוץ השקעות) as the
regulatory constraint. Exporting Hebrew financial content **outward** does not escape that —
it *adds* to it. Content published in English, Spanish or Portuguese and targeted at those
audiences may engage the financial-promotion regimes of those jurisdictions (US, UK, EU) in
addition to the Israeli one. Dubbing multiplies regulatory surface at the same rate it
multiplies audience.

This does not block anything today, and I have not researched those regimes. It belongs in
the same lawyer conversation project 01 already needs, and should not be discovered later.

---

## 7. Recommendation

**Abandon "dubbing arbitrage" as a standalone direction. Buy nothing.** The thesis — *a
billing loophole makes five languages cost the same as one, and that gap is the business* —
fails at four independent points, any one of which is sufficient:

1. **The loophole does not exist** at the named tools. HeyGen and Rask both bill per target
   language, with explicit arithmetic (§2).
2. **Where the mechanic does exist, YouTube gives it away** — free, first-party,
   policy-safe, Hebrew supported as a source language (§3).
3. **The free/paid split falls exactly wrong.** The only route that pays more than the home
   market (→English, 2.3×) is the free one. Every payable route (→Spanish, →Portuguese)
   lands in markets with 5–9× *lower* CPM than Israel's $14.08 (§3B, §3C). **The arbitrage
   runs backwards.**
4. **Even if all of the above were favourable**, the loophole is worth ≈$22 per ten-minute
   video (§4) — too small to be a business — and the pipeline's real risk is Hebrew ASR
   quality, a documented low-resource weak point sitting upstream of everything (§5).

Point 3 is the one that ends it. Points 1, 2 and 4 make the project small; point 3 makes it
value-destroying.

**What to keep — a checkbox, not a project:**

When project 01/02 ships its first Hebrew video, upload it and **enable the free auto-dubbed
English track**, then review the track before approving it. Cost: $0. Policy risk: none — it
is YouTube's own feature on your own original content, and the manual approval step is both
the quality gate for §5's number-mangling risk and the human creative judgement that keeps
the output clear of the inauthenticity line. That single checkbox captures essentially all
the realizable value this project was chartered to find.

**What to do about Spanish and Portuguese: nothing, for now.** Revisit only if the Hebrew
channel is already working and the English track is measurably pulling non-Israeli watch
time. At that point the question is no longer "is dubbing cheap" but "can we win in a
saturated market we cannot read," which is a different decision requiring different evidence.

**Do not reallocate effort here from 01 or 02.** The brief called this "the fastest path to
revenue." It is not — it is a $0 feature of whatever 01 and 02 produce. The bottleneck was
always the content, and it still is. If anything, §3C argues the *opposite* of the brief's
framing: Israel at $14.08 CPM against a finance niche paying $15–50 is a market worth serving
directly in Hebrew, not one to escape.

## 8. What would actually close the verification (if the direction is revisited)

**Important: none of this is now worth doing.** The recommendation in §7 rests on §3B and
§3C, which are about YouTube's language topology and market CPMs — *not* about vendor
pricing. Perfect primary-source pricing data would not change the conclusion. Unblocking
egress and buying an account to complete brief tasks 1–4 would buy precision on a question
that no longer decides anything. This section is recorded so the work is reproducible if the
direction is ever revisited on new evidence.

~~Item 1 (YouTube topology)~~ — **done in the second pass, see §3B.** Answer: hub-and-spoke
through English; Hebrew → Spanish/Portuguese is not free.

2. **Read the four vendor pricing pages directly** (elevenlabs.io/pricing,
   heygen.com/pricing, rask.ai/pricing, veed.io/pricing) plus each one's billing/FAQ doc.
   Look specifically for the phrase distinguishing *"billed by source duration"* from
   *"charged per target language"* — §2 argues the original claim came from conflating them.
3. **Run the clip test** (brief task 2), which needs egress + one paid account. Protocol,
   ready to execute:

   - **Source:** 60–90s Hebrew financial narration, deliberately loaded with the §5 failure
     modes: at least 4 tickers spoken in Hebrew, 3 large-scale numbers (מיליארד/טריליון),
     3 percentages with decimals, and one gendered-number construction.
   - **Write the ground-truth transcript before dubbing.** Without it, step 3 is vibes.
   - **Targets:** English + Spanish (Spanish, not a second European language — it is the
     actual target audience and it exercises a different number-formatting locale).
   - **Tools:** YouTube auto-dub (the free baseline — any paid tool must beat it, and the
     brief's comparison against *studio* dubbing is the wrong benchmark) and ElevenLabs
     (best-documented billing, so measured-vs-claimed cost is checkable).
   - **Score, per output, against the ground truth:**
     | Dimension | Pass condition |
     |---|---|
     | Hebrew ASR | Ground-truth WER < 10%; **zero errors on digits and tickers** |
     | Number survival | 100% of numeric values correct and locale-correctly formatted |
     | Naturalness | Blind A/B vs. a human read; would a stranger flag it as synthetic? |
     | Timing | Drift < 300ms at the 60s mark against on-screen chart cues |
   - **Kill rule, set in advance:** any digit or ticker error in the Hebrew ASR fails the
     tool outright. For financial content a wrong number is worse than no video, and no
     amount of downstream voice quality repairs it.
   - **Record actual credits consumed** for 1 language vs 2, from the account's usage page.
     That single comparison settles §2 empirically in about five minutes.

---

## 9. Sources

All secondary. Vendor primary pages were unreachable (§1). Retrieved 2026-08-30 via search;
snippets only, full pages not fetchable.

**On per-language billing:**
- [HeyGen pricing (2026): plans, credits, and what you'll actually pay — eesel AI](https://www.eesel.ai/blog/heygen-pricing)
- [HeyGen Video Translation Guide 2026 — fluxnote.io](https://fluxnote.io/guides/heygen-video-translation-guide)
- [How to Get Started with Video Translation — HeyGen Help Center](https://help.heygen.com/en/articles/10029081-how-to-get-started-with-video-translation)
- [Rask AI Pricing in 2026: Plans, Cost per Minute, Alternatives — geckodub](https://www.geckodub.com/en/blog/rask-ai-pricing-plans-alternatives)
- [Rask AI Pricing Breakdown: Plans, Costs & Alternatives (2026) — geckodub blog](https://blog.geckodub.com/rask-ai-pricing-plans-alternatives)
- [ElevenLabs AI Dubbing Pricing: The Full 2026 Breakdown — geckodub blog](https://blog.geckodub.com/elevenlabs-ai-dubbing-pricing)
- [The Complete Guide to ElevenLabs Plans, Overages, and Usage-Based Pricing in 2026 — Flexprice](https://flexprice.io/blog/elevenlabs-pricing-breakdown)
- [ElevenLabs Pricing (2026) — BIGVU](https://bigvu.tv/blog/elevenlabs-pricing-2026-plans-credits-commercial-rights-api-costs/)

⚠️ Vendor-published comparison pages encountered in these results — treat as marketing:
[Perso on Rask AI](https://perso.ai/blog/rask-ai-dubbing-review-2026-features-pricing-how-it-compares),
[HeyGen vs Rask vs Maestra vs Kapwing (published by HeyGen)](https://www.heygen.com/blog/heygen-vs-rask-ai-vs-maestra-vs-kapwing).

**On YouTube auto-dubbing:**
- [Use automatic dubbing — YouTube Help](https://support.google.com/youtube/answer/15569972?hl=en) *(primary source; blocked, not read)*
- [YouTube Auto-Dubbing: Now Available to All Creators — Metricool](https://metricool.com/youtube-multi-language-audio-tracks-now-available-for-more-creators/)
- [How YouTube auto dubbing works, and its limits — sync. labs](https://sync.so/blog/youtube-auto-dubbing)
- [YouTube Auto Dubbing: Who Has It, How to Disable, & More — BeMultilingual](https://www.bemultilingual.ca/blog/youtube-auto-dubbing)
- [YouTube creators can now dub videos in eight languages — eMarketer](https://www.emarketer.com/content/youtube-creators-now-dub-videos-eight-languages)

**On monetization of dubbed tracks:**
- [Can Multi-Audio Tracks Change YouTube RPM and CPM? — MilX](https://milx.app/en/cases/can-adding-new-language-reset-a-youtube-monetization-algorithm)
- [A Creator's Guide to YouTube's Multi-Language Audio Feature — RWS](https://www.rws.com/blog/youtube-multi-language-audio-guide/)

**On the YouTube language topology (§3B):**
- [Break down language barriers with auto dubbing on YouTube — YouTube Blog](https://blog.youtube/news-and-events/auto-dubbing-on-youtube/)
- [Unlocking a global audience with auto dubbing (Expressive Speech) — YouTube Blog](https://blog.youtube/news-and-events/youtube-auto-dubbing-expressive-speech/)
- [YouTube auto dubbing: what it is, on or off — TimedSubs](https://timedsubs.com/en/guides/youtube-auto-dubbing)

**On market CPM (§3C) — two independent sets, in agreement on Israel and Brazil:**
- [YouTube CPM by Country 2026: Top 20 Markets Ranked — Upgrowth](https://upgrowth.in/youtube-cpm-by-country-global-comparison-2026/)
- [YouTube CPM Overview 2026: Highest Paying Niches — Upgrowth](https://upgrowth.in/youtube-cpm-overview-highest-paying-niches/)
- [YouTube CPM Rates 2026: $0.50-$50 by Country & Niche — NoteLM](https://www.notelm.ai/blog/youtube-cpm-rates-2026)
- [Countries with the highest YouTube CPM in 2026 — MilX](https://milx.app/en/cases/in-what-countries-cpm-are-the-highest)
- [YouTube Earnings by Country 2026 — fluxnote](https://fluxnote.io/guides/youtube-earnings-by-country-comparison)
- [How much does YouTube pay in different languages — MilX](https://milx.app/en/trends/how-much-does-youtube-pay-in-different-languages)

⚠️ CPM figures are aggregator estimates from SEO-driven sites, not audited data. They agree
across sources on the ordering and the rough magnitudes, which is what §3C's argument
depends on; do not treat any individual dollar figure as precise.

**On Hebrew ASR:**
- [Building an Accurate Open-Source Hebrew ASR System through Crowdsourcing — Interspeech 2025 (PDF)](https://www.isca-archive.org/interspeech_2025/marmor25_interspeech.pdf)
- [Same, Bar-Ilan University record](https://cris.biu.ac.il/en/publications/building-an-accurate-open-source-hebrew-asr-system-through-crowds/)
- [ASR Models and Word Error Rate: What Benchmarks Miss — Kili](https://kili-technology.com/blog/asr-models-guide-word-error-rate-benchmarks-and-failure-modes-2026)
