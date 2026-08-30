# 03 — Produce in Hebrew, export to many languages

Read `../README.md` first for the shared asset inventory and constraints.

## The claimed mechanic — verify it before building on it

Reporting from mid-2026 says most AI dubbing tools bill **per source minute**,
regardless of how many target languages you request — Perso, HeyGen, Rask and
VEED are all described this way, with ElevenLabs the exception that bills each
target language separately.

If true, one Hebrew video becomes five languages for the price of one, and the
arbitrage is real. Quoted rates: roughly $0.10–3.00 per finished minute, with
entry paid plans around $0.55–2.40, against $5,000–15,000 per hour per language
for studio dubbing.

**Treat all of that as unverified.** It comes from vendor blogs and marketing
comparison pages, which have an obvious incentive to overstate. The first task
is to test it, not to assume it.

## Direction of the arrow

The common move is translating foreign content into Hebrew. The money is the
other way: **produce in Hebrew, export outward.** Hebrew is ~9M speakers;
English, Spanish and Portuguese finance audiences are orders of magnitude larger
with materially higher RPM.

Financial content is the ideal cargo — tickers, prices and percentages do not
change across languages. Only the narration does.

## Blocked: the verification cannot be done in this environment

Measured 2026-08-30. Container egress is allowlisted, and the dubbing vendors
are not on the list — `elevenlabs.io`, `www.heygen.com` and `www.rask.ai` all
return `connect_rejected`. `WebFetch` hits the same policy. See the egress
section in `../README.md`.

So reading vendors' real pricing pages and running a clip through their APIs are
both **impossible here as configured**, and `WebSearch` summaries are exactly the
secondhand marketing this project exists to distrust. Do not launder a search
result into a "finding".

Unblocking needs one of: the user widens the environment's network policy, or
the user performs the vendor steps manually and pastes results back.

## First task — everything that does not need the vendors

1. Write `FINDINGS.md` opening with the blocker stated plainly, and a precise
   **verification request for the user**: exactly which pages to open, and the
   exact question to answer on each (does billing count source minutes or target
   languages; what the per-minute rate is at the entry paid tier; whether Hebrew
   is a supported source language at all — check this, it is not guaranteed).
2. Build the cost model as a script parameterised by rate, languages and
   minutes, so confirmed numbers drop straight in. Include the break-even
   against studio dubbing.
3. Prepare the test asset locally: a 60–90s Hebrew source clip, segmented, with
   a transcript. ffmpeg works here (see `../README.md`).
4. Write the evaluation rubric **before** any output exists — transcription
   accuracy, naturalness, survival of financial terms and numbers, timing
   alignment — so the later judgement is not fitted to whatever comes back.

When vendor access exists, tasks become: run the clip, score it against the
rubric, record measured cost per finished minute against the claimed rate.

Write the result in this folder as `FINDINGS.md` — including a clear
recommendation to abandon the direction if the quality or the billing does not
hold up. A negative result here is a genuinely useful outcome and should be
reported as plainly as a positive one.

## Constraint

Whatever is produced has to clear YouTube's inauthentic-content line (see
`../README.md`). Dubbing your own original content into another language is
explicitly fine — it is AI assisting distribution of real work. Mass-producing
translated versions of *other people's* content is exactly what gets channels
removed. Stay on the first side of that line.

## Dependency

This project has the fastest path to revenue but the least to say until there is
content worth exporting. It pairs naturally with 01 (a verified scoreboard is
numbers, and numbers translate cleanly) and with 02 (which produces the videos).
Coordinate through this folder rather than assuming.
