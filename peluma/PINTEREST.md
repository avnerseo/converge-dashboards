# Pinterest — setup and first pins

Why this channel, from `DECISIONS.md`: strong visual category, static images only (filming is
not currently possible), no cost per click, and it compounds over weeks — the same clock the
2–3 week delivery runs on. It is the one channel that can start today.

The five pin images are rendered at 1000×1500 and delivered separately. Every line of text on
them is lifted from copy already live on the store — the homepage hero and the product
description. Nothing new was claimed.

## Before pinning: two setup steps

1. **Create a free Pinterest Business account** at `pinterest.com/business/create`. A personal
   account cannot see analytics and cannot run ads later.
2. **Claim the domain `pelumapets.com`** in Settings → Claimed accounts. This attributes every
   pin from the site back to the profile, unlocks analytics, and puts the logo on pins others
   save from the store. It is a meta tag or a DNS record — Shopify supports both.

Do the claim before pinning. Pins saved before the claim do not retroactively attribute.

## Profile

Pinterest weighs the display name in search, so it carries a keyword rather than only the brand.

| Field | Value |
|---|---|
| Display name | `Peluma \| Pet Grooming Essentials` |
| Username | `pelumapets` |
| Website | `https://pelumapets.com` |

**About:**

```
Simple grooming tools for cats and dogs — designed for easier routines and
a cleaner home. Free worldwide shipping on every order.
```

## Boards

Five boards, each a thing people actually search for rather than a product category. Board
descriptions are indexed, so each gets one.

**1. Cat Grooming at Home**
```
Brushing, de-shedding and coat care for cats — practical ideas for grooming
your cat at home without the mess.
```

**2. Dog Grooming at Home**
```
At-home dog grooming: brushing, de-shedding and coat care for short, medium
and long coats.
```

**3. Shedding Season Survival**
```
What actually helps when your cat or dog is shedding — brushing routines,
loose fur control, and keeping it off the furniture.
```

**4. Pet Hair & a Clean Home**
```
Keeping pet hair off sofas, beds and clothes. Tools and habits for a cleaner
home with cats and dogs.
```

**5. Peluma**
```
Our own grooming tools for cats and dogs.
```

Pin the product images to board 5 and to whichever of 1–4 fits. The same image on two relevant
boards is normal Pinterest behaviour; the same image on ten is spam.

## The five pins

Each links to the product page, except pin 1 which links to the homepage.

**Pin 1 — hero, cat and dog**
Link: `https://pelumapets.com`
```
Title: Groom smarter, enjoy a cleaner home

Peluma makes simple pet-care essentials for cats and dogs — tools that make
everyday grooming easier and keep loose fur under control. Free worldwide
shipping on every order.

#petgrooming #catgrooming #doggrooming #pethair
```

**Pin 2 — white brush**
Link: `https://pelumapets.com/products/peluma-3-in-1-mist-grooming-brush`
```
Title: A 3-in-1 mist grooming brush for cats and dogs

A fine mist helps reduce flyaway hair while soft silicone bristles brush and
massage the coat, helping collect loose fur as you go. Rechargeable, with USB
charging, and easy to clean after each session.

#groomingbrush #catbrush #dogbrush #petgroomingtools
```

**Pin 3 — purple pair**
Link: `https://pelumapets.com/products/peluma-3-in-1-mist-grooming-brush`
```
Title: Gentle enough for everyday grooming

Soft silicone bristles for gentle everyday use on cats and dogs. Rechargeable
with USB charging, in porcelain white, milk brown and purple.

#petgrooming #catcare #dogcare #groomingbrush
```

**Pin 4 — rolling lint remover**
Link: `https://pelumapets.com/products/peluma-3-in-1-mist-grooming-brush`
```
Title: For the fur that ends up on the sofa

A rolling lint remover, included with both Peluma sets. The brush handles the
coat, this handles everything the coat leaves behind.

#pethair #lintroller #catsofinstagram #cleaninghacks
```

