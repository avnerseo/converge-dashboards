# 04 — Peluma: fix the margin before spending anything on video

Read `../README.md` first for the shared asset inventory and constraints.

This is the only workstream with a live business and real customers. It is also
the only one where **video is currently the wrong thing to work on.**

## Verified state (measured 2026-08-30, not assumed)

- Shopify store "Peluma", `pelumapets.com`, Basic plan, USD, Israel.
- Zendrop store id `3546333` (`hjahey-v0.myshopify.com`).
- Performance 2026-06-01 → 2026-08-30: **1 order, $29.90 revenue, $8.20 gross
  profit, 1 unit.** That is the entire sales history.
- Two products, both created days ago:

| product | created | price | variants | inventory |
|---|---|---|---|---|
| 3-in-1 Mist Grooming Brush | 08-26 | $29.90 (one variant $39.90) | 5 | stocked |
| 2-in-1 Paw Wash Cup | 08-29 | $16.90 | 8 | **0 — see below** |

Product images were generated with GPT Image 2, so an AI creative pipeline is
already partly in place.

## Finding 1 — the Paw Wash Cup shows zero inventory

`totalInventory: 0` and every variant reads `inventoryQuantity: 0`, while the
product status is ACTIVE. Depending on how the store handles out-of-stock, this
product may be unbuyable right now. **Check this first.** If it is unbuyable,
every other decision about it is moot. The Mist Brush by contrast carries
Zendrop's virtual stock (~50,000/variant), which is normal for dropshipping.

## Finding 2 — the margin cannot support paid advertising

From the single real sale: $29.90 revenue, $8.20 gross profit, so landed cost
is about $21.70. After Shopify payment fees (~2.9% + $0.30) the contribution is
roughly **$7.03 per order, about 23.5%**.

Typical CPA for pet accessories on Meta/TikTok is $18–35. Break-even is $7. Every
paid order loses money regardless of how good the creative is.

| line | today | at $39.90 | bundle at $54.90 |
|---|---|---|---|
| price | 29.90 | 39.90 | 54.90 |
| product + shipping | −21.70 | −21.70 | −32.70\* |
| payment fee | −1.17 | −1.46 | −1.89 |
| **contribution** | **7.03** | **16.74** | **20.31** |
| margin | 23.5% | 42.0% | 37.0% |
| max break-even CPA | $7 | $17 | $20 |

\* The Paw Cup's landed cost is **estimated** from the same cost ratio — there is
only one real data point in the entire business. Pull the actual Zendrop
per-variant cost before trusting any bundle number.

Note the $39.90 Milk Brown variant already exists, so raising the price is a
field edit, not a strategic leap.

## First task — no video, no credits

1. Resolve the Paw Wash Cup inventory state.
2. Pull real per-variant landed costs from Zendrop and replace the estimates
   above with measured numbers.
3. Recompute the table from real costs and decide pricing with the user. Do not
   change live prices without confirming — this is a real storefront.

## Second task — organic before paid

Pet content has the strongest organic reach in e-commerce. With no ad budget and
a thin margin, organic short-form is the realistic path to the first sales.
Paid traffic only after the margin work lands and something shows signal.

## When video does become the work

The weak spot of generative AI video is exactly what this product needs to show:
a brush actually misting fur, a paw actually going into a cup. Text-to-video
fails at that. The approach that works:

- **Supplier footage for the demo beat.** Zendrop/CJ usually provide product
  video — check what exists before generating anything.
- **AI for hooks, b-roll and scroll-stopping openers**, where realism of the
  mechanism does not matter.
- **Compose locally with ffmpeg** (see `../README.md` for the working binary).
  Zero marginal cost on assembly.

Budget guide from the shared inventory: a 20–25s ad is roughly 4 clips plus a
product still. At the cheap test tier (PixVerse V6, 540p) that is ~215 credits,
so the 10,000 available cover ~46 test ads. Test wide and cheap, then re-render
only proven winners at a higher tier.

## The discipline that matters

Creative volume is the top driver of paid performance, but only above a viable
margin. Do not let this project start producing videos before the contribution
per order clears roughly $17. Producing 46 ads for a business that loses money
on every order just loses money faster.
