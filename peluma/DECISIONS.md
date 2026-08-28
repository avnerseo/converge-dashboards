# Decisions and business context

`STATUS.md` is the change log — what was altered and why. This file is the layer above it:
the calls that were made, the reasoning behind them, and what is still owed to whom. It
exists because this context lived only in a conversation, and conversations do not survive.

## The rule every decision is measured against

Stated by the merchant, 28 Aug: **make money, in the fastest and simplest way.**

This is not a mood. It is the tie-breaker. When two options both look reasonable, the one that
gets to profit sooner with fewer moving parts wins, and the other is dropped rather than
deferred. Three things follow from it directly:

**Simple beats complete.** Two good products with week-long delivery beat six mediocre ones.
Five variants where three cannot rationally sell is worse than two that can. Every "but" in a
setup is a place that breaks later and costs a day.

**Do not invest further in the China brush.** It cannot reach the US warehouse — Zendrop
confirmed it, permanently. If the store moves to US-sourced products, work spent perfecting
this one is work thrown away. Keep it alive and selling; stop improving it. That specifically
means: no new photography effort for it beyond what the arriving unit gives for free, no
variant restructuring beyond deleting dead ones, no copy polishing.

**Nothing gets decided on an unknown margin.** Cost price is the gate. Pricing, ad budget, and
which products to add are all downstream of it, and guessing at it risks selling at a loss
faster and more simply than any other available mistake.

What this rule does *not* excuse: the no-invented-claims rule, the refund policy, and never
publishing or writing to the live theme without care. Those are constraints, not preferences,
and moving fast through them is how a store gets shut down rather than profitable.

## Check before deciding — a rule written after breaking it three times

On 28 Aug, three decisions were made on inference while a check was available. The merchant
caught the pattern. Recording it so it does not repeat.

| Decision made on inference | What a check showed | Cost |
|---|---|---|
| Pushed twice to reword delivery to "about 2–3 weeks" | Zendrop: calendar days — the live copy was already right | Two wasted rounds |
| Estimated margin at 66–87%, assuming shipping was in the product cost | Shipping is billed separately, $9.92 of a $17.42 landed cost. Real margin 33% | A wrong conclusion that paid traffic was affordable, then withdrawn |
| Repriced the Sets to $39.90 from cost plus margin | eBay sells the same generic product at $8.99–$16.94 — below the landed cost | A reprice and a revert |

**The rule:** before changing any customer-facing number or claim, check the primary source
first. Supplier data before statements about supply. Market prices before pricing. Real landed
cost before margin arithmetic.

**And when a check is blocked, say so before deciding, not after.** `WebFetch` is blocked for
every domain outside Shopify in this environment — Amazon, Walmart, eBay and Zendrop's own help
centre all return `EGRESS_BLOCKED`. `WebSearch` runs server-side and does work. That limit
should be stated up front as a caveat on the decision, rather than discovered afterwards.

## Market research on the brush — the product is a commodity

Searched 28 Aug. The same generic "3-in-1 cat steam brush" is sold by:

- **Amazon** — at least nine different brands
- **Walmart** — several versions
- **Home Depot** — two versions
- **eBay** — listed at **$8.99, $12.00 and $16.94**

Against a landed cost of $17.42 for the Sets, **eBay sellers are listing below Peluma's cost.**
They buy direct rather than through Zendrop's markup, and ship slow and cheap.

This reframes the product. It is not differentiated, it is available everywhere with two-day
domestic delivery, and Peluma loses on price, speed, reviews and brand recognition
simultaneously. **At Zendrop's cost structure it is not viable as a standalone item.**

One thing the research did surface, and it inverts an earlier claim in this file:

| | Price | Landed cost | Net |
|---|---|---|---|
| Single brush | $29.90 | **$8.82** | **~$18.50** |
| Set | $29.90 | $17.42 | ~$9.88 |

An earlier note said the single-brush variants "can never rationally sell" because the Sets
dominated them at the same price. That was reasoning about the variants against each other
while ignoring the market outside. **The single brush is the viable product here** — $29.90 sits
inside the Amazon range and it earns roughly twice what a Set earns at the same price. The Sets
only work above market, which is to say they do not work.

