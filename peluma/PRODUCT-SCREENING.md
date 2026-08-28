# Screening a product before it goes in the store

Written 28 Aug, after a full day was spent pricing, repricing and reverting a product that
Google Shopping would have disqualified in thirty seconds.

## The rule

**No product enters the store before it is screened.** Screening is free and takes minutes.
Adding a product costs description writing, SEO, images, variant setup, shipping profile work —
and then has to be undone if the product was never viable.

## Division of labour, established by testing rather than assumption

| Task | Who | Why |
|---|---|---|
| Pull names and costs from Zendrop's US catalog | **Merchant only** | `app.zendrop.com` returns `EGRESS_BLOCKED`, and it needs the merchant's own login. Verified, not assumed. |
| Market prices, reviews, competitor check | **Claude** | `WebSearch` runs server-side and works |
| Pass / fail decision | **Claude**, on numbers | |
| Building the product in the store | **Claude** | |

`WebFetch` is blocked for every domain outside Shopify — Amazon, Walmart, eBay, Temu and
Zendrop all return `EGRESS_BLOCKED`. `WebSearch` is the only external research tool available.

## What the merchant sends

1. Zendrop → **Find Products**
2. Filter **`Ships From: US`**
3. Search `pet`, `dog`, `cat`, `grooming`
4. Pick **6–8** candidates. Do not pre-filter — send too many, screening is free.
5. Open each, click **All SKUs**, screenshot
6. Send the screenshots. Typing is not needed.

Each screenshot needs to show: product name, the `app.zendrop.com/product/…` URL, product cost,
shipping cost, total, and average shipping time.

## The four screens, in order

**1. Commodity check — Google Shopping.**
Search the product. If Temu, AliExpress or Joom carry it at a small fraction of any workable
price, it is a commodity and it is dead. The brush failed here: Temu sells it at **$3.80–$4.10
with free shipping** against a $29.90 store price and a $17.42 landed cost.

**2. Review check.**
Search for complaints. Systemic defects — leaking, buttons breaking, mould, safety — mean a
return rate that eats the margin, and returns from overseas are close to a total loss. The
brush failed here too.

**3. Margin check.**
Landed cost against the price the market actually tolerates, minus roughly 8–9% in PayPal and
Shopify fees. Below about $12 net, it does not carry the cost of acquiring a customer.

**4. Basket fit.**
Does someone buying the existing product plausibly add this one? Same-supplier products ship in
one package, so the second item avoids a second shipping charge — that is where the margin
actually compounds. Worth asking Zendrop support which candidates share a supplier.

A product must pass all four. Expect most candidates to fail; that is the screen working.

## Standing instruction from the merchant

When something is needed from the merchant, it is written as numbered steps — where to click,
what to copy, what to send back — not as a general request. And before asking, check whether it
can be done without them, and say what was checked.

## Screen results so far

Applied to five candidates. All five failed on the margin screen (screen 3), and for the same
reason each time: the Zendrop landed cost lands at or above what the US market already charges.
Full numbers and sources in `DECISIONS.md`.

Two operational rules came out of it:

- **Screen out supplier 417 ("Amazon Products", US) before anything else.** Its prices are
  Amazon retail or higher, and it carries obvious data errors ($1.17 on a grooming vacuum
  listed in stock). Nothing there can be resold.
- **NexoraUSA (supplier 416) is the one US supplier priced like a supplier**, and it ships free
  in 6 days. It is still not cheap enough on commodity goods, but it is the only US source
  worth screening.

## Open item: the POD shipping number

This is the one number blocking the print-on-demand decision, and it is the only thing standing
between us and a product category that structurally escapes the price-comparison problem.

**Checked first, without the merchant** — none of these produced the number:

- `get_catalog_categories` on the Zendrop MCP — 200+ categories, no print-on-demand among them.
- `get_catalog_products` on the POD blank names — returns plain blanks from supplier 417, not
  the POD service.
- `get_catalog_shipping_estimate` — needs a catalog product id, and POD items have none.
- Zendrop's own help article on POD fulfilment costs — blocked by this environment's egress
  proxy, and per the search summary it gives no fixed rate anyway.

So it has to come from the dashboard. **Steps:**

1. Go to `app.zendrop.com` and sign in.
2. In the left sidebar, click **Print on Demand**.
3. Open the **Bella+Canvas 3001 Unisex Short Sleeve Tee** (base cost $11.69).
4. Click **Start designing** / **Create product** — any placeholder design is fine, this will
   not be published and nothing is charged.
5. Pick one variant: **Black, size L**.
6. Look for the pricing or shipping panel on that page and copy back:
   - the **base cost** for that variant,
   - the **shipping cost to the United States**,
   - the **estimated delivery time**,
   - and the **print location / country** if it is shown anywhere.
7. If no shipping figure appears on the product page, open the same screen for the
   **White Glossy Mug** ($7.95) and copy whatever cost lines it shows.
8. If neither page shows shipping, message Zendrop support with exactly this:

   > For print-on-demand orders shipped to the United States: what is the shipping cost for
   > one Bella+Canvas 3001 t-shirt, and for one white glossy mug? What does each additional
   > item in the same order add? Which country are POD orders printed and shipped from for a
   > US customer, and what is the production time before dispatch?

**Also worth asking in the same message**, since it is still open from the last exchange:
do print-on-demand orders count toward the 20 monthly orders required for a Private Agent?

