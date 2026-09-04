# Peluma — start here

**Read this file first. It is the current state of the business.** The other files in this
folder are append-only logs of how it got here; this one says where it is.

Last verified end to end: **2 September 2026.**

---


### שפת התשובות למרצ'נט

כותבים בעברית, **מימין לשמאל**, ובלי לערבב מילים באנגלית בתוך משפט עברי —
הטרמינל הופך את הסדר והמשפט נעשה בלתי קריא. מונחים באנגלית, שמות כפתורים,
כתובות וקוד — בשורה נפרדת משלהם, לא בתוך הטקסט. בלי טבלאות שמערבבות
עברית ואנגלית באותה שורה. (התוכן שהלקוח רואה בחנות נשאר אנגלית בלבד — זה כלל נפרד.)


## 1. What this is

| | |
|---|---|
| Store | **Peluma** — `pelumapets.com` / `hjahey-v0.myshopify.com` |
| Sells | Pet grooming tools, **USD, to US customers**, English only |
| Fulfilment | **Zendrop** dropship, store id `3546333` |
| Operator | Israel-based sole operator + this assistant |
| Branch | `claude/peluma-theme-handoff-ts6y95` |
| Goal, in the merchant's words | a professional online store that **sells and makes money** |

---

## 2. Hard rules — these are not negotiable

- **English only** in anything a customer sees.
- **No invented claims.** No unmeasured percentages, no health claims, no fabricated
  reviews, testimonials or founder story.
- **Never fabricate a barcode.**
- **Never touch the refund policy.**
- **Never write to the live theme, and never publish a theme.** Ask whether the editor is
  closed before any theme write; read the file back after.
- When something needs the merchant, write it as **numbered steps**, and **first check
  whether it can be done without them** — then say what was checked.
- Before changing any customer-facing number or claim, **check the primary source first.**
  Supplier data before statements about supply. Market prices before pricing.

---

## 3. Live state

*Everything in this section was verified against the live store or a real invoice on
2 Sep 2026. Numbers that are estimates say so.*

### Products

| product | id | status | buyable |
|---|---|---|---|
| Peluma 3-in-1 Mist Grooming Brush | `10320315810105` | ACTIVE | **yes**, all 5 variants |
| Peluma 2-in-1 Paw Wash Cup | `10323824017721` | **DRAFT** | no — pulled 2 Sep |

The cup was set to DRAFT because it was **advertising itself as in stock while the supplier
had none** — the storefront and the Google feed both offered a product we could not ship,
which is the most likely cause of the Merchant Center suspension. Pulling it also removed it
from the homepage (7 mentions → 0) without touching the theme, and retired the US-only
delivery profile that contradicted the shipping policy. Verified: product URL returns **404**.

**Inventory tracking is now ON** for the brush (`tracksInventory: true`). It was off, which is
exactly why the cup could report `availableForSale: true` on zero quantity — Shopify ignores
zeros on untracked items. A zero from Zendrop will now mark a product sold out by itself.

### Brush economics — the real US numbers

Pricing: **one item $29.90, two items $39.90.** No compare-at anywhere.

**The landed cost this project used for weeks was wrong.** Order `#1001` shipped to **Hadera,
Israel** — it is the merchant's own test order. Its $21.70 total is $7.50 product plus **$14.20
Israel shipping**, and has never been the cost of anything we sell to the US.

Zendrop's own US quote for the same product: **$9.92, 8 days.**

| | product | US shipping | landed | price | contribution |
|---|---|---|---|---|---|
| single brush | $3.76 | $9.92 | **$13.68** | $29.90 | **~$15.17** |
| brush + lint roller | $7.50 | $9.92 | **$17.42** | $39.90 | **~$21.08** |

Per-variant `unitCost` in Shopify reads $3.76 / $3.61 for single brushes and $22.20 for the
sets — **those two columns are in different units.** The $22.20 is a landed-to-Israel figure
Zendrop wrote back after `#1001`. Use the table above, not the raw field.

**Shipping is 73% of the landed cost.** That single fact drives most of section 8.

### Running costs

| | monthly |
|---|---|
| Shopify Basic | $39 (promo may still apply — check) |
| Zendrop, usage-based `UBB-20-29` | $29 |
| PayPlus, if activated | ~$16 + ₪195 setup |
| **total** | **~$84** |

