# Go live — the short list

Everything else in this directory is analysis. This is the list that blocks selling.
Four items, all in Shopify admin, roughly 15 minutes total. Nothing here needs another
decision — the wording is written out below, ready to paste.

Deliberately **not** on this list, because none of it blocks a sale and all of it is better
done against real orders: the card gateway, US-warehouse sourcing, catalogue expansion, and
re-wording the delivery estimate. See `DECISIONS.md` and `LAUNCH-READINESS-2026-08-28.md`.

---

## 1. Paste the two policies · 5 min

Settings → Policies.

- Privacy policy ← `peluma/privacy-policy.peluma.html`
- Terms of service ← `peluma/terms-of-service.peluma.html`

These replace 27 live occurrences of "VelvetPaw", including the opening line of the Terms.
Paste as HTML, not as rich text.

**Do not touch the refund policy.** It was hand-corrected for four real defects and has been
destroyed once already by regenerating it from template.

## 2. Correct the shipping policy · 2 min

Settings → Policies → Shipping policy. **Edit only these two lines** — do not regenerate the
policy, the rest of it is fine.

Replace:

> Processing Time: All orders are processed within 1 to 3 business days.
> Shipping Times: Standard international shipping typically takes between 7 to 15 business days depending on your location.

With:

> Processing Time: All orders are processed within 2–3 days.
> Shipping Times: Delivery to the United States typically takes a further 10–15 days — about 12–18 days in total.

That is the same claim already live on the product page, the About page and the checkout rate.
This page is the last one still contradicting them.

## 3. Homepage SEO title and description · 2 min

Online Store → Preferences → "Homepage title" and "Homepage meta description".
Currently reads `VelvetPaw | Premium Pet Essentials & Accessories`, which is what Google shows.

Title:

```
Peluma | Pet Grooming Essentials for Cats & Dogs
```

Description:

```
Simple grooming tools for cats and dogs, designed for easier routines and a cleaner home. Free worldwide shipping on every order.
```

There is no Admin API for this — it was tested and confirmed (see `STATUS.md`).

## 4. Delete one file, then publish · 3 min

Online Store → Themes → "Horizon — Peluma fixes (2026-08-27)" → ⋯ → Edit code →
delete **`templates/collection.pre-filter-fix-backup.json`**.

It is the restore point taken before the filter fix. It is reachable as
`?view=pre-filter-fix-backup` and should not ship. `themeFilesDelete` is blocked by the
connection's safety policy, so this one is manual.

Then **Publish** the theme. The current live theme drops to unpublished and stays available as
the rollback.

---

## After publishing, in this order

1. Place one real order yourself, through PayPal, to a US address. Nothing substitutes for it.
2. Pause the Google & YouTube free listing until the no-manufacturer-identifier setting is on
   (barcodes are permanently null — Zendrop confirmed no GTIN exists).
3. Send the two Zendrop questions that are already drafted in `DECISIONS.md`: US-warehouse
   availability for the brush, and cost price per SKU.
4. Start Pinterest. Organic, static pins, no filming required.

## Known and accepted at launch

- **PayPal is the only payment method.** Shopify Payments does not support Israel-based
  merchants — that is a structural limit, not a misconfiguration. PayPal guest checkout covers
  US card users. Revisit with 20–50 orders of data.
- **Delivery is 2–3 weeks**, because this SKU ships from China. The single biggest available
  improvement is sourcing US-warehoused products instead; that is a catalogue decision, not a
  settings one.
- The `$49.90` compare-at price and the pre-checked marketing consent at checkout are both
  live and both unresolved merchant decisions.
