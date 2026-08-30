# Verification request — what I need you to open, and what to answer

The container's egress allowlist blocks every dubbing vendor (see the egress
section in `../README.md`). I cannot read these pages. You can.

**Time needed: about 15 minutes.** Copy the form at the bottom, fill it in, paste
it back. Everything downstream — the cost model, the clip test, the go/no-go — is
waiting on these answers and nothing else.

---

## Ask Q1 first. It can end the project in 60 seconds.

> **Is Hebrew supported as a SOURCE language?**

Not as a *target* — every vendor lists Hebrew as a target because dubbing English
into Hebrew is the common direction. This project needs the opposite: Hebrew
audio going **in**. That is a different list and it is usually shorter.

If Hebrew is not a supported source at a vendor, that vendor is out and its
pricing does not matter. **Check this before reading anything else on the page.**
Look for a "supported languages" page or a dropdown in the product itself, and
check whether the source list and the target list are the same list.

---

## The pages, and the exact question on each

### 1. ElevenLabs
- **Where:** `elevenlabs.io/pricing` and `elevenlabs.io/docs/capabilities/dubbing`
- **Q1** Is Hebrew in the **source** language list for Dubbing?
- **Q2** Dubbing one video into 3 languages — does it cost 1× or 3×? The docs
  should state credits-per-minute; the question is whether that is multiplied by
  language count.
- **Q3** Creator tier: monthly price, and monthly credit allowance.
- **Q4** Credits per minute for: automatic *with* watermark, automatic *without*,
  Dubbing Studio *without*. (Reported as 2,000 / 3,000 / 10,000 — confirm.)

### 2. HeyGen
- **Where:** `heygen.com/pricing` and `help.heygen.com` → Video Translation
- **Q1** Is Hebrew in the **source** language list for Video Translate?
- **Q2** For a 5-minute video into 5 languages, how many billable minutes or
  credits? (Reported as ~25 billable minutes, i.e. per-language — confirm or
  refute. **This is the single most decision-relevant number in the request.**)
- **Q3** Entry paid tier: monthly price and credit allowance.
- **Q4** Credits/minute with lip-sync vs audio-only dubbing. (Reported 5 vs 2.)

### 3. Rask.ai
- **Where:** `rask.ai/pricing`
- **Q1** Is Hebrew in the **source** language list?
- **Q2** Does a 5-minute video into 3 languages consume 5 minutes or 15 minutes
  of the plan allowance? (Reported 15 — confirm or refute.)
- **Q3** Does lip-sync double the minutes consumed? (Reported yes.)
- **Q4** Entry paid tier: monthly price and minutes included.

### 4. YouTube Studio — the free baseline, and the one that matters most
- **Where:** your own YouTube Studio, or `support.google.com/youtube/answer/15569972`
- **Q1** With a Hebrew-language video, which auto-dub target languages does
  Studio actually offer? **Specifically: are Spanish and Portuguese offered, or
  only English?**
- **Q2** Is auto-dubbing enabled on the channel, and is there an approval step
  before a dubbed track goes live?

Q1 here decides whether a paid tool has any job at all. Published lists suggest
the routing is hub-and-spoke through English (everything → English, English → 20
languages), which would mean Hebrew → Spanish is *not* covered — but I could not
read the page, and what your Studio actually offers is more authoritative than
any list anyway.

---

## Fill-in form

```
DATE CHECKED:

--- ELEVENLABS ---
Hebrew as SOURCE language?        yes / no / couldn't find
Billing: per source minute or per target language?
Entry paid tier: $____/mo for ____ credits
Credits per minute (auto, no watermark): ____
URL(s) actually read:

--- HEYGEN ---
Hebrew as SOURCE language?        yes / no / couldn't find
5-min video x 5 languages = ____ billable minutes/credits
Entry paid tier: $____/mo for ____ credits
Credits/min lip-sync ____ , audio-only ____
URL(s) actually read:

--- RASK ---
Hebrew as SOURCE language?        yes / no / couldn't find
5-min video x 3 languages = ____ minutes consumed
Lip-sync doubles consumption?     yes / no
Entry paid tier: $____/mo for ____ minutes
URL(s) actually read:

--- YOUTUBE STUDIO ---
For a Hebrew video, auto-dub targets offered: ______________________
Spanish offered?    yes / no
Portuguese offered? yes / no
Approval step before a dubbed track goes live?   yes / no

--- ANYTHING THAT CONTRADICTED THE ABOVE ---
```

---

## If you would rather not do this

Reasonable — see `FINDINGS.md` §7. My recommendation does not depend on these
answers, and I say there why I think filling this in buys precision on a question
that no longer decides anything. It is here because the brief asks for it and
because the recommendation should be falsifiable: **if HeyGen or Rask turns out
to bill per source minute after all, that is a direct hit on §2 and I want to
know.** The answers that would most change my mind are HeyGen Q2 and YouTube Q1.
