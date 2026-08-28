# Peluma storefront — work log

Store `hjahey-v0.myshopify.com` / `pelumapets.com`. Worked via the Shopify MCP
connection (Admin API). Shopify CLI is **not** available in this environment —
see "Blocked" below.

## Theme

| | |
|---|---|
| Live (untouched) | `gid://shopify/OnlineStoreTheme/189442031929` — "Horizon", role `MAIN` |
| Working copy | `gid://shopify/OnlineStoreTheme/189462839609` — "Horizon — Peluma fixes (2026-08-27)", role `UNPUBLISHED` |

The live theme was duplicated first and has **not** been modified. Because the live
theme is untouched, it doubles as the rollback point: publishing the working copy
demotes the current live theme to unpublished, where it stays available.

### Applied to `templates/index.json` on the working copy

Homepage hero (`hero_jVaWmY`), addressing §4 b/c/d of the brief:

| Setting | Live | Working copy |
|---|---|---|
| empty text block `text_qFjWcV` | present (rendered a blank 24px gap) | removed |
| heading markup | `<p>Groom Smarter…</p>` | `<h1>Groom Smarter…</h1>` |
| heading preset | `h2` | `h1` |
| subheading `text_color` | `""` → resolves to `#000` on a dark image | `{{ settings.color_palette.background }}` (white) |
| overlay `overlay_color` | `#12121266` (40%) | `#12121299` (60%) |
| CTA background | `color_palette.color2` (`#DFDFDF`) | `color_palette.foreground` (`#000`) |
| CTA text | `foreground` (`#000`) | `background` (`#fff`) |
| CTA border | `background` (`#fff`) | `foreground` (`#000`) |
| CTA width | `custom` @ 14% | `fit-content` |
| hero vertical alignment | `flex-end` | `center` |
| product-list heading | `<h3>{{ closest.collection.title }}</h3>` | `<h2>Shop Peluma</h2>` |

The homepage previously had **no `<h1>` at all** — the hero heading was a `<p>`
styled as `h2`. That is now a real `h1`. Hero copy was not changed.

`<h2>Shop Peluma</h2>` is the one string not taken from the brief. It replaces a
Liquid binding that rendered the "all" collection's title. It is a section label,
not a claim — swap it for anything else if you have approved wording.

### Not applied — needs a decision

- **§4a hero media.** Still `Orange_Brown_Cute_Illustration_Pet_Care_Logo_1.png`
  (the cartoon). `cdn.shopify.com` is blocked by this environment's egress policy,
  so the 12 product photographs could not be viewed and one could not be chosen
  responsibly. All of them are also small for a hero — the largest is 695×650.
- **§3 logo.** `config/settings_data.json` still reads
  `"logo": "shopify://shop_images/VELVETPAW.png"`, `logo_height: 100`. The new
  wordmark PNG is not in Shopify Files (only `VELVETPAW.png` and two
  `Orange_Brown_Cute_Illustration_Pet_Care_Logo*.png` illustrations are). Once the
  wordmark is uploaded, this is one file write: repoint `logo` and set
  `logo_height` / `logo_height_mobile` to the Horizon preset values `36` / `28`.

## Policies (§6)

Cleaned copies are in this directory, ready to paste into
Settings → Policies:

- `privacy-policy.peluma.html` — 41,691 → 16,254 bytes
- `terms-of-service.peluma.html` — 53,546 → 23,786 bytes

What was removed: a Gemini response wrapper (`div.markdown-main-panel`,
`div.container`, `id="p-rc_…"` on every paragraph), 334 empty
`<sup class="superscript">` citation chips, 21 `source-inline-chip-container`
button blocks, orphaned `</span>` tags from citation markup (one of which had
broken a link into `…shopify.com/e</span>n`), and every `<!---->` comment.
"VelvetPaw" → "Peluma" throughout (3 occurrences in Privacy, 24 in Terms).

Rendered text was verified byte-identical before and after, apart from the brand
name. No wording was rewritten.

These could not be written through the API: the app connection holds
`read_legal_policies` but **not** `write_legal_policies`, so `shopPolicyUpdate`
returns "Access denied". Paste them by hand, or use
Settings → Policies → "Replace with template", which also produces correct text.
Either way: **not the refund policy** (§6).

## Blocked in this environment

The organization's egress policy returns `403` on CONNECT to
`cdn.shopify.com`, `pelumapets.com` and `hjahey-v0.myshopify.com`. Consequences:

- Shopify CLI cannot authenticate — same wall the previous session hit.
- The storefront cannot be previewed or screenshotted.
- Product images cannot be viewed.

The Admin API over MCP is unaffected and authenticated against Peluma.

## Admin-UI only — unchanged by design (§5, §7, §8)

Homepage SEO title/meta, sender email, and domain email forwarding have no Admin
API mutation for any app. They remain as the brief describes them.

## Brand sweep (27 Aug)

Checked every customer-facing surface reachable from the Admin API for
"VelvetPaw" leftovers: shop name, both pages, product title / description /
SEO title / meta description, product metafields, collections.

**Clean.** The only remaining occurrences store-wide are in the Privacy Policy
and Terms of Service, which are the two files in this directory.

Also verified the return-shipping promise agrees across all three places it
appears, since the brief notes that promise was one of the four defects
hand-fixed in the refund policy:

- Refund policy — store pays for damaged / defective / wrong; customer pays for
  change of mind.
- About page — "if something arrives damaged, defective, or simply is not what
  you ordered, we cover return shipping".
- Contact page — "we cover the return shipping" for damaged or wrong.

All three agree. No contradiction to fix.

Shipping times also agree: About says 1–3 days processing, 7–15 business days
delivery; the shipping policy says the same. Whether that claim survives depends
on Zendrop's answer about fulfilment origin.

### Open, needs your decision

- **Contact page says "Sunday to Thursday"** for reply times. That is accurate
  for an Israel-based operation and confusing for the US audience the store is
  written for. Not changed — it is a positioning call, not an error.
- **`avnerseo@gmail.com` appears in more places than §7 implies:** shop
  `contactEmail`, the Contact page (once), the refund policy (twice), the
  privacy policy (once) and the terms (twice). The two refund-policy
  occurrences have to be hand-edited — that policy must not be regenerated.

## Second pass — conversion surfaces (27 Aug)

### Fixed live (not theme-scoped)

**Redirect chain collapsed.** There were two hops:
`/products/cat-pet-steam-brush` → `/products/velvetpaw-3-in-1-mist-grooming-brush`
→ `/products/peluma-3-in-1-mist-grooming-brush`. The first now points straight at
the final URL. The middle redirect was kept, since links to the velvetpaw handle
may exist.

### Fixed on the working theme

