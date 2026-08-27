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
