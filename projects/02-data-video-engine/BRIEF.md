# 02 — Sell the machine, not the videos

Read `../README.md` first for the shared asset inventory and constraints.

## The concept

Any business with a data feed wants a daily video and nobody wants to produce
one by hand. The pipeline shape — daily data → processing → automatic publish —
already exists in this repo for HTML. The same pipeline with MP4 as the output
is a product.

Candidate feeds: e-commerce (product of the day, restock, price drop), crypto
exchanges, sports fixtures and results, real estate listings, weather,
transit. Anything with rows that change daily.

The economics that make this the recommended direction: a median profitable
micro-SaaS runs around $4.2K MRR; the average is roughly $1,735 MRR at ~64%
margin. You sell a subscription, not a price per video, so you are not competing
against a $19/month tool or a $50 freelancer.

## Why it is not commodity work

Anyone can buy an AI ad generator. Almost nobody can wire a customer's live data
into a deterministic render that runs unattended every morning and never needs a
human. The moat is the integration and the reliability, not the pixels.

## Technical direction

Deterministic, code-driven rendering — **not** generative video. HTML/CSS
animation in headless Chromium, captured frame by frame, encoded with ffmpeg.
Reasons: it is free at the margin, it is reproducible, it renders text and
numbers correctly (generative models do not), and it stays clearly on the right
side of YouTube's inauthentic-content line because the output is a report on
real data rather than a template fill.

Generative clips from OpenArt are an optional garnish for b-roll, not the spine.

See `../README.md` for the verified ffmpeg setup — note the Playwright-bundled
binary is stripped and cannot encode h264.

## First task

Prove zero-marginal-cost daily rendering end to end, using Converge as the first
customer and its own data as the feed:

1. A parameterised HTML scene that takes a JSON payload and animates it.
2. A capture harness: headless Chromium, fixed frame rate, deterministic
   timing — no wall-clock dependence, so the same input always yields the same
   output.
3. ffmpeg encode to a vertical 9:16 MP4 with burned-in Hebrew text.
4. A single command that goes from JSON to finished file.

Measure and record: render time, output size, and cost (should be zero).
Everything produced stays in this folder.

## After the proof

Converge is customer zero and also the proof it works. Selling a pipeline you
have run daily against your own business for months is a fundamentally different
conversation from selling one you have never run.

## Watch out for

- Hebrew text rendering: RTL, font embedding, and line breaking in headless
  Chromium all need explicit checking, not assuming.
- Determinism: anything reading the clock, a random seed, or the network mid-
  render will make outputs unreproducible and undebuggable.
- Do not let this drift into a generic "AI video tool". The value is the data
  integration.
