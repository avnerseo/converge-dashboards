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
