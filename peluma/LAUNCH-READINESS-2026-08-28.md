# Launch readiness — full store sweep

Date 2026-08-28. Every customer-facing page crawled in a real browser, plus an Admin API
audit of markets, shipping, variants and media. Target stated by the merchant: **English
only, United States is the primary market.** Everything below is judged against that.

Method: 10 pages crawled at 1440×900 and 390×844 under the preview cookie for theme
`189462839609`, plus Admin API reads. Pages reached: `/`, `/collections/all`, `/pages/about`,
`/pages/contact`, `/products/peluma-3-in-1-mist-grooming-brush`, and all five `/policies/*`.
All returned `200`. No broken internal links. The only external links anywhere are Shopify's
own two.

## Fixed in this session

**The checkout shipping rate.** `DeliveryMethodDefinition/1186423898425` on the Zendrop
profile read *"Free worldwide shipping on all orders. Delivery in 7-15 business days."* It now
reads:

> Free worldwide shipping on every order. Orders are processed within 2-3 days, and delivery
> typically takes a further 10-15 days - about 12-18 days in total.

Verified by reading the definition back after the write. This was the last screen before
payment and the only place still asserting the retired delivery claim in business days.

Nothing else was written. No theme writes at all this session.

## Blockers for an English / US launch

### 1. Hebrew text on the collection page

`/collections/all` renders its two filter labels in Hebrew, on desktop and mobile:

```
<span class="facets__label">זמינות</span>   (Availability)
<span class="facets__label">מחיר</span>     (Price)
```

The theme is not the cause — `locales/en.default.json` on theme `189462839609` was read in
full and is entirely English, including `content.price` = "Price". The shop has exactly one
locale, `en`, primary and published. These labels come from the storefront filter
configuration in the **Search & Discovery app**, which was almost certainly created while the
admin UI was in Hebrew. Fix: Apps → Search & Discovery → Filters → rename both.

This is on the page the "Shop" nav link points at. A US visitor clicking Shop sees Hebrew.

### 2. The only market is Israel

```
markets: [{ name: "Israel", handle: "il", primary: true, enabled: true, webPresence: null }]
```

Consequences observed live: the checkout URL is `/checkouts/cn/…/en-il`, and Country/Region
defaults to **Israel**. I previously attributed that default to this environment's egress IP —
that was wrong; it is the market configuration.

US customers *can* buy: the "International" delivery zone on the general profile includes
`US`, and the product sits on the Zendrop profile which ships worldwide free. So this is not
a hard blocker on transacting. It is a blocker on being a US-first store: market is what
Shopify uses for default country, currency presentment, duties, and what Merchant Center
reads as the target. A US market should exist and be primary before paid or organic US
traffic arrives.

### 3. A Hebrew, shekel-priced shipping rate is one step away from every new product

The **default** delivery profile is named `פרופיל כללי` and carries:

| Zone | Rate name | Price |
|---|---|---|
| Domestic (IL) | `רגיל` | ₪35 ILS (and a ₪0 range condition) |
| International (27 countries incl. US) | `International` | ₪57 ILS |

The current product is on the separate **Zendrop** profile, which is why checkout shows
"Free Shipping" in USD. But `DECISIONS.md` plans to add 4–8 more products. **Any product
imported and left on the default profile will show a US shopper a rate named `רגיל` priced in
shekels.** Fix this before the next import, not after.

### 4. VelvetPaw is still live in two policies

27 occurrences across `/policies/privacy-policy` (3) and `/policies/terms-of-service` (24),
including the opening line of the Terms: *"Welcome to VelvetPaw! The terms 'we', 'us' and
'our' refer to VelvetPaw."* The cleaned files have been sitting in this directory since
27 Aug and have not been pasted. The connection holds `read_legal_policies` only, so this
cannot be done from here.

### 5. The shipping policy contradicts everything else

`/policies/shipping-policy` still reads:

> Processing Time: All orders are processed within 1 to 3 business days.
> Shipping Times: Standard international shipping typically takes between 7 to 15 business days.

Against the corrected 2–3 days processing and 10–15 days delivery (about 12–18 total) on the
product page and the About page. It was missed in the earlier correction pass. Policy page —
no write scope, admin only.

