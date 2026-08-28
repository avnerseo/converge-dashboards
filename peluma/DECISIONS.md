# Decisions and business context

`STATUS.md` is the change log — what was altered and why. This file is the layer above it:
the calls that were made, the reasoning behind them, and what is still owed to whom. It
exists because this context lived only in a conversation, and conversations do not survive.

## Supplier — Zendrop

### Answered (28 Aug, agent "Nina", ticket still open)

- **Fulfilment is China-only.** No US warehouse exists for this product. 2–3 days
  processing, 10–15 days transit. Roughly 12–18 days to a US buyer.
- **No GTIN / UPC / EAN exists** for any China-sourced Zendrop product. This is a shipping
  regulation, not missing data, and it is permanent — it applies to every future import from
  them. HS codes were offered as an alternative; useful for customs, not for Merchant Center.
- **"Set" (Z75Y6C7M0)** contains a white brush and a milk brown brush.
- **"Porcelain White Set" and "Milk Brown Set"** each contain a brush plus a rolling ball,
  and both cost Zendrop more for that reason.

### Still owed — send on the open ticket

```
Three follow-ups on the same product (import ID 62372790):

1. Business days or calendar days? You quoted 2–3 days processing and 10–15 days
   shipping. We are putting these figures on our storefront, so we need to state
   them accurately — please confirm which of the two those numbers are.

2. Shipping weight per variant. We need the packed weight (product plus packaging)
   for each of the 5 SKUs:
   PE17TFL2V — Porcelain White Set
   1O3NPE8 — Milk Brown Set
   MDYQJZF3J — Porcelain White Brush
   ZAF7RY7XJ — Purple Brush
   Z75Y6C7M0 — Set

3. Exact contents and cost price per variant. You mentioned that both "Porcelain
   White Set" and "Milk Brown Set" include a rolling ball in addition to the brush.
   Please confirm the exact contents of each of the 5 SKUs above, and the current
   cost price for each.
```

Question 1 is the urgent one. The storefront now says "days" unqualified, mirroring Nina's
own wording. If she meant business days, 12–18 business days is 17–25 calendar days, and a
US shopper reading "days" reads calendar days — the same class of understatement that was
just corrected.

## The pricing problem, and why variant renaming is on hold

Nina said **both** Sets cost more because they include the rolling ball. In the store:

| Variant | SKU | Price | Contents per Zendrop |
|---|---|---|---|
| Porcelain White Set | PE17TFL2V | $29.90 | brush + rolling ball |
| Milk Brown Set | 1O3NPE8 | $39.90 | brush + rolling ball |
| Porcelain White Brush | MDYQJZF3J | $29.90 | brush |
| Purple Brush | ZAF7RY7XJ | $29.90 | brush |
| Set | Z75Y6C7M0 | $29.90 | white brush + milk brown brush |

Porcelain White Set retails at the same price as a bare brush while containing more. Either
Nina is wrong about it or the retail price does not reflect the cost.

The names should become self-explanatory — "Porcelain White Brush + Rolling Ball",
"Two Brushes: White + Milk Brown", and so on. **But renaming first makes the problem worse.**
Today the vague names hide the anomaly; honest names put it in the shop window, where every
shopper picks the one with the extra item at the same price. Fix the price and the name in
the same move, once the cost prices come back.

## Catalogue — add 4 to 8 adjacent products

The homepage renders one card in a four-column grid. That does not read as focused, it reads
as unfinished, at the moment a stranger decides whether to enter a card number.

- **Zendrop bills on peak linked products in a cycle: 1–20 is $29/mo, 21–100 is $49/mo.**
  There is room for 19 more at no extra cost.
- Add things adjacent to grooming and shedding, so cross-sell is real and free shipping
  becomes leverage — a second item in the cart is near-pure margin.
- **Stop well under 20.** Each product needs the treatment the first one got: description,
  SEO, alt text, sensible variant names, no invented claims. Six good ones beat twenty
  mediocre ones.
- The merchant imports from Zendrop; the polish pass on each import is agent work.
- Once there are products, fill the `frontpage` collection
  (`gid://shopify/Collection/533092860217`, currently empty) and point the homepage grid at
  it instead of `all`, to control order and inclusion.

## Traffic — organic first, paid on evidence only

The China answer settles this.

- **No paid US traffic yet.** Two to three weeks' delivery, no reviews, no brand
  recognition. Paid clicks against that combination burn budget.
- **Pinterest, static pins, is the right first channel** — strong category, visual product,
  no filming required, which matters because filming is currently impossible. It compounds
  over weeks, which is the same clock the shipping runs on.
- **`marketingActivities` returns zero** — nothing is being spent today.
- **The Google & YouTube free listing is live and should be paused** until the theme is
  published and the no-manufacturer-identifier setting is on. `publishableUnpublish` is
  blocked by the MCP connection's safety policy, so this is an admin action.
- The About page already leans on honest delivery times rather than promising two-day
  shipping. Corrected numbers strengthen that position rather than undercutting it.

## Open decisions the merchant has not made

- **Hero overlay at 60% black.** Calibrated when the background was a cartoon. The
  background is now a purpose-made hero image and may not need it that heavy.
- **"Sunday to Thursday"** on the Contact page. Accurate for an Israel-based operation,
  unusual to a US reader. Keeping it means being visibly Israel-based — a positioning call,
  not an error.
- **Whether to state "ships from China" outright.** Not required, and a separate question
  from stating the delivery time honestly, which is required. Some buyers price it in; some
  abandon on it.

## What only the merchant can do

Not preference — these have no Admin API mutation for any app, or are blocked by the
connection's safety policy.

| Task | Why |
|---|---|
| Paste the two policy files | Connection holds `read_legal_policies`, not write |
| Homepage SEO title and meta | No Admin API mutation exists |
| Sender email, domain forwarding | No Admin API mutation exists |
| Pause the Google free listing | `publishableUnpublish` blocked by safety policy |
| Publish a theme | Blocked by safety policy, and should be a deliberate click |
| Zendrop imports and the ticket | No API access |

The support address `avnerseo@gmail.com` appears in six places: shop `contactEmail`, the
Contact page, the privacy policy, the terms (twice) and the refund policy (twice). The
refund-policy occurrences must be hand-edited — that policy must never be regenerated.