**`sections/footer-group.json` — removed the social links block.** It carried
Horizon's placeholder defaults: `https://www.facebook.com/`,
`https://www.instagram.com/`, `https://www.youtube.com/`,
`https://www.tiktok.com/`, `https://x.com/`. Five icons in the footer of every
page, each sending a visitor to a social network's *homepage* and out of the
store. Add real profile URLs in the editor when the accounts exist.

**`templates/product.json` — removed two empty elements:**
- the `product-recommendations` section ("You may also like", `related`, up to 4
  products) — the store has one product, so it had nothing to show;
- the `disclosures` block — heading "Disclosures" with zero child blocks.

### Verified sound, no change made

- Product title renders as a real `<h1>`.
- Sticky add-to-cart on, pickup availability off, accelerated checkout present.
- Product is ACTIVE and published to both Online Store and Google & YouTube.

### Open

- **The `disclosures` slot was the right place for shipping and returns next to
  the buy button.** Removed rather than filled, because filling it means writing
  customer-facing copy. Proposed wording is drawn only from the existing shipping
  and refund policies — no new claims — and needs approval before it goes in.
- **Google & YouTube channel is live with all 5 variants at `barcode: null`**
  and no `identifier_exists` handling. Either real GTINs from Zendrop, or the
  "no manufacturer identifier" setting in the Google & YouTube app. Not an Admin
  API field — has to be done in the app.
- **All 5 variants have weight `0 KILOGRAMS`.** Fine while shipping is free and
  flat, a problem for feed quality and for any future carrier-calculated rate.
- **Footer newsletter copy** promises "exclusive deals and early access to new
  products" — a one-product store with neither. Horizon default text.
- **The `Style` option mixes two dimensions** — colour and set-vs-brush — across
  "Porcelain White Set", "Milk Brown Set", "Porcelain White Brush",
  "Purple Brush", "Set". Restructuring needs Zendrop's answer on what "Set"
  contains.

## Shipping / Returns / Cancellations accordion (27 Aug, approved copy)

Added to `templates/product.json` on the working theme, directly below the buy
buttons and above the product description. Three `_accordion-row` blocks inside
one `accordion` block:

- **Shipping** — open by default
- **Returns** — collapsed
- **Cancellations** — collapsed

Copy is the merchant-approved wording, every line traceable to the existing
shipping or refund policy. No guarantee language beyond what those policies
already commit to.

Correction to the earlier note in this file: the `disclosures` block that was
removed was **not** rendering a visible empty heading. `blocks/disclosures.liquid`
reads `closest.product.metafields.shopify.disclosure.value` and emits
`<div hidden shopify-block-empty>` when that metafield is empty, which the
block's own stylesheet then hides with `display: none`. It was dead weight, not
a visible defect — and it was the wrong component for this content, since it
takes no child blocks. `accordion` is the right one.

Verified by reading the file back: all three rows, their text and their position
in `block_order` are intact.

**Dependency:** the "7–15 business days" line is the same claim that appears on
the About page and in the shipping policy. If Zendrop's answer on fulfilment
origin changes it, it changes in three places.

## Full verification (27 Aug, after merchant's logo + hero work)

Diffed live `189442031929` against working `189462839609`, file by file, with
JSON normalised and key-sorted so every changed key shows.

### Working theme — all correct

| | |
|---|---|
| `logo` | `shopify://shop_images/Peluma-Logo.png` |
| `logo_height` / `logo_height_mobile` | 36 / 28 |
| hero `image_1` | `shopify://shop_images/Peluma-Hero.png` |
| `VELVETPAW` references | none anywhere in the theme |
| accordion rows | Shipping, Returns, Cancellations — all present |

`config/settings_data.json` differs from live in **exactly three keys** — `logo`,
`logo_height`, `logo_height_mobile`. Nothing else drifted.

Every earlier fix survived: empty hero text block gone, `<h1>` heading at `h1`
preset, white subheading, 60% overlay, solid black CTA at `fit-content`,
centred hero content, `Shop Peluma` product-list heading, footer social block
removed, product-recommendations section removed, accordion in place below the
buy buttons.

New assets are well-formed for their jobs: `Peluma-Logo.png` 2172×724 (3:1
wordmark), `Peluma-Hero.png` 1672×941 (~16:9).

### The live theme was modified

Live `updatedAt` is 2026-08-27T12:46:38Z, after the fork. Its hero `image_1` is
also `Peluma-Hero.png`. That one setting is the **only** drift — live still
carries the old empty text block, `<p>`/h2 heading, grey clipped CTA, 40%
overlay, `flex-end` alignment, the collection-title binding, the social-links
block, the recommendations section, and the VELVETPAW logo at 100/100.

Nothing was lost and no merge is needed. The consequence is only that the
rollback point is no longer a pristine pre-work snapshot — it now includes the
new hero image, which is a change that was wanted anyway.

### One judgement call to review in preview

The hero overlay was raised from 40% to 60% black **because the background was
then a busy light cartoon** and the subheading was unreadable over it. The
background is now a purpose-made hero image, so 60% may be heavier than it
needs to be. Worth looking at in preview; dialling it back is one write.

## 28 Aug — Zendrop answered, and a bad merge in the product template

### Zendrop's answers

- **Ships from China only.** 2–3 days processing, 10–15 days transit. No US warehouse.
- **No GTIN / UPC / EAN exists** for any China-sourced Zendrop product — a shipping-regulation
  constraint, not a gap in their data. This applies to every future import, not just this
  product. HS codes were offered instead: useful for customs, not for Merchant Center.
- **"Set" (Z75Y6C7M0)** = a white brush plus a milk brown brush.
- **"Porcelain White Set" and "Milk Brown Set"** = a brush plus a rolling ball, and both
  cost Zendrop more for that reason.

### Two problems found in the theme editor's save

The merchant edited the Shipping row in the theme editor. Reading the saved file back
showed two things the editor's UI did not:

1. **The new text was appended to the old text, not replacing it.** The row contained the
   7–15 day claim immediately followed by the 12–18 day claim, with no space between
   sentences — a paragraph asserting two different delivery times at once.
2. **A second, unrelated accordion appeared** (`accordion_zYLCEc`) carrying Horizon's stock
   preset rows: "Return policy", "Shipping" and "Manufacturing". The Manufacturing row read
   *"Our products are manufactured both locally and globally. We carefully select our
   manufacturing partners…"* — boilerplate about a supply chain this store does not have,
   sitting on a product that ships from a single Chinese supplier.

Both were rewritten out. The Shipping row now reads:

> Free worldwide shipping on every order. Orders are processed within 2–3 days, and delivery
> to the United States typically takes a further 10–15 days — about 12–18 days in total.
> You'll receive a tracking number by email as soon as your order ships.

**Not verified by read-back.** The write returned no errors, but the permission classifier
blocked the follow-up read, so this rests on the mutation result alone rather than on a
diff. Worth re-checking.

### About page

Updated live (`/pages/about`): the "Honest delivery times" line now reads 2–3 days
processing and a further 10–15 days, about 12–18 in total.

