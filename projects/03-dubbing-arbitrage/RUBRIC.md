# Evaluation rubric — written 2026-08-30, BEFORE any dubbed output exists

This exists so the later judgement cannot be fitted to whatever comes back. The
thresholds and the kill rule below are **frozen**. If a tool fails them, the tool
failed — the rubric does not get renegotiated after seeing the output.

If a threshold turns out to be wrong, change it *and say so explicitly in
`FINDINGS.md`*, with the reason and the date. Silent adjustment is the failure
mode this file prevents.

**Fixture:** `source_clip/` — Hebrew script, segmentation and ground truth.
**Scorer:** `tools/score.py` (mechanical parts) + human judgement where marked.

---

## The kill rule

> **Any error on any critical token fails the tool outright.**

Critical tokens are the 4 tickers and 12 numbers enumerated in
`source_clip/ground_truth.json`. Not a deduction — a fail.

Rationale: for financial content a wrong number is worse than no video. A
confidently-narrated "110 billones" where the source said מאה ועשרה מיליארד is a
1000× error delivered in a voice that sounds authoritative. No amount of
downstream naturalness repairs it, and the audience has no way to detect it.
A tool that cannot be trusted with the numbers cannot carry this cargo, which
was the entire premise of the direction.

This rule is why the fixture is loaded with scale-word traps rather than being a
neutral sample. See the `trap` fields in the ground truth.

---

## Dimension 1 — Hebrew source transcription

The gate for everything downstream. If the Hebrew ASR is wrong, translation and
voice faithfully reproduce the error.

| | Threshold |
|---|---|
| Word error rate vs. ground truth | **< 10%** |
| Errors on critical tokens | **0** (kill rule) |
| Gender agreement forms preserved | all 4 (see ground truth) |

Scored mechanically by `tools/score.py` after normalisation (niqqud stripped,
punctuation dropped, Hebrew number-words mapped to digits). The normaliser is
part of the fixture, not written after the fact.

**Note:** if a vendor does not expose its intermediate Hebrew transcript, this
dimension cannot be scored directly and must be inferred from the output. Record
that limitation rather than skipping the dimension.

---

## Dimension 2 — Financial term and number survival

Per target language, over the 16 critical tokens.

| | Threshold |
|---|---|
| Numeric values correct | **100%** |
| Locale formatting correct | 100% — decimal separator, currency position, scale word |
| Tickers resolve to the real symbol | 100% — `אן־וי־די־איי` → `NVDA`, not `NVDA` misheard as a word |

The two scale traps (`טריליון`, `מיליארד`) are the highest-value cases in the
fixture. Spanish is chosen as the second target language specifically because
`billón` = 10¹² there, so a lazy cognate mapping produces a 1000× error that an
English-only test would never surface.

---

## Dimension 3 — Naturalness

Human judgement, not mechanical. Ask one question and answer it honestly:

> Played to a stranger who does not know it is dubbed, would they flag it as
> synthetic within the first 20 seconds?

| Verdict | Meaning |
|---|---|
| Pass | Would not flag it. Publishable. |
| Marginal | Sounds processed but not obviously machine. Publishable only with disclosure. |
| Fail | Obviously synthetic. Not publishable — see the YouTube constraint in `../README.md`. |

Record the verdict for **each** target language separately. Vendors' quality is
not uniform across languages, and English performance says nothing about Spanish.

**Bias control:** decide the verdict before looking at the price. A cheap tool
does not get graded on a curve.

---

## Dimension 4 — Timing alignment

Hebrew and English differ in length for the same content, so dubbed audio drifts
against on-screen visuals. This is the dimension most likely to be quietly
broken and least likely to be advertised.

| | Threshold |
|---|---|
| Drift at the 60s mark | **< 300ms** |
| Segment boundary drift | < 300ms at every one of the 6 segment boundaries |
| Audible truncation or unnatural compression | none |

Measured against the segment boundaries in `source_clip/ground_truth.json`.
Note whether the tool achieved alignment by *compressing speech* (audible, bad)
or by *rewriting for length* (good, but check the numbers survived the rewrite —
this is a common place for the kill rule to trip).

---

## Dimension 5 — Cost actually charged

Not a quality dimension; the one that answers brief task 4.

1. Note the account's credit balance before the run.
2. Dub the fixture into **one** language. Note the balance.
3. Dub the same fixture into a **second** language. Note the balance.
4. If step 3 costs the same as step 2, billing is per target language. If step 3
   is free, billing is per source minute and the brief's claim holds.

That single comparison settles the project's founding question empirically, in
about five minutes, and does not depend on reading any pricing page correctly.
Record the measured $/finished minute and feed it to `tools/cost_model.py --rate`.

---

## Overall verdict

A tool **passes** only if it clears **all** of: kill rule, dimensions 1, 2 and 4
thresholds, and Pass or Marginal on dimension 3 — **for every target language
tested**, not on average.

Passing on English and failing on Spanish is a **fail**, recorded as such. The
whole thesis is multi-language export; a tool that only works into English is
competing against YouTube's free English dub and loses on price.