**Pin 5 — shedding season**
Link: `https://pelumapets.com/products/peluma-3-in-1-mist-grooming-brush`
```
Title: Shedding season, handled

Suitable for cats and dogs with short, medium or long coats, and especially
useful during shedding season.

#sheddingseason #petgrooming #catshedding #dogshedding
```

## Cadence

Steady beats bursts. A handful of pins a week, spread out, does more than all five on day one
and nothing after. Pinterest surfaces pins for months, so the compounding comes from
consistency rather than volume.

Two things worth doing once the product physically arrives: photograph it properly, and make
new pins from those photos. The current five are built from supplier imagery, which is the
weakest asset in this whole setup.

## What is convention and what is measured

The structure above — business account, domain claim, keyworded display name and boards,
descriptions on everything — is standard Pinterest practice, not something measured for this
store. No performance is promised. The store has had no marketing traffic at all, so the first
weeks are the baseline, not a test of whether this works.

---

## Revision 2026-08-28 — install the Shopify app first, then pin

The two setup steps above (business account, manual domain claim) still stand, but the manual
claim is now the slow way round. **Shopify's free Pinterest app does more, in one flow.**
Verified before recommending:

- **Claims `pelumapets.com` automatically** — no meta tag to paste, no DNS record, no wait.
- **Syncs the product catalog** into Pinterest as a data source, which generates **organic
  Product Pins for free**. Prices, images and descriptions then update themselves — the feed
  refreshes every 24 hours, collections every 48.
- **Installs the Pinterest tag and the Conversions API**, browser-side and server-side, without
  editing theme files by hand.

Organic Product Pins cost nothing; only ads are paid. So the app produces a second, automatic
stream of pins alongside the five designed ones, and it is what makes any of this measurable.

**One thing to know before installing:** the app injects a meta tag into the live theme's head.
That is normal and it is the app doing it with the merchant's authorisation — but it is a write
to the live theme, so **the Shopify theme editor must be closed while it installs**, for the
same reason that rule exists everywhere else in this project.

Revised order:

1. Pinterest Business account.
2. Install the Pinterest app in Shopify — claim, tag and catalog sync all happen here.
3. Fill in the profile fields (below).
4. Create the five boards (below).
5. Upload the five designed pins with their copy (below).

Steps 1–2 are the ones that compound; 3–5 are the creative on top.

## Link check, 2026-08-28

Both pin destinations verified live, HTTP 200:

- `https://pelumapets.com`
- `https://pelumapets.com/products/peluma-3-in-1-mist-grooming-brush`

Live variants confirmed against the pin copy — Porcelain White Set $29.90, Milk Brown Set
$39.90, Porcelain White Brush $29.90, Purple Brush $29.90, Set $29.90. Pin 3 names porcelain
white, milk brown and purple, which matches. "Free worldwide shipping" appears on the live
product page, so the claim in pins 1 and 2 is copy that already exists on the store.

The pin images are committed at `peluma/pinterest-pins/pin-1.png` … `pin-5.png`, 1000×1500.

**Noted, not acted on:** the variant named simply **"Set"** carries no colour, which reads as
ambiguous next to four named variants. Traffic is about to land on this page for the first time,
so it is worth a decision — but it is the merchant's call and is not blocking the launch.

---

## Blocked by Israel: the Shopify app cannot complete setup (2026-08-28)

The Pinterest business account connected successfully, but the app's setup wizard stops there.
Observed directly in the Shopify admin:

```
✅ Your Pinterest Business account            avnerseo@gmail.com
⛔ Connect your Ad Account
⛔ Pinterest Tag and conversion measurement
   [Complete setup]  ← disabled
```

**The Pinterest Tag is step 3 and is gated behind the Ad Account.** An earlier note here
speculated the catalog might sync without an ads account; that was wrong — `Complete setup`
stays disabled until all three are green, and the app's own text says the merchant account
connection is what connects the catalog.

**Why the ad account is blocked:** Pinterest does not sell advertising directly in Israel. Since
August 2024 its sales partner there is **Aleph Israel**, covering 11 markets. Working with them
means signing a partnership contract, confirming ad account details and accepting the Pinterest
Advertising Service Agreement. The in-app request form promises a decision **within 3–4 business
days** by email.