### Google & YouTube

`marketingActivities` returns **zero** — no campaign is running and nothing is being spent.
The product is still published to the Google & YouTube channel as a free listing.
`publishableUnpublish` is blocked by this connection's safety policy, so pausing that
listing has to be done in admin.

### Still not doable from here

- **Shop name is already `Peluma`.** What still says VelvetPaw is the homepage SEO title and
  meta description, which live in Online Store → Preferences and have no Admin API mutation.
- **Policies** — no `write_legal_policies` scope. Files in this directory.
- **Variant weights** — no data. Asking Zendrop for packed weight per variant, rather than
  inventing a number.
- **Mobile, cart and checkout testing** — the storefront is blocked from this environment.

### Verified by read-back (28 Aug, second attempt)

The earlier read was blocked by the permission classifier; a retry went through.
`templates/product.json` on the working theme is confirmed correct: one accordion,
three rows, and a single shipping paragraph reading

> Free worldwide shipping on every order. Orders are processed within 2–3 days, and
> delivery to the United States typically takes a further 10–15 days — about 12–18 days in
> total. You'll receive a tracking number by email as soon as your order ships.

No stray accordion, no Manufacturing boilerplate. File is 9,819 bytes, down from 12,961.
The live theme is untouched and still carries its original product template.

### Footer newsletter copy

`sections/footer-group.json` — replaced Horizon's default *"Get exclusive deals and early
access to new products"* with *"Occasional emails when we add something new. No spam, and
you can unsubscribe at any time."* Same defect class as the Manufacturing boilerplate: a
theme default promising something the store does not have.

## Sweep of the remaining templates (28 Aug)

Reviewed `collection.json`, `cart.json`, `404.json`, `search.json`, `page.json` and
`header-group.json` — the files not touched until now. Two real defects.

**The announcement bar was bright magenta at heading size.** `header-group.json` carried
`"text_color": "#af14bd"` at `font_size: 1.5rem`, running across the top of every page. The
store's entire palette is `#ffffff` / `#000000` / `#333333` / `#DFDFDF` — that purple appears
nowhere else in the theme. Changed to `color_palette.foreground` at `0.875rem`, which is
supporting-text size for an announcement bar. The wording was left alone; it is on-brand and
makes no claim. **If the purple was deliberate, it is one field to put back.**

Also set `show_language: false` there. The store publishes exactly one locale, so the
language selector had nothing to switch between.

**The cart page recommended the product already in the cart.** `cart.json` carried a
`product-list` section headed "You may also like", pulling from collection `all`, max 4. With
one product in the store, that renders the item the shopper has just added, directly under
their own cart. Section removed. This is different from the product-page section removed
earlier — that one used `related` and rendered nothing; this one renders the wrong thing.

`404.json` also carries a product list ("Discover something new"). Left in place: on a 404,
showing the shop's one product is a reasonable destination rather than a dead end.

`collection.json`, `search.json` and `page.json` are sound — real `<h1>`s bound to the
collection or page title, no placeholder copy.

## Composio is not the Shopify connection

Checked, because it was assumed to be. Two separate things: Shopify runs over its own MCP
server here; Composio is a different connector and has **no active Shopify connection**.

Connecting it would not solve the policy problem. Its Shopify toolkit has no
policy-update action — a search for one returns `SHOPIFY_CREATE_PAGE` / `SHOPIFY_UPDATE_PAGE`
(ordinary pages, already available here) and Box's own enterprise terms-of-service, which is
unrelated. What it does add is `SHOPIFY_UPDATE_THEME` with `role: "main"` (publish) and
`SHOPIFY_DELETE_THEME`. Publishing is one click in admin and should be deliberate; theme
deletion is not power worth holding. Recommendation: do not connect it.

## 28 Aug — the storefront was finally rendered in a browser

Full write-up in `peluma/PREVIEW-AUDIT-2026-08-28.md`. Read-only session; no theme writes.

Chromium reached the store once TLS was capped with `--ssl-version-max=tls1.2` — the egress
gateway resets Chrome 141's 1783-byte post-quantum ClientHello, and the `PostQuantumKyber` /
`UseMLKEM` flags no longer shrink it. Capping the version drops it to 201 bytes. TLS
verification stays on. Preview via `?preview_theme_id=189462839609` once; the cookie carries
through checkout.

Verified on theme 189462839609, desktop 1440×900 and iPhone 13: add to cart → cart → checkout
completes on both, no horizontal overflow, no theme-origin console errors, announcement bar at
14px black weight 400, and every earlier fix visible on the rendered page.

Desktop `html`/`body` compute to `overflow:hidden; height:100dvh` at ≥990px — that is Horizon
by design, `.page-wrapper` is the scroll container. The live theme does the same. Automation
must scroll `.page-wrapper`, not `window`.

New defects, in priority order:

1. **Checkout still says "Delivery in 7-15 business days."** The shipping *rate* description
   was missed when the claim was corrected in the accordion, the About page and the shipping
   policy. It is the last screen before payment. Settings → Shipping and delivery, admin only.
   Note it says *business* days, while the product page says plain "days" — checkout is
   pre-answering the business-vs-calendar question `DECISIONS.md` is still waiting on Zendrop for.
2. **The cart thumbnail is the `68mm` dimension diagram**, not a product photo.
3. **On mobile the product gallery opens on that same diagram**, letterboxed with large margins.
4. **Product image masters are 476×467 to 695×683** — the theme requests `width=3840`, so the
   desktop gallery is upscaling roughly 2×. Supplier cut-outs and spec sheets, no lifestyle
   photograph. Good enough to launch on, not good enough to compete on.
5. Variant selection does not change the gallery image.
6. No sticky add-to-cart appeared at 390px, though it is recorded here as on.
7. Two `<h1>`s on the homepage — the hero plus Horizon's hidden header-logo one.
8. `<title>` still renders `VelvetPaw | Premium Pet Essentials & Accessories` (already known).

Could not verify: **card payment**. `checkout.pci.shopifyinc.com` is blocked by egress, so the
card fields could not load and checkout showed PayPal only. That is an artefact of this
environment, not a finding — confirm Shopify Payments in admin. Two things that did render and
need a decision: the marketing-consent checkbox is **pre-checked**, and `$29.90` is struck
against `$49.90` everywhere, which is a reference-price claim if `$49.90` was never charged.

**The hero overlay question is answered, and the premise was wrong.** The text is centred over
the brightest part of the image. Measuring WCAG contrast on the real composited pixels: at 60%
both the heading and the subheading pass everywhere; at 50% a quarter of the subheading falls
below 4.5:1; at the live theme's 40% both fail. Keep `#12121299`, or `#1212128C` (55%) as the
floor. Dialling back to 45% would be an accessibility regression. The real improvement is the
crop — the brush is cropped out entirely at 390px. This closes the overlay item listed as an
open merchant decision in `DECISIONS.md`.