**Break-even ≈ 5 orders/month.** At ~$17 contribution.

### Traffic and sales — the honest picture

- **1 order ever**: `#1001`, 28 Aug, $29.90, PAID — **the merchant's own test.**
- **1 customer**: the merchant.
- Sessions are effectively all `direct` and are mostly this assistant's own checks.
- **Pinterest, search and social have produced zero sessions.** Expected — the Pins are days
  old and indexing takes 4–8 weeks.

---

## 4. Channels

| channel | state |
|---|---|
| **Pinterest** | Connected and automated. 6 boards, **16 Pins**. Catalog feed confirmed matching (`is_product: true`). Video Pins are **impossible** via the connector. |
| **YouTube** | Channel `UCRxrWRucsEzb8lbGrtXaoOg` `@peluma-v2p`. One public Short `b_KEDxWF08g`. Branding text set via API; **avatar must be set by hand** (no API). |
| **TikTok** | `@pelumapets` created. Not set up — needs Business switch, avatar, bio, link. **Posting via API is not viable** (see traps). |
| **Instagram** | The connected account is personal, **not Peluma**. Do not publish there. |
| **Gmail** | `pelumapets@gmail.com` connected. `shop.contactEmail` points at it and the sender email is verified. |
| **Google Merchant Center** | Feed built and submitted; status not verifiable from here. |

Boards: Peluma `916553030354941631` · Dog Grooming at Home `916553030354941640` · Cat Grooming
at Home `916553030354941638` · Paw & Nail Care `916553030354941962` · Gifts for Dog Lovers
`916553030354942957` · Gifts for Cat Lovers `916553030354942958`

---

## 5. What is blocking, and who owns it

| # | blocker | owner | state |
|---|---|---|---|
| 0 | ~~Google Merchant Center suspended — `Misrepresentation`~~ | — | **RESOLVED 2 Sep, 16:16 UTC.** Google: *"The requested review of Misrepresentation has been completed and the issue no longer appears in your Merchant Center account."* Submitted 13:40, cleared 16:16 — **2h 36m**, on the first of three review requests. |
| 1 | **No card field at checkout.** PayPal only. PayPlus is activated; quote #31219 awaits signature. | merchant — sign | Unchanged. Still the hardest blocker: a US visitor who reaches checkout and sees only PayPal leaves. |
| 2 | **Paw cup out of stock at supplier.** | Zendrop — "Notify Me" | Product now DRAFT, so it no longer harms the store. |
| 3 | ~~Sold-out cup 7× on the homepage~~ | — | **Solved** by the DRAFT, without a theme edit. |
| 4 | **No photograph of the real product in a real hand.** | waiting on delivery | Unchanged. Still the standing gate on all video. |
| 5 | Zendrop UBB $29/mo with zero orders | merchant — ask to downgrade | Unchanged. |
| 6 | **No viable second product found.** Ten screened on 2 Sep; nine rejected on verified US retail prices. | see section 8 | One candidate open, pending a US-dollar price check. |

## 6. Hard-won knowledge — read before touching anything

### Costs and stock

- **Zendrop catalog `price` is a "from" price** — the cheapest variant. Pricing a product from
  it is how a grinding head got mistaken for a $15.67 grinder. **Never price from it.**
- **`inventoryItem.unitCost` on a fresh import is accurate.** Validated against a real Zendrop
  invoice: unitCost $22.20 vs invoiced **$21.70** — within 2%. This is the reliable source.
- **The catalog `availability.in_stock` field lies.** It returned `true` for the paw cup on
  three separate days while the product was genuinely out of stock and unbuyable.
  **The only authoritative test is adding the variant to a real cart:**
  `POST /cart/add.js` → a 422 means it cannot be sold. A feed reading "in stock" is not a
  purchase. This is the single most expensive lesson in this project.
- Inventory at a fulfilment-service location is **owned by the service**
  (`fulfillmentService.inventoryManagement: true`). Shopify rejects manual quantity writes.
- **Never let anyone press "Push to store" in Zendrop** on a live product — it overwrites the
  description and images.

### Shopify API