The request form asks for a 12-month advertising spend figure and warns that "advertisers who do
not meet their spend threshold may not qualify to continue advertising on Pinterest" — so the
figure has to be a real intention, not a number chosen to pass review.

### What is genuinely unaffected

Verified against Pinterest's own documentation rather than assumed:

- **Claiming the domain** — Pinterest offers four independent methods (Google Merchant Center,
  HTML tag, HTML file, TXT record). None involve advertising.
- **Boards and organic Pins** — core account functionality, created on pinterest.com directly,
  not through the Shopify app.

So the entire traffic-generating half of the plan works today. What is deferred is measurement
precision and catalog automation.

### Measurement fallback, tested not assumed

Without the Pinterest Tag, attribution comes from Shopify's own analytics. Confirmed working:

```
FROM sessions SHOW sessions GROUP BY referrer_source SINCE -30d
direct  130 · search  5 · unknown  1
```

**Those 130 direct sessions are this project's own automated browser checks and admin previews —
real customer traffic is zero.** That is the baseline to measure against.

Pinterest traffic will appear under `social`, and the full funnel is available
(`sessions_with_cart_additions`, `sessions_that_reached_checkout`,
`sessions_that_completed_checkout`, `conversion_rate`). Less precise than the tag — it cannot
attribute a sale to an individual Pin — but sufficient for the only question that matters now:
**does Pinterest send people who buy.**

---

## Shipped 2026-08-28 — five Pins, five boards, live

All five Pins are published from the organic Pin builder, each creating its own board:

| Pin | Board | Destination |
|---|---|---|
| pin-1 | Peluma | homepage |
| pin-2 | Cat Grooming at Home | product page |
| pin-3 | Dog Grooming at Home | product page |
| pin-4 | Pet Hair & a Clean Home | product page |
| pin-5 | Shedding Season Survival | product page |

The plan originally put each Pin on two boards. That was dropped — a Pin is created on one board
and a second placement needs manual repinning, for no real gain. One board per Pin produces the
same five boards with half the work.

### Two traps hit along the way, recorded so they are not repeated

**`pinterest.com/pin-builder/` served the "Create Pin for ad" builder**, whose header reads
*Create Pin for ad* and which has **no board selector** — ad creatives do not live on boards.
Scrolling to the bottom looking for one is wasted effort. The organic builder is
`pinterest.com/pin-creation-tool/`, titled plainly **Create Pin** with *Working on: Your profile*.

**`Show similar products` was switched off on every Pin.** Its own description is "People can shop
products similar to what's shown in this Pin" — it surfaces *competitors'* products on our Pin.
There is no reason to hand traffic away on creative we paid attention to build.

Also set per Pin: `Tagged topics` (invisible to viewers, a free distribution signal), Alt Text,
comments left on, `Mark as AI-Modified` left off — the photography is genuine supplier imagery
with text composed over it, not AI-generated, so the label would have been inaccurate in the
other direction.

### Baseline at launch — measured, so the before/after is clean

```
FROM sessions SHOW sessions GROUP BY referrer_source SINCE -7d
direct  130 · search  5 · unknown  1     (social: absent)
```

Those 130 direct sessions are this project's own automated browser checks and the merchant's
admin previews. **Real customer traffic at the moment the Pins went live: zero, and `social` does
not appear at all.** Any `social` row that appears from here is genuinely Pinterest.

Note: `sessions_with_cart_additions` and `sessions_that_completed_checkout` fail when combined
with `GROUP BY referrer_source` in this store's analytics — query sessions by source first, then
the funnel separately.

### What to check, and when

Give it a week. Pinterest surfaces Pins over weeks, not hours, and five Pins on a new account
with no domain claim will start slow. The question at the first check is only whether `social`
appears at all — not what it converts.

## Pinterest ads are permanently closed for this store — and that resolves things

The Aleph request was submitted and **rejected outright**:

> "Unfortunately, advertisers must meet a **ILS 75,125 yearly minimum** to request to advertise
> on Pinterest."