The one-card-in-a-four-column-grid problem `DECISIONS.md` describes is confirmed visually and
looks worse in a browser than on paper. Separately, the `$49.90` compare-at price runs on every
surface and is a reference-price claim — it belongs in `DECISIONS.md` and is not there yet.

## 28 Aug — full store sweep against the English / US-first target

Full write-up in `peluma/LAUNCH-READINESS-2026-08-28.md`. Merchant restated the target this
session: **English only, United States primary.** Every page crawled in a browser at 1440×900
and 390×844, plus an Admin API audit of markets, delivery profiles, variants and media.
All 10 customer-facing pages return 200; no broken internal links.

**Changed live (one write, verified by read-back):** the Zendrop profile's Free Shipping rate
description, `DeliveryMethodDefinition/1186423898425`. Was "Delivery in 7-15 business days",
now "Free worldwide shipping on every order. Orders are processed within 2-3 days, and
delivery typically takes a further 10-15 days - about 12-18 days in total." No theme writes.

New blockers, all against the English/US target:

1. **Hebrew on `/collections/all`** — the two filter labels render `זמינות` and `מחיר`. Not
   the theme: `locales/en.default.json` was read in full and is entirely English, and the shop
   has one locale (`en`, primary, published). It is the Search & Discovery app's filter labels,
   created while the admin UI was Hebrew. The "Shop" nav link points at this page.
2. **The only market is Israel** (`handle: il`, primary, `webPresence: null`). That, not this
   environment's IP, is why checkout is `/en-il` and defaults Country to Israel — correcting
   what the previous audit assumed. US customers can still buy (the International zone
   includes US), but a US-first store needs a US market as primary.
3. **The default delivery profile is `פרופיל כללי` with rate `רגיל` at ₪35/₪57 ILS.** The
   current product is on the Zendrop profile so customers see Free Shipping in USD — but every
   new import that lands on the default profile will show a US shopper a Hebrew, shekel-priced
   rate. Fix before the 4–8 product expansion in `DECISIONS.md`, not after.
4. **VelvetPaw is still live in the Privacy Policy (3) and Terms (24).** The cleaned files
   have been in this directory since 27 Aug and were never pasted.
5. **The shipping policy still says 1–3 and 7–15 business days** — missed in the correction
   pass. The delivery claim is now right in three places and wrong in one.
6. Homepage `<title>` and meta still sell VelvetPaw.

