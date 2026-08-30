# Handoff — Peluma economics → the store's owning session

**Status: workstream 04 is closed.** It was opened without checking what was
already running, and duplicated an older session (`Peluma Shopify theme
testing`, branch `claude/peluma-theme-handoff-ts6y95`) that built the store and
holds two days of context on it. Two agents writing to one live storefront is
how things break silently, so the store stays with that session. This file is
what 04 produced, handed over. `BRIEF.md` beside it stays as reference.

## Needs checking first — 04 wrote to the live store

Before anything else: 04 reported **"Israeli shipping profiles fixed."** It
changed shipping configuration on the live store, not just read it. Verify that
change against what the theme/setup work had already configured. It may be a
genuine fix or it may have overwritten a deliberate setting — 04 did not know
what the earlier session had set up, because it had none of that context.

04 never pushed its branch, so its detailed working notes are only in its own
(now archived, still readable) transcript. The Shopify-side changes are live
regardless.

## The finding worth keeping

From the single recorded sale (2026-06-01 → 08-30: 1 order, $29.90 revenue,
$8.20 gross profit), landed cost is about $21.70. After payment fees
(~2.9% + $0.30) contribution is roughly **$7.03 per order, about 23.5%**.

Typical CPA for pet accessories on Meta/TikTok is $18–35. Break-even is $7.
**Paid advertising loses money on every order at current pricing, regardless of
creative quality.**

| line | today | at $39.90 | bundle at $54.90 |
|---|---|---|---|
| price | 29.90 | 39.90 | 54.90 |
| product + shipping | −21.70 | −21.70 | −32.70\* |
| payment fee | −1.17 | −1.46 | −1.89 |
| **contribution** | **7.03** | **16.74** | **20.31** |
| margin | 23.5% | 42.0% | 37.0% |
| max break-even CPA | $7 | $17 | $20 |

\* Estimated, not measured — see below.

The $39.90 Milk Brown variant already exists, so raising the price is a field
edit rather than a strategic leap.

## What is NOT verified — do not treat these as facts

- **The Paw Cup's landed cost is a guess**, derived from the Mist Brush's cost
  ratio. There is exactly one real sale in the entire business, so every bundle
  number above is built on one data point. Pull real per-variant landed costs
  from Zendrop before acting on the bundle column.
- **Paw Wash Cup inventory.** It read ACTIVE with `totalInventory: 0` and every
  variant at 0 on 2026-08-30. It may not be purchasable. 04 was checking this
  when it closed; the result did not reach git. Re-check it.
- CPA ranges are industry estimates, not measured for this store.

## The open decision

Pricing. It needs the real costs first, then a call from the owner. Nothing
should change on a live storefront without that.

## The gate that matters

**No video production until contribution per order clears roughly $17.**

This project began as a question about video, and without an explicit gate the
work drifts there naturally. Producing 46 test ads for a business that loses
money on every order only loses money faster. Creative volume is the top driver
of paid performance — but only above a viable margin.

When the gate is cleared, the approach is in `BRIEF.md`: supplier footage for
the demo beat (generative video cannot show a brush actually misting fur),
AI for hooks and b-roll, assembly locally with ffmpeg at zero marginal cost.
Budget guide: ~215 credits per test ad at the cheap tier, so the 10,000 OpenArt
credits cover roughly 46 of them.
