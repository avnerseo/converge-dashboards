# Storefront preview audit — theme 189462839609

Date 2026-08-28. First session in which the storefront was actually rendered in a browser.
Theme identity confirmed in-page on every load:

```
Shopify.theme = {"name":"Horizon — Peluma fixes (2026-08-27)","id":189462839609,
                 "schema_name":"Horizon","schema_version":"4.1.4","role":"unpublished"}
```

Nothing was written to any theme in this session. Read-only throughout.

## How the browser was unblocked

Egress now permits `pelumapets.com`, `*.myshopify.com` and `cdn.shopify.com` — `curl` returns
`200`. Chromium still failed with `ERR_CONNECTION_RESET` on every allowed host. Cause, from a
Chromium net-log: the CONNECT tunnel is established (`HTTP/1.1 200 Connection Established`) and
the gateway then resets the TLS handshake on Chromium's 1783-byte ClientHello. The size comes
from Chrome's post-quantum key share; the `--disable-features=PostQuantumKyber` / `UseMLKEM`
flags no longer shrink it in Chrome 141.

Working launch flags — TLS verification stays **on**, only the TLS version is capped, which
drops the ClientHello to 201 bytes:

```js
chromium.launch({
  executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  proxy: { server: 'http://127.0.0.1:35017' },
  args: ['--no-sandbox', '--dns-over-https-mode=off', '--ssl-version-max=tls1.2'],
})
```

Preview an unpublished theme by loading `https://pelumapets.com/?preview_theme_id=189462839609`
once; the cookie carries the preview across the whole session, checkout included.

Still blocked, and it matters below: `checkout.pci.shopifyinc.com`, `www.paypal.com`,
`checkout.shopify.com`. Those are checkout's own payment hosts.

## Verified working

- **Add to cart → cart → checkout completes on both viewports.** A real checkout session was
  reached on desktop (1440×900) and on an iPhone 13 viewport. `/cart.js` returned
  `item_count: 1`, `total_price: 2990`, correct variant title. No console errors originating
  from theme code — every failed request was an analytics or payment host blocked by egress.
- **No horizontal overflow** at 1440px or 390px. `scrollWidth === clientWidth`.
- Announcement bar renders as `<p>` at **14px, `rgb(0,0,0)`, weight 400** — supporting text,
  not a headline. The magenta is gone. This one is settled.
- Every earlier fix is visible on the rendered page: real `<h1>` in the hero, white subheading,
  solid black fit-content CTA, centred hero content, `Shop Peluma` heading, no footer social
  icons, no cart recommendation, the three-row accordion below the buy buttons with the single
  corrected 12–18 day shipping paragraph, and the rewritten newsletter line.
- **Desktop scrolling is not broken.** `html`/`body` compute to `overflow:hidden; height:900px`,
  which looks alarming, but it is Horizon by design: `base.css` sets
  `@media (min-width: 990px) { html:has(.page-wrapper), html:has(.page-wrapper) body
  { height: 100dvh; overflow: hidden; } }` and scrolls `.page-wrapper` instead
  (`scrollHeight 1420`, `overflow-y: auto`). The live theme behaves identically. Any future
  automation must scroll `.page-wrapper`, not `window`, or it will screenshot only the first
  viewport and conclude the page is empty.

## Defects found

### 1. Checkout contradicts the product page on delivery time — highest priority

The shipping rate shown at checkout reads:

> **Free Shipping** — Free worldwide shipping on all orders. Delivery in 7-15 business days.

The product page accordion, the About page and the shipping policy were all corrected to
2–3 days processing plus 10–15 days transit, about 12–18 days total. The checkout rate was
missed. It is the last screen before payment, so it is the one a customer is most likely to
rely on, and it is the only surviving instance of the old claim.

Not theme-scoped and not in `templates/`: it is the rate name and description under
Settings → Shipping and delivery. This is the fourth place that claim lives.