**Product media is worse than the first pass showed.** Twelve images: four are near-duplicate
`68mm` dimension diagrams, one of those still carries the supplier's red annotation boxes, two
have baked-in marketing text in non-native English ("Stain from sofa hair dust", "Sticky snack
crumbs"), and one is a static JPEG with a **fake video play button painted into it**. All
twelve share near-identical alt text. A reorder putting the clean white-brush shot first was
attempted and **blocked by the permission classifier** — order unchanged.

Still open for the merchant: compare-at prices on all five variants ($49.90 / $69.90),
pre-checked marketing consent at checkout, `avnerseo@gmail.com` on five customer-facing pages,
and card payment still unverified because `checkout.pci.shopifyinc.com` is blocked here.

### 28 Aug — item-by-item fixes, merchant approving each step

**Item 1 — product media.** Reordered all 12 so the clean porcelain-white brush leads and
everything questionable (the supplier's red annotation boxes, the fake video play button, the
two images with marketing text baked into the pixels) sits at the bottom of the gallery.

Reordering alone did **not** fix the mobile first slide or the cart thumbnail. Both are driven
by the **variant** image, not the product media order. Found on inspection: "Porcelain White
Set" (the default variant) and "Milk Brown Set" both had a `68mm` dimension diagram as their
variant image. With the merchant's approval:

- Porcelain White Set → `33e6eede…` (clean porcelain-white brush)
- Milk Brown Set → `490627294…` (milk brown brush)

Verified in a browser afterwards: the mobile product page and the cart both now show the clean
brush. The diagram is gone from both.

**Item 2 — alt text.** All 12 images carried near-identical alt text, including the four
dimension diagrams and the three rolling-ball shots. Each now describes what is actually in
the frame. Two deliberate choices: the image with the fake play button gets ordinary alt text
that does not mention video, and the rolling-ball images are described as a rolling ball
lint remover rather than as the brush — which is also the clearest evidence that this listing
is carrying two different products under one product record.

**Item 3 — the default delivery profile.** The International zone (27 countries including the
US) was `International` at ₪57 ILS. It is now `Free Shipping` at **$0 USD** with the corrected
English description. Verified by read-back.

The Domestic (Israel) zone **could not be changed** — Shopify rejected it: that method
definition carries a rate range condition, and this API version cannot edit a definition with
multiple conditions. It is still `רגיל` at ₪35 and needs admin. The profile's own name,
`פרופיל כללי`, is admin-side only and was left alone.

Confirmed end to end afterwards: checkout now renders "Free Shipping — Free worldwide shipping
on every order. Orders are processed within 2-3 days…", so the earlier Zendrop-profile fix is
verified live and not just by mutation result.

**Item 4 — the US market. Attempted, broke checkout, rolled back.**

First, a correction to the earlier audit. The Israel market's condition is `SPECIFIED` over a
single region: Israel. It is the only market. So it is not that the primary market was merely
*wrong* — **no market covered the United States at all.** US visitors fell through to the
default market, which is why checkout was `/en-il`.

Created `United States` (`handle: us`, ACTIVE, base currency USD, region US). The checkout URL
did move to `/en-us` — and then checkout landed on `/stock-problems` with an empty cart. The
cart permalink that had added a unit minutes earlier returned `item_count: 0`.

Set the market to DRAFT immediately and re-verified: cart back to 1 item at $29.90, checkout
back to `/en-il` and working. Total time broken was one verification cycle. **The market still
exists, as DRAFT** — it is not deleted, so it can be activated once the cause is fixed.

Cause, from the follow-up reads:

- The only location returned by `locations` is `Adnei-Paz Street 29`, **country IL**, active
  and fulfilling online orders.
- The product's inventory is not there. It sits at a separate `Zendrop` location with 50,000
  available and `tracked: false`.
- The Zendrop delivery profile's only zone is `[Zendrop — Worldwide Zone]`, whose country list
  is a single entry: **`Rest of World` (countryCode `null`)** — the US is not named explicitly.

So the working hypothesis is that with a US market active, the US stops resolving through
"Rest of World" and no rate or fulfilment route is found, which surfaces as a stock problem.
Note the general profile's International zone *does* name `US` explicitly — the Zendrop one
does not.

**Correct sequence, not yet done:** add United States explicitly to the Zendrop profile's zone
(or give that profile a US zone carrying the same free rate) **first**, then flip the US market
back to ACTIVE, then re-verify cart and checkout. Doing it in the other order is what broke it.

**Item 4 — retried in the correct order, and it worked.**

The hypothesis held. Added an explicit `United States` zone to the **Zendrop** delivery profile
carrying the same free rate (Shopify rejected the first attempt: a US zone must include its
provinces, so `includeAllProvinces: true`). The profile now has two zones, both free:
`United States` and the original `[Zendrop — Worldwide Zone]` / Rest of World.

Then set the US market back to ACTIVE and verified end to end on an iPhone viewport with a
real US address:

- cart 1 item, $29.90 USD
- checkout `/en-us`, **no stock problem**
- Country/Region defaults to **United States**, with State and ZIP fields
- shipping method renders: *"Free Shipping — Free shipping on every order. Orders are
  processed within 2-3 days, and delivery typically takes a further 10-15 days - about 12-18
  days in total. FREE"*
- order-summary thumbnail is the clean brush from item 1

So the ordering rule is now established for this store: **a market cannot go active before its
countries are named explicitly in the delivery profile that serves the products.** "Rest of
World" does not cover a country that has its own market.

**Item 5 — the theme. Deliberately no changes.**

Read `templates/index.json` on the working theme. Everything earlier sessions fixed is intact:
`overlay_color` is `#12121299`, the `<h1>` is a real h1 at the h1 preset, `Shop Peluma` is the
product-list heading, the CTA is solid black at fit-content, the hero content is centred.

The one remaining theme-level observation is `"columns": 4` on the product list, which is why
one product looks lost in a wide row. That is **not** changed, on purpose: the grid is sparse
because the catalogue has one item, and `DECISIONS.md` plans 4–8 more, at which point 4 columns
is correct. Editing this file to set 3 and editing it back later is churn on the one file that
has already been corrupted once by a theme-editor save. The fix for a sparse grid is products.

For whoever adds those products: `"image_ratio": "adapt"` on the product card means cards will
be ragged once images with different aspect ratios sit side by side. Set a fixed ratio in the
same edit that adds the products, not before.

### Two "admin-only" items re-tested against the API, 28 Aug

Both turned out to be addressable as *resources* but not writable, so both stay admin-only.
Recording the attempts so nobody re-runs them.

**Filter labels.** They are real resources: `OnlineStoreFilterSetting/122377273657` (`זמינות`)
and `/122377306425` (`מחיר`), each with a translatable `label` at `locale: en`.
`translationsRegister` refuses them — *"Locale cannot be the same as the shop's primary region
and language settings."* Those Hebrew strings are the **base** values, not translations, and
the Admin API exposes no mutation to edit an `OnlineStoreFilterSetting`. Apps → Search &
Discovery → Filters → click the filter → **Filter label**.

**Homepage SEO.** Also a real resource: `Shop/101098225977` carries `meta_title`
"VelvetPaw | Premium Pet Essentials & Accessories" and a matching `meta_description`, again at
`locale: en` and again refused by `translationsRegister` for the same reason. Shopify's SEO
docs point at `global.title_tag` / `global.description_tag` metafields, so that was tried:
`metafieldsSet` accepted them on the Shop owner, but the rendered homepage `<title>` did not
change — checked twice, once with a cache-buster. **Shop-level `title_tag` does not drive the
homepage title.** The two stray metafields were deleted afterwards so nothing junk is left on
the shop. Online Store → Preferences is the only route.

### Item 1 solved without the app — filters disabled on the collection template

The Search & Discovery app **is not installed** on this store (installed apps: Zendrop, the
Claude connector, Messaging). So the Hebrew filter labels were not app configuration — they
are Shopify's built-in default storefront filters, whose labels are base values that no
mutation can edit.

Rather than install an app to rename two labels, the filters were switched off. In
`templates/collection.json` on the working theme, the `filters` block of `main-collection`:

```
"enable_filtering": true   →   false
```

Correct on the merits regardless of language: an "Availability" and a "Price" filter on a
collection holding one in-stock product at a single price refine nothing. `enable_sorting` and
`enable_grid_density` are untouched, and both render in English ("Sort", "Column grid").

Procedure, since this file class has been corrupted once before:

1. `themeFilesCopy` within the theme → `templates/collection.pre-filter-fix-backup.json`,
   byte-identical at 7215 bytes, as a restore point.
2. `themeFilesUpsert` with the full file, one value changed. Result size 7216 — exactly +1 for
   `true` → `false`, which is itself a check that nothing else moved.
3. Verified in a browser at 1440×900 and on an iPhone 13: **zero Hebrew characters** in the DOM
   on `/collections/all`, on both viewports.

**Before publishing, delete `templates/collection.pre-filter-fix-backup.json`.** It is reachable
as an alternate template (`?view=pre-filter-fix-backup`) and should not ship.

### Side effect of the US market to review

With two markets now defined, the header renders a **region and language selector** ("USD",
"Region and language selector") on desktop `/collections/all` — it was not there when Israel
was the only market. It is not broken, but it does let a US visitor switch themselves into the
Israel market. If that is unwanted, it is a header setting in the theme editor, in the same
place `show_language: false` was set earlier.

## 28 Aug — LIVE

The merchant published theme `189462839609`. Verified against the live storefront with no
preview parameter — this is what a customer sees.

`Shopify.theme` reports id `189462839609`, **role `main`**. The previous live theme
`189442031929` drops to unpublished and remains the rollback point.

Swept all ten customer-facing pages at 1440×900 and on an iPhone 13:

| | |
|---|---|
| "VelvetPaw" | **0 occurrences**, all ten pages — the cleaned policies were pasted |
| Hebrew characters | **0**, all ten pages, including `/collections/all` |
| Homepage `<title>` | `Peluma \| Pet Grooming Essentials for Cats & Dogs` |
| Homepage meta | the new description, no VelvetPaw |
| Shipping policy | "7 to 15 business days" and "1 to 3 business days" both gone |
| Cart | 1 item, $29.90 USD, thumbnail is the clean porcelain-white brush |
| Checkout | `/en-us`, Country defaults to **United States**, State and ZIP fields, no stock problem |
| Theme console errors | none — every console error traces to a host blocked by this environment |

Every fix from this session survived publication: media order and variant images, alt text,
the Zendrop rate wording, the US market and its delivery zone, and the disabled filters.

One cosmetic leftover in the shipping policy: a doubled period in "about 12–18 days in
total..". The duplicated "Processing Time:" label the merchant introduced on first paste was
caught and corrected.

### Accepted at launch, knowingly

- **PayPal is the only payment method.** Shopify Payments does not serve Israel-based
  merchants — verified against Shopify's supported-countries list, not assumed. The three
  offered alternatives (PayPlus, Hyp, Checkout.com) each add Shopify's 2% on top of their own
  fee. Deferred until there are 20–50 orders to decide against.
- **Delivery is 2–3 weeks**, because this SKU ships from China. Zendrop stocks top SKUs in a
  California warehouse and the catalogue has a `Ships From: US` filter; sourcing from it would
  cut delivery to roughly a week. That is the single largest improvement available and it is a
  catalogue decision, not a settings one.
- The `$49.90` compare-at price and the pre-checked marketing consent remain open merchant
  decisions.

### Post-launch verification — order calculation across US states

The merchant has no US address, so a real US test order is not possible. Ran
`draftOrderCalculate` instead — it computes the full order without creating or persisting
anything, so there is zero footprint on the live store and no charge.

| Scenario | Subtotal | Shipping | Tax | Total |
|---|---|---|---|---|
| New York, 1 × Porcelain White Set | $29.90 | Free Shipping $0.00 | $0.00 | $29.90 |
| California, 1 × Porcelain White Set | $29.90 | Free Shipping $0.00 | $0.00 | $29.90 |
| Texas, 1 × Milk Brown Set | $39.90 | Free Shipping $0.00 | $0.00 | $39.90 |
| Illinois, 2 × Porcelain White Set | $59.80 | Free Shipping $0.00 | $0.00 | $59.80 |

**Exactly one shipping rate is offered in every case** — the US zone added to the Zendrop
profile is serving, with no competing or duplicate rate. Variant pricing resolves correctly
($39.90 for Milk Brown Set, not the default $29.90).

Tax is zero everywhere, which is correct: no US nexus, and the shop is `taxesIncluded: true`,
so the displayed price is what the customer pays. Nothing is added at checkout.

Still unverifiable without a real order: that a PayPal payment actually clears, that the order
reaches Zendrop, and that the confirmation email is clean. The merchant is placing a test order
to their own Israeli address, which exercises the Rest of World zone rather than the US zone —
acceptable, since the US zone is covered by the table above, and the three untested items are
address-independent.

That order also puts the physical product in the merchant's hands, which is the only way to
replace the supplier imagery: four near-duplicate dimension diagrams, one with the supplier's
red annotation boxes, two with broken English baked into the pixels, and one static JPEG with a
fake video play button painted on.

## 28 Aug — first order placed and paid

Order **#1001**, $29.90 USD, `displayFinancialStatus: PAID`.

The merchant could not test by paying from their own PayPal: PayPal blocks a merchant buying
through their own seller account, in every path — login, guest, and a fresh incognito session.
That block is a PayPal rule about self-purchase, not a store defect, and a real customer never
meets it. Recording it so nobody burns another hour on it.

**The path that worked, and what it proves.** PayPal's guest checkout — *"pay with a credit or
debit card"*, no PayPal account, no login — with an email other than the seller's. It went
through.

That settles the largest open question from the payments review. "PayPal only" does **not** mean
"no card payments": a US customer without a PayPal account can pay by card, through PayPal's
screen rather than in the Shopify checkout. Worse than an embedded gateway, far better than the
PayPal-account-only reading that was feared.

Verified on the resulting order:

| | |
|---|---|
| Financial status | PAID |
| Total / tax | $29.90 USD, $4.56 Israeli VAT included |
| Shipping | Free Shipping, $0.00 |
| Line item | Porcelain White Set, SKU `PE17TFL2V`, vendor Peluma |
| Line item image | `33e6eede…` — the clean brush, so the media fix carried into the order |
| Fulfillment service | **Zendrop** |
| Tags | `test-order`, `internal` |

Two PayPal transactions are recorded, a `FAILURE` then a `SUCCESS`, both $29.90. **Correcting
an earlier reading of this:** the failure was *not* the blocked self-purchase. Those blocks
happen before payment and never create a transaction at all. The failure was the card itself —
the Israeli issuer held the charge pending the cardholder's own approval, and it cleared on the
retry. The customer was charged once.

Worth carrying forward: an issuer declining a first cross-border charge to an unfamiliar
merchant and clearing it on retry is ordinary, and a US customer's bank can do the same. It is
not fixable from the store side, but it is a reason not to read a single declined transaction
as a broken checkout.

**Not verifiable from here, and now proven why.** `fulfillmentOrders` returns an empty list on
a paid order. Querying `currentAppInstallation { accessScopes }` settles it: this connection
holds `read_merchant_managed_fulfillment_orders` but **not**
`read_assigned_fulfillment_orders` and **not** `read_third_party_fulfillment_orders`. Zendrop
is a third-party fulfillment service, so its fulfillment orders fall in exactly the category
this connection cannot read, and Shopify returns an empty list rather than an error. The same
gap explains why `locations(includeInactive: true)` returns only the Hadera address and not the
Zendrop location.

So the empty list is evidence of blindness, not of a missing fulfillment order. What is
visible confirms the routing: the line item's `fulfillmentService` resolves to Zendrop. Closing
this needs the Zendrop dashboard or the order page in Shopify admin — neither reachable from
here, since Zendrop's domain is blocked by this environment's egress policy.

The order confirmation email and the invoice email both rendered correctly: Peluma branding,
English, no VelvetPaw.

### Zendrop confirmed on the order page

The order page closes the loop that the API could not. Order #1001's fulfillment section reads
**"לא מומש · Zendrop"** — unfulfilled, assigned to Zendrop. Shopify has routed the fulfillment
to them, which is exactly what the empty `fulfillmentOrders` response could not show.

The timeline confirms the rest:

- Payment of $29.90 USD processed through **PayPal Express Checkout**, authorization `3C1JMFYQH`
- Order confirmation email sent to `avnerseo@gmail.com`
- Created from draft order #D1
- The earlier failure recorded 13 minutes prior — the issuer hold, per the merchant

Also on the order: risk assessed **low**, and PayPal Seller Protection may apply.

**One thing a real order surfaced.** The shipping line renders as
`Free Shipping (0.0 kg: items 0.0 kg, package 0.0 kg)` — the zero variant weights, now visible
on a live order rather than only in the API. Harmless while shipping is free and flat, and a
problem the moment a weight-based rate or a quality Merchant Center feed matters. It stays part
of the open Zendrop question about packed weight per SKU.

**Channel caveat worth carrying forward:** this order's channel is *Draft Orders*, not *Online
Store*, because it was created as an invoice. Some fulfillment apps sync only storefront
orders. Zendrop was assigned here, so this looks fine — but the first genuine storefront order
is still worth watching, in case draft-origin orders behave differently in Zendrop's own sync.

## 2026-08-28 — Supplier screen via Zendrop MCP; POD confirmed out of reach

Ran the product screen against the Zendrop catalog through the MCP connection.

**Grooming vacuum kits (the merchant's own category, higher ticket):**
- `2000023` Daski Vkiskli 4-in-1, NexoraUSA — $61.33, shipping **$0**, **6 days** to US.
- `2001005` N3 9-in-1, NexoraUSA — $55.11, shipping **$0**, **6 days** to US.
- US market: oneisall $35–55, Afloia $65, a 12,000Pa kit recently at $39.99.
- **Rejected on margin.** Landed cost sits inside the market's retail band.

**Supplier 417 "Amazon Products" screened out permanently** — Amazon retail pricing or above
($176.66 / $232.70 / $352.16 on comparable kits), plus a $1.17 listing that is a data error.

That is five candidates across four categories, all failing the same screen. Recorded in
`DECISIONS.md` as a supplier problem rather than a product-selection problem, and the earlier
"US sourcing is the highest-value move" hypothesis is marked tested and disproven — US shipping
does fix delivery times ($0–6.99, 6 days) but the base prices absorb the saving.

**Print-on-demand is not exposed through the MCP.** Verified against
`get_catalog_categories` (no POD category; the only "print" match is *Print, Copy, Scan & Fax*)
and against keyword searches on the POD blank names (returns supplier-417 blanks instead).
Zendrop's POD help article is blocked by the egress proxy.

POD base costs *were* confirmed competitive against Printify ($7.95 vs $13.09 on a mug, $6.50
vs $10.95 on a poster) — the first cost structure this week that starts in the right place.
Shipping remains the one unknown, and the recommendation is deliberately parked until it is a
real Zendrop figure rather than a Printful benchmark. Numbered steps written into
`PRODUCT-SCREENING.md`.

No storefront or theme changes in this pass — research and documentation only.

## 2026-08-28 (later) — Pre-traffic audit, and order #1001 confirmed in Zendrop

Zendrop's MCP reconnected mid-session, so the two things that had been blocked on it are now done.

### Order #1001 — confirmed, and it is sitting unfulfilled

`get_order` on store `3546333`, order `#1001` (internal `45089149`):

- **Status: Unfulfilled.** Placed 2026-08-28 13:18 UTC, no issues, no tracking number yet.
- Porcelain White Set × 1, routed as `zendrop_fulfillment`.
- Ships to Hadera, IL, 3831014.

Routing is therefore fully confirmed end to end: Shopify → Zendrop, correct variant, correct
address. **But the order will not ship until it is paid for inside Zendrop.** Credit balance is
`0`, so fulfilling charges the payment method directly.

### The real cost, verified rather than estimated

`get_order_fulfillment_cost` on that order returns the actual figures Zendrop will charge:

| | |
|---|---|
| Products Cost | **$7.50** |
| Shipping Cost (to Israel) | **$14.20** |
| **Total** | **$21.70** |

This **confirms the $7.50 product cost already in `DECISIONS.md`** — it was correct. The $14.20 is
Israel-specific; the US figure on record is $9.92, so the US landed cost stays **$17.42**, and
every margin conclusion built on it stands. First time this week a cost has been read from a
real transaction rather than a catalog listing.

### Mobile product page — the buy button is below the fold

Pinterest traffic is overwhelmingly mobile, and these pins land on the product page, so it was
checked at iPhone 13 size (390×664 CSS px) before sending anyone there:

- Page height 2131px. **"Add to cart" starts at y=724 — past the bottom of a 664px screen.**
- The first screen is almost entirely the product image. The title only begins to appear at the
  very bottom edge; price, variant picker and buy button are all below it.
- `domReady` 1955ms — speed is fine, this is a layout issue, not a performance one.
- No review content on the page (expected — nothing may be fabricated).
- Shipping copy renders honestly: processed in 2–3 days, US delivery 10–15 days, 12–18 total.

Not fixed here: the product template belongs to the live theme, and writing to the live theme is
prohibited in this project. It is a theme-editor change, written up for the merchant.

### No analytics of any kind on the storefront

Grepped the live homepage: no `gtag`, no Google Analytics, no Meta pixel, no `pintrk`, no
Klaviyo — nothing. Shopify's own admin analytics still records sessions and orders, so the first
traffic is not invisible, but there is no channel-level attribution. The Pinterest app in
`PINTEREST.md` step 2 installs the Pinterest tag and Conversions API, which closes this for the
one channel about to be used.

A newsletter capture **does** exist in the footer (`contact[email]`), so non-buyers are not
entirely lost.

### Pinterest cannot be done from here — checked, not assumed

`pinterest.com` returns `000`; the proxy logs a 403 policy denial on CONNECT. Searched the
connector registry for a Pinterest MCP and there is none — the closest results are analytics
aggregators (Supermetrics, Funnel) and Klaviyo, none of which publish pins. Account creation and
pin upload stay with the merchant.

### Mobile buy button — checked further, and it is worse than first recorded

The product template already carries `"enable_sticky_add_to_cart": true`, so the below-fold
button looked like it might be a non-issue. It was tested rather than assumed, at three scroll
positions on an iPhone 13 viewport, looking for any `fixed` or `sticky` element containing
"Add to cart" or "Buy it now":

| scrollY | sticky buy bar found |
|---|---|
| 0 | none |
| 900 | none (the in-flow button is on screen here) |
| 1500 (page bottom) | **none** |

**The setting is enabled but no sticky bar renders on mobile.** So once a visitor scrolls past
y≈850, there is no way to buy without scrolling back up. Screenshots at each position confirm it
visually.

Sequence of what a phone visitor actually sees:

1. **First screen: the product image and nothing else.** No price, no variant picker, no button —
   the title only begins at the very bottom edge.
2. Scrolling reveals title, price, the five variant buttons, then Add to cart / Buy it now.
3. Past that, the buy controls are gone for the rest of the page.

The page content below is good and needs no work — description, "Why pet owners love it",
suitability, how to use, in the box, then the email capture.

Root cause is in the media gallery block: `"aspect_ratio": "adapt"` with
`"constrain_to_viewport": true` lets a tall product image occupy the whole first screen. Both are
theme-editor settings, not code.

Not changed here — `189462839609` is `MAIN` (live), and writing to the live theme is prohibited
in this project. Handed to the merchant as editor steps.

Also visible in the scrolled screenshot: the variant picker renders the five options as stacked
buttons, where **"Set"** sits directly under "Purple Brush" with nothing to distinguish it. On a
phone that ambiguity is more prominent than on desktop.

## 2026-08-28 (later still) — Order #1001 fulfilment attempted; mobile fix built on a copy

### Order #1001 — fulfilment attempted, and it revealed the real blocker

`fulfill_order` was run for order `45089149` after previewing the cost. The async operation
reported `completed`, but that is not the same as paid:

- `get_billing_invoices` shows invoice `3596885`, 2026-08-28 15:31 UTC, **$21.70, status `canceled`**.
- `get_order` still returns `status: Unfulfilled`, no tracking number.
- `get_billing_payment_methods` returns **`[]` — no payment method on file.**

So the order did not ship and **no money was charged.** The blocker is not the order, it is that
the Zendrop account has no payment method. Nothing else about the routing is wrong.

This matters beyond this one order: **every future customer order will fail the same way** until
a payment method is added. That is now the single hardest blocker on the store — a real sale
would take the customer's money and then not ship.

### The mobile buy button — fixed and measured, on an unpublished copy

Live theme `189462839609` was duplicated to **`189492035897` "Horizon — mobile buy fix
(2026-08-28)"**, role `UNPUBLISHED`, and the work was done there. The live theme was not touched
and nothing was published.

First attempt set `aspect_ratio` to `"square"`, which did nothing. Reading
`blocks/_product-media-gallery.liquid` showed why: the valid values are `adapt`, `1/1.25`, `1`,
`2/1` — `"square"` is not one of them, so Shopify silently fell back to `adapt`. Corrected to
`"1"`.

That alone only saved 55px, because the media was never the main problem. Measurement showed the
real cause: **five full-width stacked variant buttons.** `blocks/variant-picker.liquid` offers
`buttons` or `dropdowns`; switching to `dropdowns` collapses them into one control.

Final changes on the copy — all four are editor settings, no code:

| Setting | Live | Copy |
|---|---|---|
| `media-gallery.aspect_ratio` | `adapt` | `1` |
| `variant_picker.variant_style` | `buttons` | `dropdowns` |
| `product-details.gap` | 28 | 16 |
| `product-details.padding-block-start` | 24 | 12 |
| `accordion row_shipping.open_by_default` | true | false |

Measured on an iPhone 13 viewport (390×664), after full load and scroll to force lazy images:

| | Live | Copy |
|---|---|---|
| Product image height | 445px | **390px** |
| Title top | 574px | **511px** |
| **Add to cart top** | **1065px** | **749px** |
| Page height | 2285px | 1831px |

**The buy button moved 316px up.** It is still ~85px below a 664px fold, so this is a large
improvement rather than a complete fix — an honest phone visitor now scrolls a little instead of
a lot. Getting it fully above the fold would need the image smaller than square or the
announcement bar removed, both of which cost more than they gain.

Checked visually as well: `media_fit: contain` holds at a fixed aspect ratio, so **the product
image is letterboxed, not cropped** — the brush is shown whole.

Not published. Preview:
`https://pelumapets.com/products/peluma-3-in-1-mist-grooming-brush?preview_theme_id=189492035897`

## 2026-08-28 — Order #1001 paid and processing; the blocker is cleared

Merchant added a payment method. Verified rather than assumed:

- `get_billing_payment_methods` → **Mastercard •0657**, default, exp 04/2031.
- Re-ran `fulfill_order` (preview, then confirmed).
- `get_billing_invoices` → invoice **`3596898`, $21.70, status `paid`** — alongside the earlier
  `3596885` still showing `canceled`, the two side by side being a clean before/after of the fix.
- `get_order #1001` → status moved **`Unfulfilled` → `Processing`**, `fulfillment_date`
  2026-08-28T16:02:14Z, no issues.

`cost_details` is now populated, which only happens on a fulfilled order — the definitive
confirmation of the landed cost:

| | |
|---|---|
| product_cost | **$7.50** |
| shipping_cost | **$14.20** (Israel) |
| total_cost | **$21.70** |

`tracking_number` is still `null`; it appears when Zendrop dispatches.

**The store can now actually fulfil a paying customer.** That was not true this morning, and it
is the single most important thing that changed today.

Per the checklist added to `LAUNCH-READINESS`, the invoice status was checked separately from the
async operation result. Last time the operation reported `completed` while the invoice was
`canceled`; this time both agree.

Still open: **`Auto fulfillment` is toggled off** in the Zendrop orders screen, so every future
order waits for a manual Fulfill click. With a card now on file it can be switched on, which
means Zendrop charges automatically per order — the right setting for a store taking orders, and
worth turning on deliberately rather than by accident.

### Auto fulfilment on — the supply chain is now closed end to end

`get_store 3546333` confirms `auto_fulfillment_enabled: true`. Combined with the card on file,
an incoming order now routes to Zendrop, charges automatically and dispatches with no manual
step. **The full path from customer payment to supplier shipment works without intervention** —
the thing that was broken this morning.

Three other store settings visible in the same response, none of them blocking:

- `daily_fulfillment_enabled: false` — orders go out as they arrive rather than batched once a
  day. Faster; leave as is.
- `tracking_page_enabled: false` — no branded tracking page. Customers still get tracking by
  email from Shopify. Worth enabling later to cut "where is my order" messages, not urgent.
- `origin_country_hidden: false` — the origin country is visible to customers. **Left alone
  deliberately.** Hiding it would obscure where goods actually come from, which sits badly beside
  this project's rule against unsupported claims, and the store already states 12–18 day delivery
  honestly. Not recommended.

Remaining before the store can earn: **traffic.** Pinterest is prepared and unshipped, and is
the only thing left between this store and a first real sale.

### Tracking page enabled, in response to Zendrop's delivery disclaimer

Zendrop's first-order notice closes with:

> "Dropshipping suppliers are not logistics companies. We always use the best option for shipping
> your products but once it leaves our fulfillment center, it's the shipping company's
> responsibility to ensure speedy delivery."

So neither processing time nor delivery time is guaranteed. **The corrected product copy already
covers this** — "delivery to the United States *typically* takes a further 10–15 days" — and was
left alone rather than reworked again.

The real consequence is operational: unguaranteed delivery produces "where is my order" messages
and, left unanswered, PayPal disputes. The defence is visible tracking. So
`tracking_page_enabled` was turned on via `update_store_settings` (two-step, previewed then
confirmed) and verified with `get_store`:

```
auto_fulfillment_enabled : true
daily_fulfillment_enabled: false
tracking_page_enabled    : true   ← changed
origin_country_hidden    : false  ← deliberately unchanged
```

The preview confirmed `tracking_page_enabled` was the only field changing. **`origin_country_hidden`
was left `false` on purpose** — hiding where goods ship from would obscure a material fact from
customers, against this project's rule on unsupported claims. It is available in the same call
and was not used.

### Theme published by the merchant — verified live, and better than the preview showed

`themes` now reports `189492035897` as **`MAIN`**. Verified on the live URL with no preview
parameter, iPhone 13 viewport, after full load:

| | Before | Live now |
|---|---|---|
| **Add to cart top** | 1065px | **592px** |
| Page height | 2285px | 1831px |
| Variant control | 5 stacked buttons | `<select>` dropdown |

**Add to cart is now above the fold** on a 664px screen. The earlier preview measurement of 749px
was pessimistic — Shopify's preview bar occupies roughly 80px that does not exist on the
published theme. The real gain is **1065px → 592px**.

Shipping copy confirmed live in the page source:

> "Most orders are processed within 3 days, though occasionally longer, and delivery to the
> United States typically takes a further 10–15 days. You'll receive a tracking number by email
> as soon as your order ships."

The old "processed within 2–3 days" string returns zero matches — fully replaced.

`189462839609` ("Horizon — Peluma fixes (2026-08-27)") is now `UNPUBLISHED` and is the rollback
point if anything about the new layout proves wrong.