That is roughly **$20,000 a year / $1,700 a month** in ad spend, as a *minimum to be considered*.
It is not a threshold this store will approach, so **Pinterest advertising is closed — not
pending, not "3–4 business days", closed.**

The ₪6,000 figure suggested here was an honest estimate of real intent and was far below their
floor. **Inflating it is not an option**: Aleph's own form warns that advertisers who do not meet
their spend threshold do not continue advertising, so a declaration the merchant cannot honour
risks the account for nothing.

### Three things closed at once, and none of them were wanted

| Closed | Why it does not matter |
|---|---|
| Pinterest paid ads | The margin analysis already showed paid traffic loses money at ~$10 net |
| The Pinterest Tag | Gated behind the ad account |
| Catalog auto-sync | Same gate |

**Pinterest's restriction and this store's economics agree.** Nothing was lost that the numbers
had not already ruled out.

**Pinterest here is organic, permanently.** That is exactly what was built — five Pins on five
boards, which distribute over weeks at no cost. Attribution stays with Shopify's session
analytics, already verified working against a clean zero-`social` baseline.

**Remove "waiting for Aleph" from every plan.** There is nothing to wait for.

### What this promotes

With paid Pinterest gone, **Google Shopping's free listings become the second free channel** —
and it is already installed with the product published to it since 2026-08-27. It has never been
verified. That check is now the highest-value open item after photography:

- All five variants have `barcode: null` — correct and permanent; Zendrop confirmed no GTIN
  exists for China-sourced goods, and fabricating one is forbidden.
- The `mm-google-shopping` metafield namespace is **empty** — no declaration that the product
  has no manufacturer identifier.

Without that declaration Google Merchant Center rejects a product for a missing GTIN, so the feed
is likely failing silently. Not fixed blind from here: the Google channel has changed how it
stores these settings across versions, and overwriting one it manages itself could make things
worse. The definitive check is the channel's own product status screen.

## Batch 2 — five more Pins, 2026-08-28

Five Pins is thin for a new account, and Pinterest rewards consistency over volume. This batch
gives a month of posting at 2–3 a week without needing anything new made.

Same visual system as batch 1, five different search intents, and **every claim traced to copy
already live on the store** — nothing new asserted.

| File | Board | Angle |
|---|---|---|
| `pin-6` | Peluma | the 3-in-1 feature |
| `pin-7` | Cat Grooming at Home | cats that dislike brushing |
| `pin-8` | Peluma | rechargeable, no batteries |
| `pin-9` | Dog Grooming at Home | coat types and colours |
| `pin-10` | Peluma | gift framing |

**Three supplier images had to be discarded**, caught by rendering a contact sheet and looking
rather than trusting filenames: two carry the supplier's own burnt-in English captions
("Sticky snack crumbs", "Stain from sofa hair dust") and one is a dimensions diagram with red
annotation boxes. A first render used two of them before the check — the images were selected
blind, which is the same failure mode as quoting a market price without reading the listing.
They are deleted from the working set so they cannot be picked up again.

### Copy

**pin-6** — `Three things, one brush`
```
Mist, brush and collect loose fur in a single pass. A fine mist helps reduce flyaway hair while
soft silicone bristles brush and massage the coat.

#petgrooming #groomingbrush #catgrooming #doggrooming
```

**pin-7** — `For cats who hate being brushed`
```
Soft silicone bristles that brush and massage, for gentle everyday use on cats and dogs.

#catgrooming #catcare #catsofinstagram #petgrooming
```

**pin-8** — `No batteries, just a USB cable`
```
Rechargeable with USB charging, and easy to clean after each grooming session.

#petgroomingtools #groomingbrush #petcare #catsanddogs
```

**pin-9** — `Short, medium or long coats`
```
Suitable for cats and dogs with short, medium or long coats, in porcelain white, milk brown and
purple.

#doggrooming #dogcare #petgrooming #groomingtools
```

**pin-10** — `A small gift for a dog person`
```
Both Peluma sets include the mist grooming brush and a rolling lint remover. Free worldwide
shipping on every order.

#dogmom #dogdad #petgifts #petgrooming
```

