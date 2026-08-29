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
