# Start here

You are picking up work on the **Peluma** Shopify store (`pelumapets.com`,
`hjahey-v0.myshopify.com`). Read `peluma/STATUS.md` in this directory first — it is the
full change log and holds every ID, decision and open item. This file is only the handover.

## Why this session exists

The previous session could not reach any Shopify host: the environment's egress policy
answered `403` to `*.myshopify.com`, `pelumapets.com` and `cdn.shopify.com`. Every check it
made was at file level through the Shopify MCP server — it never saw a rendered page.

That policy has now been changed to **Custom**, allowing:

```
*.myshopify.com
pelumapets.com
cdn.shopify.com
*.frame.claudeusercontent.com
```

**Confirm that first.** `curl -sS -o /dev/null -w "%{http_code}" https://pelumapets.com`
should return a real status code, not `000`. If it still fails, stop and say so.

## The immediate job

Everything below is blocked on one thing: nobody has looked at the storefront.

Theme **`gid://shopify/OnlineStoreTheme/189462839609`** ("Horizon — Peluma fixes
(2026-08-27)") is unpublished and carries all the work. The live theme
`189442031929` is untouched and is the rollback point.

Preview the working theme in a browser (Chromium and Playwright are installed) and check:

1. **Mobile, cart and checkout.** The merchant asked for this explicitly and it is the last
   gate before publishing. Add to cart, reach checkout, on a phone viewport and a desktop one.
2. **The hero overlay.** It sits at 60% black (`#12121299`). That value was set when the
   background was a busy cartoon; the background is now a purpose-made hero image
   (`Peluma-Hero.png`, 1672×941). It may be heavier than it needs to be. Look, then
   recommend a number.
3. **The announcement bar.** It was `#af14bd` magenta at `1.5rem`; it is now the palette
   foreground at `0.875rem`. Confirm it reads as supporting text, not a headline.
4. **The product images.** They could never be viewed before. Judge whether they are good
   enough to sell on, and whether the hero image works at full width.

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