Links: `pin-6` … `pin-10` all point at
`https://pelumapets.com/products/peluma-3-in-1-mist-grooming-brush`.

**Cadence:** 2–3 a week, not all at once. Ten Pins posted over a month beats ten in a day.

## Catalogs is open without an ad account — the automatic-Pins path is alive

Tested after claiming the domain. **`pinterest.com/business/catalogs/` opens and works with no ad
account**, which contradicts the assumption made earlier from the Shopify app's gated wizard.
A retail catalog was created (`4860981355946`), and `Add a retail catalog data source` offers four
routes:

| Route | Status |
|---|---|
| **Provide a URL link** | ✅ **open** — Pinterest ingests a hosted feed daily |
| Upload manually | ✅ open — a file upload, no automation |
| **Connect to Shopify** | ❌ **circular** — redirects to the Shopify App Store listing for the Pinterest app, which is already installed and whose wizard is gated behind the Aleph-blocked ad account |
| Use Shopping API | needs developer credentials |

So the Shopify shortcut is genuinely closed, but **catalog ingestion itself is not**. The
`Provide a URL link` route needs a product feed in a format Pinterest accepts (CSV, TSV, or
RSS/Atom XML with real `id`, `title`, `description`, `link`, `image_link`, `price`,
`availability` fields).

**Shopify's native feed is not sufficient.** `https://pelumapets.com/collections/all.atom` returns
HTTP 200 and 4,081 bytes, and carries `id`, `link`, `title`, `s:type` and `s:vendor` — but the
price, image and description are buried inside an HTML table in `<summary>`, not exposed as
fields. Pinterest will reject it.

**Next step (not tonight):** install a free Shopify product-feed app that publishes a
Google-Shopping-format feed URL, then paste that URL into `Provide a URL link`. Once that
ingests, Product Pins generate and update themselves daily — prices, images and availability
included — and manual pinning stops being necessary.

### What was won tonight regardless

**The domain is claimed.** `pelumapets.com` now shows without the "claim" prefix on the profile.
That was done by appending the verification meta tag to `snippets/meta-tags.liquid` on a theme
copy, which the merchant published — confirmed live on `pelumapets.com`.

Claiming brings analytics on Pins that link to the site, correct attribution, and the Peluma logo
on Pins others save from the store. It is also the prerequisite for merchant review, which is why
`Begin review process` did nothing when clicked: **there is no catalog for it to review yet.** The
order is catalog first, review second — the reverse of what was assumed.

## Catalog feed built and validated — 2026-08-29

Pinterest's `Connect to Shopify` route is circular, so the feed was built **inside the theme**
rather than with a third-party app: a Liquid template that renders a Google-Shopping-format RSS
feed live from the store's own product data.

**`templates/page.pinterest-feed.liquid`** + a page at **`/pages/pinterest-feed`**.

```
https://pelumapets.com/pages/pinterest-feed
```

Why this over a feed app: it is **dynamic** — prices, stock and any new product appear
automatically — with no monthly fee, no third-party dependency, and no app that can break or
start charging. `{% layout none %}` is what lets a page template emit raw XML instead of the
site's HTML shell.

### Three defects caught by validating instead of assuming

1. **`g:price` and `g:sale_price` were identical.** Per the spec `price` is the list price and
   `sale_price` the current one. Fixed to emit `sale_price` only when a genuine compare-at exists.
2. **XML would not parse.** The `&` in `...jpg?v=...&width=1200` is illegal raw in XML. Fixed with
   `| escape` on both the image and item URLs.
3. **Description words ran together** — `coat.Why pet owners love it:Helps collect...` — because
   `strip_html` removes tags without inserting a space. Fixed by injecting a space before each tag
   first.

Each was found by parsing the output with a real XML parser, not by reading it.

### Pinterest's own validator: passed

Run through `Test your data source` with Currency `USD` and Country `United States`:

- **No errors.**
- One non-blocking **Alert 157**: `google_product_category` missing, which "may limit visibility
  in recommendations, search results and shopping experiences".