With the shipping figure in hand the POD decision resolves immediately — the base costs are
already confirmed competitive, so shipping is the only variable left.

## POD base costs — verified from the dashboard (2026-08-28)

The merchant opened the Print-on-demand catalog, so these are read off Zendrop's own screens
rather than inferred. `Catalog > Women's clothing > All shirts > T-shirts`, page 1 of 3:

| Blank | Zendrop base | Colors | Note |
|---|---|---|---|
| Gildan 64000L (women's) | **$7.50** | 6 | cheapest quality blank in the catalog |
| Gildan 5000 | **$9.25** | 30 | |
| Gildan 64000 (unisex) | **$9.44** | 29 | industry-standard blank |
| Next Level 6210 CVC | $11.25 | 8 | |
| Gildan 8000 sports tee | $11.29 | 12 | |
| Bella+Canvas 6405CVC (women's V) | $15.25 | 4 | |
| Bella+Canvas 4810GD heavyweight | $16.49 | 1 | |
| Bella+Canvas 3005 V-neck | $17.09 | — | |
| Bella+Canvas 3413 tri-blend | $17.95 | 18 | |
| Comfort Colors 6030 pocket | $19.55 | 6 | |
| All-Over Print women's athletic | $32.10 | — | |
| All-Over Print boxy football jersey | $37.00 | — | |

Bella+Canvas 3001 was not on page 1; **Gildan 64000 at $9.44 is the working candidate** — most
colors, standard blank, good price.

These sit **below** Printify's and Printful's published base costs on comparable blanks. The POD
side of Zendrop is priced normally, unlike its dropship catalog. Confirmed again alongside the
earlier mug ($7.95 vs Printify $13.09) and poster ($6.50 vs $10.95) figures.

**Shipping is still the only unknown**, and it is not shown on the catalog grid — it appears
inside the design flow. Steps issued: `Start Design` on the $9.44 Gildan 64000, any placeholder
image, Black / L, continue to the pricing step, screenshot the cost breakdown.

## Which POD products actually fit this store

A grooming store selling plain t-shirts makes no sense. A product carrying **the customer's own
pet's photo or name** does, and it is the one thing that cannot be price-compared at all — the
design is the customer's. That is the whole reason POD survives the screen.

Ranked by fit, once shipping is known:

| Candidate | Base | Indicative retail |
|---|---|---|
| Mug with the pet's photo | $7.95 | $24.99 |
| Pillow / blanket with the pet's photo | $13.75 | $44.99 |
| Tee | $9.44 | $26.99 |

The mug and the pillow fit Peluma better than apparel. The tee is being measured first only
because it was the open screen; the shipping structure should carry across, and one real figure
lets all three be costed.

## POD verdict: Zendrop cannot do the product that would have worked

Checked before building anything, and it changes the answer.

**Zendrop POD is merchant-designed, fixed-listing only.** From their own documentation: you add a
design in their builder, it saves as a product, and that product is what sells. Their sourcing
article states plainly that *custom-made or fully personalized sourcing requests are not
supported*, and even branded thank-you cards are unavailable on POD items. Nothing in the
documentation describes per-order customer artwork.

That kills the one candidate that passed the margin test. The pillow/blanket only cleared the
screen **because** the design was the customer's own pet — that is what made it
price-incomparable and what justified $44.99. A generic printed blanket has neither property.

Sensitivity analysis, net after ~9% fees, across the whole plausible shipping range:

| Item | Base | Retail | ship $5 | ship $8 | ship $12 | ship $15 |
|---|---|---|---|---|---|---|
| Gildan 64000 tee | $9.44 | $26.99 | $10.12 | $7.12 | $3.12 | — |
| Mug | $7.95 | $24.99 | $9.79 | $6.79 | $2.79 | — |
| All-over print pillow | $13.75 | $44.99 | $26.19 | $23.19 | $19.19 | $16.19 |

Worth noting for its own sake: **the decision never actually depended on the missing shipping
number.** The tee and the mug fail at *every* value in the range — they never reach the ~$12 net
that screen 3 requires to carry a customer acquisition cost. Blocking on that number was a
mistake; the right move was to test whether the conclusion was sensitive to it, and it was not.

Per-order personalization does exist — Printify and Printful support it, via apps such as
Teeinblue or Customily, or by placing manual orders. That is a different supplier and a
different setup, and it is parked, not rejected.

## The actual bottleneck

Five products screened, two suppliers compared, a whole POD category investigated. All of it
sound, and none of it the thing standing between this store and revenue.

- The store is live, in English, US-targeted, checkout verified end to end, one real order through.
- Five variants are priced against verified market comparisons.
- **Nobody has ever visited it.**
- Pinterest — profile, 5 boards, 5 rendered 1000×1500 pins, all copy — has been ready and unshipped.

A new product is not the fast path to profit; it is more setup. Sending traffic to a store that
already works costs nothing, adds no supplier, no app and no reversible-decision risk, and
returns the one thing missing from every decision made this week: **real behaviour**. Product
choices after ~200 visitors rest on what people click, not on cost tables.

**Recommendation: park POD, ship Pinterest.** Revisit POD through Printify only if traffic shows
demand that the current margin cannot fund.

The five rendered pins are now committed at `peluma/pinterest-pins/` so they survive this
container; copy for each is in `PINTEREST.md`.