Data quality: the prices above are eBay figures returned by search, and eBay is the cheapest
channel. Amazon's actual prices could not be retrieved — the domain is blocked. Treat the range
as directional, and confirm on Amazon before pricing decisions rest on it.


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

## Catalogue expansion — what to add, and the gate in front of it

Added 28 Aug, after the full store sweep. Merchant restated the target: English only, US primary.

### The gate: do not import anything yet

The default delivery profile is `פרופיל כללי`, carrying rate `רגיל` at ₪35 domestic and ₪57
international. The current product escapes it only because Zendrop put it on its own profile.
**Every new import that lands on the default profile shows a US shopper a Hebrew rate name
priced in shekels.** Fix the profile first; importing first means finding this in a support
email from a confused customer. Same for the Search & Discovery filter labels, which render
`זמינות` / `מחיר` on `/collections/all` — the page the Shop nav points at.

### The category is validated

US pet grooming products: **$5.11B (2024) → $7.01B (2030), 5.47% CAGR**. De-shedding sits in
the fastest-rising application segment at **7–9% annually**. E-commerce is **26–34% of market
value by 2026**. Grooming tools are consistently cited as the highest-margin, lowest-risk entry
point in the niche, with realistic margins of **40–65%**. Sources at the end of this section.

So the existing product is in the right category. The problem is that it is alone.

### The constraint that should pick the products

China-only fulfilment at 12–18 days rules out a whole class of otherwise-good items:

- **Nothing impulse-driven, seasonal or gift-timed.** A buyer who wants it this week buys it
  on Amazon. Everything added has to survive "I'll get it in about two weeks."
- **Nothing that competes head-on with a Prime-shipped identical item.** The defence is a
  narrower audience and a better page, not price.
- **Nothing that needs video to sell**, while filming is impossible. Supplier stills have to
  carry it — and per the media audit, this supplier's stills need heavy filtering.

What survives: considered, repeat-use grooming items a shedding-season owner buys as a set.

### The cheapest second SKU already exists in the catalogue