Added `Animals & Pet Supplies > Pet Supplies > Pet Grooming Supplies` on a further theme copy,
`189506421049`, and verified it renders. **The text path was used rather than the numeric ID
(6383)** — `google.com` is blocked by this environment's egress proxy so the official taxonomy
file could not be fetched to confirm the number, and a wrong ID would miscategorise silently
whereas a wrong path fails loudly.

### Sequencing note

The alert does not block ingestion, so the data source can be uploaded before the category ships
— the daily re-ingest picks it up on the next run. No need to hold the merchant on it.

### Data source connected — 2026-08-29

`Peluma Shopify Feed` is registered against `https://pelumapets.com/pages/pinterest-feed`,
format XML, United States / USD, ingesting every 24 hours.

**A snag worth recording:** the first attempt silently failed. `Test your data source` opens a
*separate* debugger screen, and returning from it loses the dialog — the form has to be filled
again and `Upload` pressed directly. Testing and saving are two different actions, and the test
is not a step in the upload flow. Since validation had already passed, the second attempt skipped
the test entirely and went straight to `Upload`.

**From here Pinterest pulls the catalog itself, daily.** Any product added to the store enters
Pinterest without manual work; prices and stock stay in sync on their own. Manual pinning is now
optional creative rather than the only route in.

### google_product_category shipped — 2026-08-29

`Horizon — feed category (2026-08-29)` published. Verified live on the feed: all five items now
carry `Animals & Pet Supplies > Pet Supplies > Pet Grooming Supplies`, XML still parses, prices
clean, all in stock. The storefront was checked in the same pass and is unaffected — product page
returns 200 with the buy button present.

This closes Pinterest's Alert 157. The next daily ingest picks it up.

## Batch 3 — two Pins for the Paw Wash Cup, 2026-08-29

The second product now has Pins. **Two, not three** — and the reason is the point of this entry.

| Pin | Board | Destination |
|---|---|---|
| `pin-11.png` | Paw & Nail Care | `/products/peluma-2-in-1-paw-wash-cup` |
| `pin-12.png` | Paw & Nail Care | `/products/peluma-2-in-1-paw-wash-cup` |

Destination verified HTTP 200. Both rendered on the same 1000×1500 template as pins 1–10 —
logo, image box, headline, subhead and footer measured against `pin-7.png` and matching it to
the pixel (footer width 275px in both).

### Copy

**pin-11** — `Turn it inside out. Now it's a bath brush.`
```
One soft silicone cup — a paw washer one way, a bath and grooming brush the other. Add a little
water, place the paw inside and turn gently.

#dogpaws #pawcare #petgrooming #muddypaws
```

**pin-12** — `Gentle on paws. Tough on mud.`
```
Soft silicone bristles that work around the pads and between the toes, lifting mud, sand and
dirt before it reaches the floor.

#pawcleaner #dogwalking #petgrooming #dogcare
```

### Why there is no third Pin

A third was built — a four-colour grid showing all the variants — and **rejected after looking at
it**. Every one of the eight supplier product photos carries a hanging paper tag for a different
brand (*Soft Gentle · HistoTree*). The only crop that removes the tag also removes the top of the
cup, and what is left reads as an abstract coloured blob. Unidentifiable products do not get
saved on Pinterest.

That leaves exactly **two usable frames** for this product: the lifestyle shot and a macro crop
of its bristles. Both come from the same single photograph.

**This is the photography blocker showing up as a hard limit on output rather than as an
abstraction.** It is no longer "our images are weaker than competitors'" — it is "we can produce
two Pins for this product and no more." Own photographs unlock colour Pins, size-comparison Pins,
in-use Pins, and the entire variant story, none of which can be made today.

## Pinning is automated now — 2026-08-29

**Claude can post Pins directly.** Four Pins went up in one pass with no merchant action:

| Pin | Board | Pinterest ID |
|---|---|---|
| `pin-11` Turn it inside out | Paw & Nail Care | `916552961685357448` |
| `pin-12` Gentle on paws | Paw & Nail Care | `916552961685357449` |
| `pin-6` Three things, one brush | Peluma | `916552961685357510` |
| `pin-7` For cats who hate being brushed | Cat Grooming at Home | `916552961685357509` |

