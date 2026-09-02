# Peluma — start here

**Read this file first. It is the current state of the business.** The other files in this
folder are append-only logs of how it got here; this one says where it is.

Last verified end to end: **2 September 2026.**

---

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

### Products

| product | id | status | buyable |
|---|---|---|---|
| Peluma 3-in-1 Mist Grooming Brush | `10320315810105` | ACTIVE | **yes**, all 5 variants |
| Peluma 2-in-1 Paw Wash Cup | `10323824017721` | ACTIVE | **no** — supplier out of stock |

### Brush variants, prices and economics

Pricing rule now in force: **one item $29.90, two items $39.90.** No compare-at anywhere.

| variant | SKU | price | landed | contribution |
|---|---|---|---|---|
| White brush | `MDYQJZF3J` | 29.90 | ~11 est | ~17.7 |
| Purple brush | `ZAF7RY7XJ` | 29.90 | ~11 est | ~17.7 |
| White brush + lint roller | `PE17TFL2V` | 39.90 | **21.70 invoiced** | **16.74** |
| Milk brown brush + lint roller | `1O3NPE8` | 39.90 | ~21.70 | ~16.74 |
| Two brushes - white + milk brown | `Z75Y6C7M0` | 39.90 | ~21.70 | ~16.74 |

Paw cup: `$16.90`, landed `$7.65` (S) / `$8.56` (L), NexoraUSA, ships $0 in 6 days. Dead
until restock.

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

| # | blocker | owner | why it matters |
|---|---|---|---|
| 1 | **No card field at checkout.** PayPal only, and its first transaction failed. PayPlus account exists, service not activated. | merchant — phone call | The November test is uninterpretable if run with a known checkout handicap. |
| 2 | **Paw cup out of stock at supplier.** | Zendrop — "Notify Me" | Half the catalogue, and 7 of 16 Pins point at it. |
| 3 | **Sold-out cup appears 7× on the homepage.** | merchant — theme edit | First thing a visitor sees. Assistant may not touch the theme. |
| 4 | **No photograph of the real product in a real hand.** | waiting on delivery | No demo, before/after or testimonial ad exists without it. |
| 5 | Zendrop UBB $29/mo with zero orders | merchant — ask to downgrade | ~$116 saved before the window. |

---

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

The store is no longer the problem. Products are clean, copy is honest, prices are coherent,
six social and feed channels are wired. **What it has never had is a single real customer.**

Every number in this document except one is a model. The exception is order `#1001`, which the
merchant placed himself.

The structural fact, arrived at from four independent directions: **these products have no
defensibility.** eBay sells the same generic brush at $8.99–$16.94; Peluma asks $29.90. That
works only if brand or content is worth the gap, and there is no evidence yet for either.

So the plan is a **single dated test**: the gifting window, **10 Nov – 22 Dec**, run on free
organic Pinterest, with a working checkout and real product photography.

**If that window passes with real content, buyable products and a card field, and still
produces nothing — the answer is the product, not the marketing.** That converts "will this
work" from an argument into an experiment with a date.

Standing gate: **no video production until there is footage of the real product in a real
hand.** Generating more AI clips is spending effort on an asset that will not convince anyone.

---

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