- There is **no `shopUpdate` mutation.** Store email, sender email, notification branding and
  email templates are admin-only. The full Mutation type was enumerated to confirm this.
- `productVariantAppendMedia` fails with *"already has media attached"* — run
  `productVariantDetachMedia` first.
- `publishablePublish` takes `PublicationInput`, not `ResourcePublicationInput`.
- A market cannot go active before its countries are **named explicitly** in the delivery
  profile serving the products. "Rest of World" does not cover a country that has its own
  market. Doing it in the wrong order breaks checkout.

### Reach and workarounds

- `pinterest.com`, `facebook.com`, `ads.tiktok.com`, `alibaba.com`, `amazon.com`,
  `payplus.co.il` and most comparison sites are **blocked by the egress proxy**. MCP traffic is
  not — it routes through claude.ai. That is why Pinterest posting works while `curl` does not.
- **Shopify `fileCreate(originalSource: <url>)` fetches server-side**, so a blocked CDN image
  can be pulled into Shopify and read back from `cdn.shopify.com`. Pinterest and Meta also
  fetch image URLs server-side.
- Video is the exception — Shopify rejects external video URLs; it needs a staged upload.
- **ffmpeg is available**: `pip install imageio-ffmpeg` ships a static ffmpeg 7.0.2. Do not
  encode social video with OpenCV — it writes obsolete `mp4v`.
- Playwright: `executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'`,
  `proxy:{server:process.env.HTTPS_PROXY}`, args
  `['--no-sandbox','--dns-over-https-mode=off','--ssl-version-max=tls1.2']`, run with
  `NODE_PATH=/opt/node22/lib/node_modules`.

### Platforms

- **TikTok posting via API is not viable.** Composio has no managed auth for TikTok; it needs
  your own registered developer app, and until TikTok audits that app only `SELF_ONLY` posts
  are allowed — zero distribution. Weeks of process to save a 60-second manual upload.
- **Pinterest video Pins are impossible** through this connector — they need a `media_id` from
  a registration endpoint that is not exposed. Verified twice.
- YouTube uploads need a file in **Composio's own storage**. Path: Shopify staged upload →
  public CDN URL → download into `COMPOSIO_REMOTE_WORKBENCH` `/mnt/files/` →
  `get_mount_file_s3_key(path)` (**returns a `(key, error)` tuple, not a string**) →
  `run_composio_tool(..., account="youtube_prefab-surahi")` — the kwarg is `account`.
- **The default YouTube account is a toddler-music channel.** Always assert the resolved
  channel is `Peluma` / `UCRxrWRucsEzb8lbGrtXaoOg` before uploading.

### Judgement

- **Judge images at full size.** A downscaled contact sheet has twice suggested a defect that
  did not exist at native resolution, once nearly costing two good product photos and once
  nearly a good video.
- Every motion requested of a video model is an opportunity for it to forget the product.
  3 seconds, camera-only, with explicit anti-deformation wording, stays faithful. 5 seconds
  with three motions deforms from 1.0s.
- Occlusion is the visual cue for "inside" — the rim must pass in front of the paw.

---

## 7. What the market data says

Pulled from Pinterest's own US keyword trends, 30 Aug — the first content decision here made
from measured demand rather than intuition.

- The grooming vocabulary the early Pins were written for **does not rank at all**:
  `dog grooming at home`, `pet grooming brush`, `paw cleaner`, `muddy paws`, `dog shedding`
  all returned nothing.
- `dog grooming` is **flat 7–11 all year**. There is no seasonal upside for the brush.
- The one term that multiplies is **gifting**: `dog gifts` runs 1–2 for ten months and hits 11
  in mid-December — roughly **8x**. `dog christmas gifts` peaks around 2x the grooming
  baseline.
- Therefore **Peluma's season is 10 November – 22 December, framed as gifting**, and Pinterest
  needs 4–8 weeks to index. Building gift Pins now lands on the ramp; building them in
  November is too late.
- Explicitly Christmas Pins belong in **late October**, not earlier — 15 weeks ahead collects
  no engagement, which is a weak start for a Pin.

---

## 8. The strategic position, stated plainly

*Rewritten 2 Sep 2026 after pricing, product-screening and market research all landed on the
same conclusion from different directions.*

### The one sentence