Both Paw Wash Cup Pins came back with **`is_product: true`** — Pinterest matched the destination
URL to the claimed domain and the catalog, so they registered as **Product Pins**, which carry
price and availability and get richer placement than a plain image Pin.

`pin-8`, `pin-9` and `pin-10` are scheduled for **31 Aug, 2 Sep and 4 Sep at 19:00 Israel time**,
keeping the 2–3-a-week cadence rather than posting five at once.

### How, after it was written off

Earlier in the project `pinterest.com` was found blocked at the network gateway (403 on CONNECT,
organisation egress policy) and the whole channel was written off as merchant-only work. **That
conclusion was wrong, and the evidence to see it was already in this file:** MCP traffic does not
go through the container proxy — that is exactly why Zendrop and Shopify work here. Two known
facts, never connected, until the merchant pushed back.

The route is **`PINTEREST_CREATE_PIN` via the Composio MCP connector**, authorised once by the
merchant with a single OAuth click. Everything else is automatic.

### Two things that had to be solved along the way

1. **The `Paw & Nail Care` board did not exist.** It was named in this document as a destination
   but was never created — the account had five boards, none of them that one. Created via
   `PINTEREST_CREATE_BOARD` before pinning. Writing a plan is not the same as executing it, and
   this file asserted a board that was never checked.
2. **Pin images needed public URLs.** Base64 payloads are 600–830 KB, too large to pass inline.
   All seven Pins were uploaded to **Shopify Files** (`stagedUploadsCreate` → `fileCreate`),
   giving stable `cdn.shopify.com` URLs that Pinterest fetches directly. Shopify Files are
   separate from product media, so this does not touch the Google Merchant feed.

### Known risk on the scheduled Pins

The three scheduled Routines bind to this session so they inherit its Composio connection —
fresh-session Routines cannot carry connectors on this organisation, and the API rejects the
`connectors` parameter outright. **If a scheduled run reports no Pinterest tools, the Pin must be
posted manually from a live session.** Untested until 31 Aug.

## Carousel Pin shipped — 2026-08-29

A three-card carousel for the Paw Wash Cup, `creative_type: CAROUSEL`, Pinterest id
`916552961685358081`, on the **Paw & Nail Care** board. Each card carries its own title,
description and destination link.

| Card | Image | Line |
|---|---|---|
| 1 | lifestyle | *Muddy paws stop at the door* |
| 2 | bristle macro | *Soft silicone bristles* |
| 3 | four-colour grid | *Four colours, two sizes* |

### The card that was rejected as a Pin works as card 3

The four-colour grid was built earlier today and **thrown out** — cropped below the supplier's
hangtag, the cups read as abstract coloured blobs, and an unidentifiable product does not get
saved. As the third card of a carousel it works, because cards 1 and 2 have already established
what the object is.

**Sequence buys context that a single image has to earn on its own.** Same asset, opposite
verdict, decided by position.

## Image generation: what free tooling can and cannot do — 2026-08-29

The merchant challenged the assumption that new product imagery has to wait for the physical
product. Correct — and the assumption was lazy. Tested properly:

**Paid (OpenArt, `kling-3-omni` image2image, 10 credits):** removed the third-party
*Soft Gentle · HistoTree* hangtag and its carabiner cleanly, rebuilding the ribbed bands, raised
dots and tie-dye gradient underneath. No text, no logo. **The result is a reconstruction, not a
retouch** — the silhouette shifts slightly and the background greys off. Fine for marketing
creative; not yet trusted as the primary catalogue image, which must represent the product
exactly.

**Free (OpenCV, two attempts):** both failed, and the failures are recorded rather than hidden.