Worse than a stale number: the checkout rate says **business days** explicitly, while the
product page says plain "days". `DECISIONS.md` flags "business days or calendar days?" as the
urgent open question to Zendrop precisely because the storefront now says "days" unqualified.
Checkout is already answering that question on its own, with the retired figure. Whatever
Nina comes back with has to land here too.

### 2. The cart thumbnail is a technical drawing

The cart line item for "Porcelain White Set" renders a pale grey diagram annotated `68mm`
rather than a product photo. On a one-item cart it is the only image on the page.

### 3. On mobile the product page opens on a spec sheet

The first gallery slide at 390px is a two-up composite: a white brush on the left, the same
`68mm` dimension diagram on the right, letterboxed inside a 485px slide with large empty
margins. That composite is the first thing a mobile shopper sees. Title lands at y≈614 in a
664px viewport, Add to cart at y≈1105.

Reordering the media so a clean product photo is first is a merchandising change in admin,
not a theme edit.

### 4. Product image masters are too small to sell on

Fetched from the CDN without a `width` parameter, so these are the masters:

| File | Master | Weight |
|---|---|---|
| `9a027028461099dd1bcb0f0bec37.jpg` | 619×342 | 13 KB |
| `490627294bd3a01ca08ecc7064a5.jpg` | 518×644 | 29 KB |
| `65cce9fb45aa93153025339cdfe8.jpg` | 626×491 | 15 KB |
| `910684d94582aa85ba841193a76a.png` | 695×650 | 224 KB |
| `5fb974414d60af6cdf28e20d34c1.png` | 584×441 | 46 KB |
| `37b1dedc492ca591cb8d86c72522.png` | 694×683 | 223 KB |
| `adb0107942de9abda2842ce17748.jpg` | 476×467 | 36 KB |
| `46dd832645f195aef9b94211f816.png` | 510×486 | 224 KB |

The theme requests `width=3840` in its srcset; Shopify never upscales past the master, so the
desktop gallery paints 500–700px files into slots roughly twice that. They are visibly soft.
Answering the brief's question directly: **these are adequate to launch on and not adequate to
compete on.** They are supplier-catalogue images — several are white-background cut-outs and
at least two are dimension diagrams. There is no lifestyle photograph among them, which is
the gap the hero image currently fills single-handedly.

### 5. The homepage grid renders one card in a four-column row

Confirmed visually at 1440px: a single product card at the far left, roughly three quarters of
the row empty, directly above the newsletter block. `DECISIONS.md` already calls this out as
reading "unfinished" rather than focused, and proposes filling the `frontpage` collection
(`gid://shopify/Collection/533092860217`, empty today) and pointing the grid at it instead of
`all`. Nothing in this audit contradicts that; it is simply worse in a browser than on paper.

### 6. Variant selection does not change the gallery

With "Porcelain White Set" selected, the large desktop image is the orange-and-tan brush.
Colour-named variants that never show their colour.

### 7. No sticky add-to-cart on mobile

`STATUS.md` records sticky add-to-cart as on and verified via the API. At 390px, scrolled to
y=1400 and y=1900, the only fixed element pinned to the bottom of the viewport is the Shopify
preview bar (an empty 68px div). No add-to-cart bar appeared. Either the setting does not
apply at this breakpoint, or the preview bar suppresses it. Worth one look in the editor.

### 8. Two `<h1>` elements on the homepage

The hero `<h1>` ("Groom Smarter. Enjoy a Cleaner Home.", 56px, visible) plus a 1×1px
visually-hidden `<h1>` reading "Peluma" from Horizon's header logo. The hero fix worked; the
theme simply ships a second one. Minor, and a known Horizon default.

### 9. Homepage SEO title still says VelvetPaw

`<title>` renders `VelvetPaw | Premium Pet Essentials & Accessories`. Already known and
already recorded as admin-only — now confirmed against the rendered page rather than inferred.

## Could not verify