The "Porcelain White Set" and "Milk Brown Set" variants each include a **rolling ball lint
remover**, and the product already carries three images of it (media #3, #8, #12). It is
supplied, photographed, and priced — and it is not sold on its own. Listing it standalone
costs one Zendrop link and no new photography. It is also the natural cross-sell to the brush:
same job, different surface — the pet, then the sofa.

Caveat from the media audit: #3 and #8 have marketing text baked into the pixels in non-native
English ("Stain from sofa hair dust", "Sticky snack crumbs"). Those two cannot ship as-is.
#12 is clean.

### Then, in order of fit

1. **De-shedding grooming glove.** Same job as the brush, different form. The most-cited safe
   entry product in the niche. Bundles naturally.
2. **Self-cleaning slicker brush.** Same buyer, same session, higher basket.
3. **Paw washer.** Sourcing under $5, retails $15–25. Different moment, same owner.
4. **Rechargeable quiet nail grinder.** Same "rechargeable grooming device" buyer as the mist
   brush; a considered purchase, so the wait is tolerable.

That is five SKUs including the rolling ball, against a Zendrop tier that allows 20. It leaves
room and respects the "six good ones beat twenty mediocre ones" rule already in this file.

### Positioning

The sub-niche advice in the sources is worth taking: rather than "pet grooming", narrow to
**shedding season for indoor cat and dog owners**. It matches the product, matches the hero
image, matches the announcement bar copy that is already live, and it is the one framing where
a two-week wait is normal — shedding is a recurring season, not an emergency.

### What is still missing before any of this earns money

Cost prices per SKU are still owed by Zendrop (see above). Margin cannot be checked without
them, and the existing pricing anomaly — Porcelain White Set at the same $29.90 as a bare
brush while containing more — is unresolved. Adding four more SKUs on top of an unexplained
price structure multiplies the problem rather than diluting it.

Sources: [Research and Markets — US pet grooming products](https://www.researchandmarkets.com/report/united-states-grooming-product-market),
[Grand View Research — pet grooming products market](https://www.grandviewresearch.com/industry-analysis/pet-grooming-products-market),
[Dropified — pet products dropshipping 2026](https://www.dropified.com/blog/pet-products-dropshipping-in-2026-best-selling-items-suppliers-profit-margins/),
[Product Lair — best pet dropshipping products, US trends](https://productlair.com/blog/best-pet-dropshipping-products).
Market figures are third-party estimates, quoted as such — they are not measurements of this
store and must not appear in customer-facing copy.

## Zendrop answered the open ticket (28 Aug, Nina)

### 1. Calendar days — the storefront copy was already right

> "For the processing and shipping days, both of these are calendar days, but to note these are
> average days and can take more or less depending on exact real-time data."

This closes the question this file flagged as urgent. The store says "processed within 2–3
days… a further 10–15 days — about 12–18 days in total", unqualified, which is exactly how a US
shopper reads calendar days. **No change needed.** A change to "about 2–3 weeks" was proposed
twice while the answer was ambiguous; with the ambiguity resolved it would now overstate the
wait, so it is dropped.

"Average, can take more or less" is already carried by "typically takes" in the live copy.

### 2. Packed weights — applied

| Variant | SKU | Price | Weight |
|---|---|---|---|
| Porcelain White Set | PE17TFL2V | $29.90 | **0.307 kg** |
| Milk Brown Set | 1O3NPE8 | $39.90 | **0.307 kg** |
| Set | Z75Y6C7M0 | $29.90 | **0.307 kg** |
| Porcelain White Brush | MDYQJZF3J | $29.90 | **0.173 kg** |
| Purple Brush | ZAF7RY7XJ | $29.90 | **0.125 kg** |

Written to Shopify and verified. The `0.0 kg` that showed on order #1001 is gone, and the
Merchant Center feed and any future weight-based rate now have real numbers.

(Zendrop also quoted `FORC9Q8LH` at 0.173 kg — a SKU this store does not carry.)

### 3. The weights settle the pricing anomaly, and it is worse than described

Nina confirmed each variant contains **one** of each item shown, the rolling ball included.
The weights then say something the price list does not:

- **The three "Set" variants weigh exactly the same: 0.307 kg.** Same contents by mass.
- 0.307 − 0.173 = 0.134 kg — the second item, consistent with a brush plus a rolling ball.
- **Porcelain White Set and Milk Brown Set are identical in weight and structure. One is
  $29.90, the other $39.90.** The only difference is colour. A $10 gap for a colour.
- **Porcelain White Set (brush + ball, 0.307 kg) costs the same $29.90 as Porcelain White
  Brush (brush alone, 0.173 kg).** The Set strictly dominates: more product, same money.

The practical consequence: **the single-brush variants can never rationally sell.** Any shopper
comparing them picks a Set. Three of the five options are doing nothing except adding choice
paralysis, and one of them is priced $10 above its identical twin.

This still cannot be fixed without cost prices — repricing blind risks selling at a loss. But
the shape of the fix is now clear, and it is a pricing decision, not a naming one.

### 4. The brush cannot move to the US warehouse — ever

> "This is available from Chinese suppliers (Zendrop Fulfilment) and cannot be added to the US
> warehouse, since the current suppliers are shipping from China. That said, you can certainly
> review our US catalog and find any similar products you can use."

Definitive. **This product is permanently a 12–18 day product.** The delivery-speed lever does
not exist for it.

That reframes the catalogue plan in this file. It is no longer "add 4–8 adjacent products". It
is: **the US catalog is where a competitive store gets built, and this brush is the legacy
item.** Zendrop is pointing at the same conclusion — find similar products that ship from the US.

Whether the brush stays, becomes the slow option alongside fast ones, or is eventually replaced,
is a decision for after the first US-stocked products are live and their conversion can be
compared against it.

### Still unanswered: cost price per SKU

Nina answered days, weights and contents, but **not cost price** — the one number that decides
whether any of this is profitable. It no longer needs a support reply: **order #1001 has gone to
Zendrop, and their fulfilment charge for it is the cost price of `PE17TFL2V`.** It will land in
the Zendrop dashboard or on the card within days.

## Cost prices arrived, and they changed the business (28 Aug)

Zendrop's product page gives per-SKU costs. **Shipping is charged separately and it is the
dominant cost**, which an earlier margin estimate in this session got wrong by assuming it was
included.

| SKU | Variant | Product | Shipping | **Total to Zendrop** |
|---|---|---|---|---|
| PE17TFL2V | Porcelain White Set | $7.50 | $9.92 | **$17.42** |
| 1O3NPE8 | Milk Brown Set | $7.50 | $9.92 | **$17.42** |
| FORC9Q8LH | Brown Brush | $1.27 | $7.55 | **$8.82** |

Zendrop also shows **8 days average shipping to the United States** on this product — better
than the 10–15 the storefront states. The storefront under-promises, which is the right
direction, so it stays.

### The pricing was steering customers to the worst variant

At the old prices, with fees of roughly $2.60:

| | Old price | Cost | Old net |
|---|---|---|---|
| Porcelain White Set | $29.90 | $17.42 | **$9.88** |
| Milk Brown Set | $39.90 | $17.42 | $19.88 |

Identical cost, identical contents, identical weight — a $10 gap in profit decided by colour.
And because Porcelain White Set carried a brush *plus* a rolling ball for the same $29.90 as a
bare brush, every rational shopper picked it. **The default variant was the least profitable
one, and the pricing actively pushed people toward it.**

### Repriced, with the merchant's approval

All three Set variants → **$39.90**. The two single brushes stay at **$29.90**. Verified live.

Compare-at was aligned to $49.90 across all five. Milk Brown had been showing "was $69.90"
against identical products showing "$49.90"; levelling it removes the inconsistency and
*reduces* an unsubstantiated discount claim rather than inflating one. The underlying
compare-at question — whether $49.90 was ever a real price — is unchanged and still open.

Net result: roughly **$19 profit on every variant**, versus $9.88 on the one most customers
were choosing.

Note on rigour: `Z75Y6C7M0` ("Set") did not appear in the SKU cost table. Its cost is **inferred
from its weight** being identical to the two confirmed Sets. If it turns out to differ, reprice.

### What this does to the traffic plan

An earlier note in this session said the margin allowed paid traffic. **That was based on the
wrong margin and is withdrawn.** At $9.88 it was clearly loss-making against typical acquisition
costs of $15–30 for a product at this price. At ~$19 it is borderline, not comfortable.

Organic stays the affordable channel, not the slow alternative to a better one.

### The real economics problem, stated plainly

**Shipping from China costs $9.92 on a $29.90 product — a third of revenue.** No campaign fixes
that. Domestic US shipping typically runs $3–6, so moving to US-sourced products would add
roughly $4–7 per order *and* cut delivery from 12–18 days to 3–11. One move, both problems.
That remains the highest-value action available, and it costs nothing to make.

---

## 2026-08-28 — The supplier screen, run four times, with the same answer

### The US-sourcing hypothesis was tested and it failed

The section above closed by saying that moving to US-sourced products was "the highest-value
action available." That was a hypothesis, not a finding. It has now been tested directly
through the Zendrop MCP, and it does not hold.

US shipping is genuinely better — a flat **$6.99** on most US suppliers, and **$0.00 with
6-day delivery** on NexoraUSA. The delivery problem really does go away. **The cost problem
does not**, because the US base prices absorb the shipping saving and then some.

| Product | Category | Zendrop landed (US) | US market price | Verdict |
|---|---|---|---|---|
| Pet hair brush (CN) | Grooming | $17.42 | eBay $8.99–$16.94 · Temu ~$4 | ✗ |
| Pet hair brush (US supplier) | Grooming | $14.00 | same | ✗ |
| Cat tree, NexoraUSA `1998045` | Furniture | $72.77 | Chewy $39.87–$80 | ✗ |
| Grooming vacuum kit, NexoraUSA `2000023` | Grooming appliance | **$61.33** | oneisall $35–55 · Afloia $65 | ✗ |
| Grooming vacuum kit, NexoraUSA `2001005` | Grooming appliance | **$55.11** | same | ✗ |

Both grooming vacuums ship free in 6 days, so $55.11 and $61.33 *are* the landed costs — the
best case Zendrop offers. To clear even a 40% margin they would have to retail at $92–$102,
against `oneisall` at $35–55 and `Afloia` at $65 on Amazon today, and a 12,000Pa kit that was
recently on offer at $39.99. Nobody pays $99 for the thing they can see at $45. Rejected on
the margin screen.

**Four products, four categories, cheap and expensive, China and US — the same outcome every
time.** This has stopped being a product-selection problem. Zendrop is a middleman, and it is
being asked to undercut retailers who buy direct at volume. On any item a customer can
recognise and search for, it cannot.

### The "Amazon Products" supplier is not a supplier

Supplier id **417, "Amazon Products" (US)** carries a large share of the US catalog. Its
prices are Amazon *retail*, sometimes well above it:

- FUKUMARU grooming vacuum — **$176.66**
- KungFuPet grooming vacuum — **$232.70**
- A generic 5-tool kit — **$352.16**
- Sweetcrispy grooming vacuum — **$1.17** (an obvious data error, listed as in stock)

There is no price at which these resell. Treat supplier 417 as unusable and screen it out
before looking at anything else. **NexoraUSA (id 416) is the one US supplier whose pricing
behaves like a supplier's.**

### What this leaves

The screen only ever fails for one reason: the customer can find the identical object
somewhere else. So the products that survive it are the ones where that comparison is not
possible:

1. **Personalised / print-on-demand** — the design is ours, so there is no identical object
   to compare against. This is the only category that structurally escapes the problem.
2. **Bundles** — a combination nobody else sells as a single SKU. Weaker, because the parts
   are still individually searchable.

That makes POD the main line now, not a side experiment.

### Print-on-demand: what is verified, and the one number still missing

**POD is not exposed through the Zendrop MCP.** Confirmed, not assumed: `get_catalog_categories`
returns 200+ categories with no print-on-demand among them (the only "print" match is
*Print, Copy, Scan & Fax* — printers). Searching the POD blank names returns plain blanks
resold by supplier 417, not the POD service. So the POD numbers cannot be pulled from here.

Zendrop does not publish POD shipping rates either — their help centre says shipping is
calculated per product by weight, destination and type. That article is also blocked by this
environment's egress proxy, so it cannot be read from here directly.

What *can* be checked is whether the POD base costs are competitive, and they are. Against
Printify's published base costs, Zendrop's POD catalog is at or below market:

| Item | Zendrop POD base | Printify base |
|---|---|---|
| White glossy mug | $7.95 | $13.09 |
| Matte paper poster | $6.50 | $10.95 |
| Gildan 64000 tee | $9.44 | — |
| Bella+Canvas 3001 tee | $11.69 | — |

This matters: unlike the dropship catalog, **Zendrop's POD pricing is not marked up above the
industry.** That is the first cost structure this week that starts in the right place.

The industry shipping benchmark, for scale only: Printful charges **$4.75** for the first tee
(+$2.20 each additional) and **$4.69** for the first mug (+$2.55 each additional) inside the US.
If Zendrop is anywhere near that, a Bella+Canvas 3001 lands around **$17** and retails at
$29.99–$34.99 for a **43–51% margin against no comparable competitor**.

**That "if" is doing all the work, and I am not going to build on it.** The margin error earlier
today came from exactly this — assuming a shipping cost instead of reading it. Printful's rate
is Printful's rate, not Zendrop's, and Zendrop's own documentation says the number is
weight-and-destination dependent. So the recommendation stays parked until the real figure is
in hand. It is a two-minute check inside the Zendrop dashboard; the steps are in
`PRODUCT-SCREENING.md`.

## Zendrop answer — POD orders do count toward Private Agent

Asked whether print-on-demand orders count toward the 20 monthly orders required for a Private
Agent. Zendrop support's answer, relayed by the merchant:

> "Yes, as our team simply check on the order revenue generated or number of orders generated by
> your store. Hence whether you use POD as order basis or more, PAP simply can be made eligible."

So eligibility is measured on **total order count and revenue, regardless of product type**. No
category is excluded, and mixing POD with regular dropship orders is fine.

**What this changes right now: nothing.** It is worth recording because Private Agent is the one
plausible route to better sourcing prices, and the margin problem documented above is the reason
we would want it. But the threshold is 20 orders a month and the store is at **one** — a test
order that has not even shipped. Private Agent is a consequence of traction, not a way to get it.

It does remove one hypothetical: if POD ever becomes worth running here, those orders would not
be wasted from an eligibility standpoint. That is a smaller point than it first appears, since
Zendrop POD was already ruled out for the personalised products that were the only ones to pass
the margin screen.

Filed under: true, useful later, not actionable today.
