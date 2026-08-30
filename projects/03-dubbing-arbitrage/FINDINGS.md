# 03 — Findings: the dubbing arbitrage does not hold up

**Date of investigation:** 2026-08-30
**Status:** verification attempted, **partially blocked** — see §1 before reading anything else.
**Recommendation: abandon this as a standalone direction.** Keep one narrow piece of it
as a free feature of projects 01/02. Reasoning in §7.

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

Two caveats that keep a narrow opening (both **unverified — see §8**):

1. **Topology.** "29 source languages → English" and "English → 20 languages" reads as
   hub-and-spoke through English. If so, **Hebrew → Spanish/Portuguese is not directly
   covered**, and those are precisely the large, higher-RPM finance audiences the brief
   targets. This single fact is the most decision-relevant unknown in the whole project.
2. **Quality.** YouTube's "Expressive Speech" — the mode that carries pitch, intonation and
   energy — covers 8 languages: English, French, German, Hindi, Indonesian, Italian,
   Portuguese, Spanish. **Hebrew is not among them.** The free Hebrew→English dub is
   therefore the flat-affect version, which matters for whether the output "sounds like a
   person" (brief task 3).

**Policy note, which is favourable:** auto-dubbing is YouTube's own first-party feature
applied to your own original upload. It sits on the safe side of the inauthentic-content line
by construction. Nothing in §3 creates strike risk.

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

**Abandon "dubbing arbitrage" as a standalone project.** The specific thesis — *a billing
loophole makes five languages cost the same as one, and that gap is the business* — does not
survive contact with the evidence:

1. The loophole appears not to exist at the named tools (§2).
2. Where the mechanic does exist, YouTube provides it **free**, first-party, and
   policy-safe (§3).
3. Even if the loophole were real, its value is ≈$22 per ten-minute video — too small to be a
   business (§4).
4. The pipeline's real risk is Hebrew ASR quality, which is a known weak point, sits upstream
   of everything else, and is untested (§5).

**What to keep instead — as a feature, not a project:**

Produce in Hebrew (projects 01/02), publish to YouTube, and **enable the free auto-dubbed
English track.** Cost: zero. Policy risk: zero, it is YouTube's own feature on your own
original content. Review each generated track before approving it — the approval gate is
exactly where Finding 5's number-mangling risk gets caught, and it is a human creative
judgement, which also keeps the output on the right side of the inauthenticity line.

Spend on a paid tool only if a specific measured need appears — most likely Hebrew→Spanish
or Hebrew→Portuguese, *if* §8's topology check confirms YouTube does not cover it. That is a
per-video purchase decision at ~$0.55–$5.50 per video, not a business model.

**Do not reallocate effort here from 01 or 02.** This project's stated dependency was that it
has "the least to say until there is content worth exporting." That remains true, and the
export step turns out to be free. The bottleneck was always the content, not the dubbing.

---

## 8. What would actually close the verification (if the direction is revisited)

Ordered by how much each would change the recommendation. **Item 1 alone could reopen the
project**; nothing else here can.

1. **Read `support.google.com/youtube/answer/15569972` directly.** Confirm the source/target
   topology. If Hebrew → Spanish/Portuguese is directly supported and free, this project is
   dead as a paid direction but the *outcome it wanted* is fully achieved at zero cost. If it
   is hub-and-spoke through English only, a narrow paid use case for those two languages
   survives. **This is one page and it decides the question.**
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

**On Hebrew ASR:**
- [Building an Accurate Open-Source Hebrew ASR System through Crowdsourcing — Interspeech 2025 (PDF)](https://www.isca-archive.org/interspeech_2025/marmor25_interspeech.pdf)
- [Same, Bar-Ilan University record](https://cris.biu.ac.il/en/publications/building-an-accurate-open-source-hebrew-asr-system-through-crowds/)
- [ASR Models and Word Error Rate: What Benchmarks Miss — Kili](https://kili-technology.com/blog/asr-models-guide-word-error-rate-benchmarks-and-failure-modes-2026)