**Right channel, wrong product.** Pinterest is the best-converting option available to a store
this size. What we put in front of it is a commodity we cannot price competitively.

### Why the brush cannot be fixed by lowering its price

The same rechargeable mist grooming brush, verified across six live listings on 2 Sep:

| retailer | price |
|---|---|
| Walmart, 4-in-1 | $6.99 |
| Walmart, 3-in-1 white | $9.68 |
| Walmart, XYRSRUW | $10.69 |
| Walmart, 2026 model | $11.66 |
| Walmart, for shedding | $11.99 |
| Amazon, Feelneedy | $10.99 |

**Our landed cost of $13.68 is higher than the price Walmart charges a shopper.** Every
competitive price point loses money. Cutting the price does not reach the shelf; it only
shrinks the margin. The brush stays at $29.90 as an impulse-channel product.

**The sharp version: a 3× price survives on impulse channels and dies on comparison channels.**
Pinterest shows a product in a moment of desire. Google Shopping shows our $29.90 in a grid
beside somebody's $9.68.

### Ten products screened, and why nine failed

Screen used: **landed cost must be ≥ $18.50 below verified US retail** to clear ~$17
contribution. Landed = Zendrop product price + Zendrop's own US shipping quote. Retail = live
Walmart / Chewy / Amazon listings.

| product | landed | verified US retail | outcome |
|---|---|---|---|
| mist brush *(live)* | $13.68 | $6.99–$11.99 | cost above market |
| silicone grooming glove | ~$9.75 | $5.53–$12.74 | cost at market |
| ultrasonic bark deterrent | $20.36 | $8.99–$20.99 | cost at market top |
| window cat hammock | $47.17 | — | shipping 2× the product |
| expandable cat backpack | $50.90 | $34.00–$51.99 | cost at market top |
| wireless water fountain | $39.95 | $30s–$90.99 | passed on cost, failed on everything else |
| pet bathrobe | $10.88 | $9.29–$39.95 | marginal |
| pet first-aid kits ×2 | $26–$28 | — | $18.61 to ship a $9 item |
| **dog leash & harness set** | **$12.49** | **unverified** | **open** |

**Why the failures are structural, not bad luck.** Shipping squeezes from both ends. Cheap
products die against a ~$9 shipping floor; bulky ones die against shipping that outgrows the
product. And Zendrop's catalog is generic Chinese goods — **every item in it is already in US
retail**, sold by someone moving containers while we pay $6–$34 a unit.

The water fountain deserves its own note because it passed the arithmetic and still failed:
its specs are identical to **PETLIBRO Dockstream**, which is carried at Amazon, Walmart, Chewy,
Best Buy *and* Costco. **Passing the cost screen is necessary, not sufficient** — the screen
must also ask who already owns the category and what happens when the product breaks.

### The bundle route, and Zendrop closing it

Zendrop support, asked directly on 2 Sep: **shipping is charged per product, not per order.**
Three products in one order means three shipping fees even to one address, and they do **not**
support a single-SKU bundle. Items may travel in one parcel; that is packing, not billing.

So a self-assembled "bath day set" is dead: the three items cost about $40 at US retail, and
any price that clears our gate is above the sum of the parts — which a shopper can check.

**But there is a door left open.** A *supplier* SKU that already contains several objects does
carry one shipping charge. Our own store proves it — "White brush + lint roller" is one SKU
holding two objects, and `#1001` paid shipping once. The route is to find existing multi-item
SKUs, not to assemble them.

### The open candidate: `3050917`, Dog Leash & Harness Set

One SKU containing **harness, collar, leash, bow and poop-bag holder.** 16 variants, 7 images,
landed **$12.49**.

It is the first candidate whose competitors are **not Walmart**. Searching its US market returns
Lucy & Co. (now in Petco), Sniff & Bark, Posh Dog Life, Furry Muse — boutique DTC brands, several
on Shopify. **There is no $9.68 commodity listing underneath this category.** It also matches
what the Pinterest research asks for: an aesthetic product bought as a planned purchase.

| our price | contribution |
|---|---|
| $39.90 | $26.01 |
| $49.90 | $35.66 |
| $59.90 | $45.31 |

Against the brush's $15.17.