That makes the delivery claim consistent in three places and wrong in one. Before this
session it was wrong in two; the checkout half is now fixed.

### 6. Homepage title and meta still sell VelvetPaw

```
<title>VelvetPaw | Premium Pet Essentials & Accessories – Peluma</title>
<meta name="description" content="…Discover the VelvetPaw collection today">
```

This is the first thing Google shows. Already logged as admin-only (Online Store →
Preferences); now confirmed against the rendered page.

## Product media — worse than the earlier pass suggested

Twelve images. Rendered and inspected as a contact sheet:

| # | What it actually is |
|---|---|
| 1 | Orange/tan brush, clean on white |
| 2, 6, 7 | Three near-duplicate `68mm` dimension diagrams |
| 3 | Rose rolling ball, with **baked-in text: "Stain from sofa hair dust"** |
| 4 | Purple brush pair — matches the "Purple Brush" variant |
| 5 | A fourth dimension diagram, **with the supplier's red annotation boxes left in** |
| 8 | Rolling ball, with **baked-in text: "Sticky snack crumbs"** |
| 9 | Cat + hand + both brushes — the one genuine lifestyle shot |
| 10 | White brush, clean on white — matches "Porcelain White" |
| 11 | Same composite as 9, **with a fake video play button baked into the JPEG** |
| 12 | Rose rolling ball on white |

Three things here are not just "low quality", they are wrong to ship:

- **The fake play button (#11).** A static JPEG painted to look like a video. A shopper who
  clicks it gets nothing.
- **The red annotation boxes (#5).** Internal supplier markup.
- **The baked-in English (#3, #8).** "Stain from sofa hair dust" is not English a US buyer
  reads as native. It cannot be edited — it is pixels — so the image has to go or be replaced.

Four of twelve images are the same dimension diagram. One of them is currently the first
thing a mobile shopper sees, and it is the cart thumbnail.

I attempted to reorder the media so #10 (clean white brush, matching the default variant)
leads, followed by #9, #4, #1, then the balls, then the diagrams, with #5 and #11 last.
**The write was blocked by the permission classifier**, so the order is unchanged. It needs
either permission or two minutes in admin.

Also: all twelve share near-identical alt text ("Peluma 3-in-1 mist grooming brush for cats
and dogs"), including the dimension diagrams and the rolling-ball shots. Useless to a screen
reader, wasted for image search.

Masters run 476×467 to 695×683 against a `width=3840` srcset — unchanged from the earlier
finding.

## Open questions for the merchant

- **Compare-at price on all five variants** ($49.90, and $69.90 on Milk Brown Set). A
  permanent strikethrough is a reference-price claim. If those prices were never charged it
  is the same class of problem as the boilerplate that was removed twice.
- **Marketing consent is pre-checked at checkout** ("Email me with news and offers"). Opt-in
  checked by default is a problem for EU visitors and unpopular in the US.
- **`avnerseo@gmail.com` on five customer-facing pages**, seven occurrences. A gmail address
  as the only support contact reads as a hobby store to a US buyer deciding on a $29.90
  purchase from an unknown brand.
- **"Sunday to Thursday"** on the Contact page — already logged as a positioning call, but it
  reads oddly next to a US-first store.
- **Card payment is still unverified.** `checkout.pci.shopifyinc.com` is blocked by this
  environment, so the card fields cannot load here and checkout renders PayPal only. Confirm
  Shopify Payments is active — a US store that only takes PayPal loses most of its traffic.

## Still true from the earlier audit

Variant weights are all `0 KILOGRAMS`, barcodes all `null` (permanent, per Zendrop), the
homepage grid renders one card in a four-column row, the hero overlay should stay at 60%, and
the collection page and all five policy pages have no meta description.

## What has to happen before "live"

Admin, in this order:

1. Rename the two Search & Discovery filters to English.
2. Create a US market and make it primary.
3. Put a USD rate on the default delivery profile, or delete the Hebrew ones, so the next
   import cannot inherit them.
4. Paste the two cleaned policy files.
5. Correct the shipping policy to 2–3 / 10–15 / about 12–18.
6. Set the homepage SEO title and meta.
7. Confirm Shopify Payments is on.
8. Reorder product media and delete #5 and #11.

Then publish the theme. Items 1–5 are all things a US visitor sees; none of them are
cosmetic.