**Card payment.** The checkout Payment section offered PayPal only. Do not read that as
"PayPal is the only method": `checkout.pci.shopifyinc.com/build/.../card_fields.js` was blocked
by this environment's egress policy, and that script is what draws the card fields. Express
checkout rendered as an empty grey block for the same reason. Whether Shopify Payments is
active has to be confirmed in admin or from an unproxied browser.

Two things that did render and are worth a decision:

- **"Email me with news and offers" is pre-checked** at checkout. Opt-in consent checked by
  default is the kind of default that is a problem for EU visitors and is disliked in the US.
- **`$29.90` struck through against `$49.90`** on every surface. If `$49.90` was never a price
  the product actually sold at, a permanent strikethrough is a reference-price claim, and it
  falls under the same "no invented claims" rule as the removed boilerplate. Worth confirming
  before publish.

## The hero overlay — recommendation: keep 60%, or 55% at the very lowest

The premise in `NEXT-SESSION.md` was that 60% was set for the old busy cartoon and is probably
too heavy for the purpose-made hero. Rendered and measured, that premise is wrong.

The hero text is centred, and the centre of `Peluma-Hero.png` is its brightest region — a
sunlit window, a cream cushion and a pale dog. Compositing `rgba(18,18,18,α)` over the actual
pixels behind the text and computing WCAG contrast against white, at the real rendered
geometry (`object-fit: cover`, 1440×484 desktop and 390×600 mobile):

| Overlay | H1 56px bold, needs 3.0 | Subheading 17px, needs 4.5 |
|---|---|---|
| 60% `#12121299` (current) | worst 5.08 — **pass** | worst 5.16 — **pass** |
| 55% `#1212128C` | worst 4.30 — pass | worst 4.34 — 1.1% of area below |
| 50% `#12121280` | worst 3.68 — pass | worst 3.73 — **25.5% below** |
| 45% `#12121273` | worst 3.17 — pass | worst 3.22 — **36.0% below** |
| 40% `#12121266` (live) | worst 2.74 — **fails** | worst 2.77 — **55.6% below** |

Mobile tracks desktop closely; at 40% the subheading is below 4.5:1 across 40% of its area.

So 60% is not a leftover from the cartoon — it is what makes the subheading legible, and the
live theme's 40% would fail AA for both the subheading *and* the heading. If the image feels
buried, **55% (`#1212128C`) is the floor**, and it costs a sliver of the subheading. Going to
45% to "let the photo through" would be a real accessibility regression.

The better lever is composition, not opacity: the product — the brush in the hand — sits on the
right edge and is cropped out entirely at 390px. A hero crop that keeps the brush visible would
do more for the page than any overlay value.

## Against the open decisions in `DECISIONS.md`

That file lists the hero overlay as an open merchant decision, on the assumption that 60% was
calibrated for the cartoon and "may not need to be that heavy". Measured, it does need to be:
see the table above. That item can be closed — keep 60%, or 55% if a lighter hero is wanted.

The `$49.90` compare-at price is not in `DECISIONS.md` and should be. It appears on the
homepage card, the product page, the cart and checkout, and it is a reference-price claim in
exactly the sense the no-invented-claims rule covers. The variant pricing anomaly recorded
there — Porcelain White Set at $29.90 containing more than a bare brush at $29.90, while Milk
Brown Set is $39.90 — is a separate question and was not re-examined here.

## Suggested order of work

1. Fix the checkout shipping description (admin, Settings → Shipping and delivery). It is the
   only place still asserting the retired delivery claim, and it asserts it in business days
   while the open Zendrop question is exactly business-versus-calendar.
2. Reorder product media so a product photo, not the `68mm` diagram, is first — fixes the cart
   thumbnail and the mobile first slide together.
3. Confirm card payment is live, and decide on the pre-checked marketing consent and the
   `$49.90` compare-at price.
4. Leave the overlay at 60%, or set 55% if a lighter hero is wanted.
5. Replace the product photography when there is budget for it. Nothing else on this list is
   blocked by it.