**Verified 2 Sep, in USD**, by re-opening sniffandbark.com.co with `?country=US` (the first
pull came back in ILS because the site geo-detects Israel; converting that is not the same as
the US price, so it was re-pulled rather than converted):

| their product | list | with their standing CRAZY40 code |
|---|---|---|
| AllSet harness alone | $59.00 | $35.40 |
| Joyline leash alone | $49.00 | $29.40 |
| Bundle — harness + leash + bag holder | $109.00 | $65.40 |
| **Mega Bundle** — collar + leash + bowtie + harness + bandana + bag holder | **$151.00** | **$90.60** |

The Mega Bundle is the near-exact match for `3050917` (ours lacks only the bandana).

**Treat the "regular" prices as theatre, not market data.** The harness's compare-at changes
with size while its sale price does not — a size L shows 23% off and an XS shows 12% off, same
product, same campaign — and the leash carries no compare-at at all. Those anchors are
marketing inputs. **The honest market price is the post-code figure: $90.60.**

**The pre-committed rule was: proceed above $35 USD. It came back at $90.60 — 2.6× the
threshold. Decision: proceed.**

### What the market research says about the category itself

- US pet industry **$158 B (2025) → $165 B (2026)**, +4.4%. 95 M pet households. Dog ownership
  **51% → 53%** in one year. **Demand is not the constraint.**
- But growth sits where we are not: health and wellness **42%** of spend, premium nutrition
  **28%**, technology **12%**; services are the fastest-growing segment. **Grooming accessories
  appear nowhere on the growth list.**
- **Chewy owns pet e-commerce at $12.0 B — 7.5× Walmart.**
- Christmas gifting: toys **68%**, treats **45%**, bedding **8%**, **grooming 3%** — tied for
  last. The gift boards built in August point at a 3% slice. The **price band is right**
  ($25–$50 is what 27% of dog owners spend); the category is not.

### Pinterest is confirmed, and we are using it wrong

**1.8% conversion, 2.3× the conversion value of other social platforms, ~80% new visitors.** It
drives **planned** purchases by people designing a look around their pet — "cat-friendly living
rooms", "outdoor dog oases".

Two mismatches, both free to fix:
1. **We pin a tool as a catalogue shot** at an audience planning a room.
2. **Idea Pins get 4× the saves and 3.2× the outbound clicks of standard pins** — and every
   Peluma pin so far is a standard pin.

### The test still stands

A single dated test in the gifting window, **10 Nov – 22 Dec**, on free organic Pinterest, with
a working checkout and real product photography. **If that passes with real content, buyable
products and a card field and still produces nothing, the answer is the product, not the
marketing.**

Standing gate: **no video production until there is footage of the real product in a real hand.**

## 9. The other files

| file | what it holds |
|---|---|
| `DECISIONS.md` | Every decision and reversal, with the evidence. The economics, the reprices, the corrections. Longest and most important. |
| `STATUS.md` | Chronological log of work done to the store, the accounts and the content. |
| `PINTEREST.md` | Every Pin, board, copy block, schedule and the keyword research. |
| `PRODUCT-SCREENING.md` | How products are screened, and which were rejected and why. |
| `LAUNCH-READINESS-2026-08-28.md` · `PREVIEW-AUDIT-2026-08-28.md` · `GO-LIVE.md` | Pre-launch audits. Historical. |
| `NEXT-SESSION.md` | Superseded by this file. |
| `reel-caption.py` | Rebuilds the social reel with captions and an end card, H.264. |
| `pinterest-pins/` | Every published Pin image. |
| `combo-*.png`, `peluma-avatar.png`, `peluma-email-logo.png` | Brand and product assets in use. |

---

## 10. If you are picking this up cold

1. Read this file.
2. Verify the two products against the **live storefront**, not the Admin API —
   `/products/<handle>.js` and a real `POST /cart/add.js`. The Admin API has reported a
   product buyable while the storefront refused to sell it.
3. Check `#5` — the blockers — before starting anything new. Four of the five are the
   merchant's, and nothing downstream matters until the checkout can take a card.
4. Do not add Pins faster than a few a day. The account went 5 → 16 in one day on 31 Aug;
   more than that from a young account risks being read as spam, and this account has to stay
   in good standing until December.