| Method | Result |
|---|---|
| Telea / Navier-Stokes inpainting | Smeared the upper cup; NS pushed a white streak through the body |
| Symmetry reconstruction (mirror about the cup's centre) | Covered only 29% of the hole; the fallback pulled the tag's green into the fill |

**Why:** the masked region is 9% of the frame and sits **on the product's outline**, not on flat
background. Classical inpainting continues texture; it cannot invent shape.

**So the split is:** templates, typography, carousels, composition and publishing are free and
already automated. Removing the hangtag is not — it costs ~10 credits per image, 80 for the set.

### A blocked CDN, routed around legitimately

`cdn.openart.ai` is blocked by the same egress policy as `pinterest.com`, so generated images
cannot be downloaded here. **Shopify fetches `originalSource` URLs server-side**, so passing the
OpenArt URL to `fileCreate` pulls the image into Shopify Files, from where its `cdn.shopify.com`
URL is readable. Pinterest fetches image URLs the same way. The pipeline
**generate → Shopify → Pinterest** therefore runs end to end without the container ever needing
to reach the blocked host.

## Real Pinterest search data — 2026-08-30

`PINTEREST_GET_KEYWORD_TRENDS` (US) is available through the connector. Until now every line
of Pin copy was written from intuition. This is the first time the copy has been measured
against what people actually search.

### Method note that matters

By default each keyword's series is normalized **to its own peak**, so cross-keyword
comparison is meaningless — it only shows shape. `normalize_against_group: true` normalizes
all keywords against a shared peak, and only those numbers are comparable. The first read of
this data was done without the flag and produced a wrong conclusion (see the correction below).

### Finding 1 — the terms the current Pins target do not rank at all

Queried for: `dog grooming at home`, `cat grooming at home`, `dog shedding`, `cat shedding`,
`muddy paws`, `paw cleaner`, `dog grooming tools`, `pet grooming brush`, `dog mom gifts`.

**Not one of them returned a row.** They are outside Pinterest's ranked top-50 US monthly
trends — too little search volume to rank. `pin-6` through `pin-12` are all written around
this vocabulary.

### Finding 2 — "dog grooming" has no season (this corrects an earlier reading)

Group-normalized, `dog grooming` sits at **7–11 all year**, currently 8. On the
self-normalized series it looks like it peaks hard in late December, and that was first read
here as "the brush's season is Dec–Jan". It is not. In comparable units the swing is 8 → 10,
about 25% — a wiggle, not a season. No grooming spike is coming for the brush.

### Finding 3 — the category's real seasonal mass is Christmas, and it is 3–10x grooming

Group-normalized peaks:

| keyword | annual peak | when | intent |
|---|---|---|---|
| `dog christmas pictures` | **100** | 17 Nov | inspiration |
| `dog christmas photoshoot` | 28 | 15 Dec | inspiration |
| `dog christmas card` | 27 | 22 Dec | inspiration |
| `dog christmas` | 23 | 8 Dec | mixed |
| `dog christmas gifts` | 18 | 8–22 Dec | **shopping** |
| `dog gifts` | 11 | 15 Dec | **shopping** |
| `dog grooming` | 10 | flat | mixed |

The huge terms are photo-inspiration intent and will not buy. The shopping slice —
`dog christmas gifts` and `dog gifts` — is an order of magnitude smaller than the photo terms
but still roughly **2x the grooming baseline at peak**, and it is the only place in this
category where demand multiplies rather than trickles.

`dog gifts` runs 1–2 for ten months and hits 11 in mid-December: an **~8x** swing.

### What this changes

1. Grooming vocabulary is a steady trickle with no upside spike. Keep the Pins; stop
   expecting them to break out.
2. The one genuine demand event of the Peluma year is **10 Nov – 22 Dec**, framed as gifting,
   not as grooming.
3. That is ~10 weeks out, and Pinterest needs roughly 4–8 weeks to index a Pin and build
   distribution. **Building gift-framed Pins now lands exactly on the ramp.** Building them in
   November is too late.
4. `pin-10` was already gift-framed and was treated as a one-off. That instinct was right and
   should become the main axis for the next batch.

### Caveat kept honest

These are search-volume trends, not conversion data. They say where attention goes, not who
buys. Nothing here has been validated against a Peluma sale, because there has not been one.
