# Start here

You are picking up work on the **Peluma** Shopify store (`pelumapets.com`,
`hjahey-v0.myshopify.com`). Read `peluma/STATUS.md` first — it is the full change log and holds
every ID, decision and open item. `DECISIONS.md` holds the business reasoning and the supplier
economics. This file is only the handover.

## Where things actually stand (2026-08-28)

**The store is live, working, and can fulfil a paying customer.** As of today the whole path —
customer pays on Shopify → order routes to Zendrop → Zendrop charges the card → supplier ships —
runs end to end with no manual step. That was not true this morning.

Proven, not assumed:

- Order **#1001** is `Processing` in Zendrop, invoice `3596898` **paid**, `cost_details`
  populated (product **$7.50** + shipping **$14.20**). US landed cost stays **$17.42**.
- Zendrop has a payment method on file (Mastercard •0657) and `auto_fulfillment_enabled: true`.
- Checkout verified end to end with a real paid order.

**What is missing is customers.** The store has never had a marketing visitor.

## The two open items

### 1. A theme is waiting to be published — one merchant click

Theme **`189492035897`** ("Horizon — mobile buy fix (2026-08-28)"), `UNPUBLISHED`, carries five
changes to `templates/product.json`, all verified by measurement and screenshot:

| Setting | Live `189462839609` | Copy `189492035897` |
|---|---|---|
| `media-gallery.aspect_ratio` | `adapt` | `1` |
| `variant_picker.variant_style` | `buttons` | `dropdowns` |
| `product-details.gap` | 28 | 16 |
| `product-details.padding-block-start` | 24 | 12 |
| Shipping copy | "processed within 2–3 days" | "Most orders … though occasionally longer" |

On a 390×664 viewport this moves **Add to cart from 1065px to 749px**. The copy change exists
because Zendrop states processing times vary and they hold no warehouse stock — the old wording
promised more than the supplier commits to.

`themePublish` is blocked by the MCP safety policy, deliberately. **The merchant publishes.**
If they decline, delete the theme; the live one was never touched.

### 2. Pinterest — the only thing between this store and a first sale

Everything is prepared in `PINTEREST.md`: business account, the free Shopify Pinterest app
(claims the domain, syncs the catalog into free organic Product Pins, installs the tag and
Conversions API), profile copy, five boards, and five rendered 1000×1500 pins committed at
`peluma/pinterest-pins/`.

**`pinterest.com` is blocked by this environment's egress policy (403) and there is no Pinterest
connector in the registry** — checked, not assumed. This is merchant work.

## What was ruled out, so you do not redo it

Five products across four categories were screened against real US market prices. **All five
failed on margin**, because Zendrop's landed cost lands at or above what Amazon, Chewy, eBay and
Temu already charge. This is a supplier problem, not a product-selection problem.

- Screen out supplier **417 ("Amazon Products")** entirely — Amazon retail pricing or above.
- **NexoraUSA (416)** is the one US supplier priced like a supplier; still not cheap enough on
  commodity goods.
- **Zendrop POD is fixed-listing only** — no per-order customer artwork. That kills the
  personalised pet-photo product, the only candidate that passed the margin screen.
- Catalog `in_stock: true` means the supplier **can source** an item, not that stock exists.
  Never read it as a shipping-speed guarantee.
- Private Agent and Safety Stock both require traction (20 orders/month) — consequences of
  sales, not routes to them.

## The rule this session learned the hard way

**Verify the money path, not just the data path.** The launch audit checked the storefront end to
end but never asked whether the supplier could be paid — and Zendrop had no card on file, so a
real customer would have paid and received nothing. A `completed` async fulfilment operation is
**not** proof of payment; check the invoice status separately. Full supplier checklist at the
bottom of `LAUNCH-READINESS-2026-08-28.md`.

## Hard constraints — carried over, still binding

1. **English only** in anything a customer sees.
2. **No invented claims.** No unmeasured percentages, no health claims, no fabricated
   reviews, testimonials or founder story. Theme defaults have violated this twice already
   (a "manufacturing partners" paragraph, and a newsletter promising exclusive deals) — both
   were removed. Watch for more.
3. **Never fabricate a barcode.** Zendrop has confirmed no GTIN exists for any China-sourced
   product, permanently. The Google feed needs the no-manufacturer-identifier setting instead.
4. **Never touch the refund policy.** It was hand-corrected to fix four real defects and has
   already been destroyed once by regenerating it from template.
5. **Never write to the live theme, and never publish.** Both are blocked by the MCP server
   anyway. Publishing is the merchant's deliberate click.

## Do not do these — already done

Do not re-fix the logo, the hero image, the `<h1>`, the CTA, the footer social links, the
redirect chain, the shipping accordion, the cart recommendation or the announcement bar.
`STATUS.md` records each one and why. Re-doing them risks undoing them.

## Waiting on other people

- **Zendrop**, on an open ticket: business days vs calendar days; packed weight per variant;
  exact contents and cost price per SKU. The cost prices matter — Nina said both "Sets"
  include a rolling ball and cost more, but Porcelain White Set retails at $29.90, the same
  as a bare brush. Variant renaming waits on that answer.
- **The merchant**, in Shopify admin: paste the two policy files in this directory; set the
  homepage SEO title and meta; configure domain email forwarding and the sender address;
  pause the Google & YouTube free listing; then publish the theme.

## One operational rule

The merchant sometimes has the theme editor open on `189462839609`. An open editor holds a
stale copy and its save overwrites API writes — this has already corrupted the product
template once, appending new shipping text to old rather than replacing it. Before writing
to that theme, ask whether the editor is closed. After writing, read the file back.
