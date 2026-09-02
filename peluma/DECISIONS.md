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

## Zendrop's first-order notice — two corrections it forces

Zendrop showed a first-order notice in the dashboard. Two things in it matter.

### 1. Our shipping copy promised more than the supplier commits to

Zendrop's own words:

> "Processing times (how long it takes for your orders to ship) will vary. Most of your orders
> will ship in 3 days or less, **but sometimes it can take much longer than that.** This is
> because dropshipping suppliers (including Zendrop) **don't carry stock in their warehouse for
> any of the products in their catalog.**"

The live product page said: *"Orders are processed within 2–3 days."* That is a firm commitment
the supplier explicitly does not make. If an order takes ten days to process, the customer was
given a number we could not keep — which is exactly the kind of unsupported claim this project
forbids, and in practice it produces late-delivery complaints and PayPal disputes.

Corrected on the unpublished theme copy `189492035897`:

> "Free worldwide shipping on every order. **Most orders are processed within 3 days, though
> occasionally longer**, and delivery to the United States typically takes a further 10–15 days.
> You'll receive a tracking number by email as soon as your order ships."

This mirrors Zendrop's own language, keeps the 10–15 day delivery figure that was already
verified, and drops only the part we cannot stand behind. The "12–18 days in total" line goes
with it, since a total built on a processing time that "will vary" is not a real total.

### 2. "In stock" in the catalog does not mean stock exists

Zendrop states plainly that they hold **no** warehouse stock for **any** catalog product. So the
`availability: { in_stock: true, inventory_level: "In stock" }` field returned by
`get_catalog_product` means the supplier can source the item, **not that it is sitting on a
shelf ready to ship.**

This reframes every availability reading taken during the product screening. It does not change
any of the five rejections — those failed on price, not stock — but it means **no future product
decision should treat "In stock" as a shipping-speed guarantee.** The only real speed signal is
a supplier's stated delivery estimate, and the only proof is a fulfilled order.

Relatedly, Zendrop offers **"Safety Stock"**: once a product is selling at volume they will hold
inventory so orders ship within 24 hours, and they say they reach out when that point comes. Like
Private Agent, it is a consequence of traction, not a route to it — worth knowing, not actionable
at one order.

## The $49.90 compare-at was never a price — removed 2026-08-29

The compare-at question had been open since the first day. The data closes it:

```
product createdAt   2026-08-26 18:10:44Z
variants createdAt  2026-08-26 18:10:44Z   ← same second
compareAtPrice      set at creation
order history       one order, #1001, at $29.90
```

**The compare-at did not come from a price reduction — it arrived with the Zendrop import**, which
is what dropshipping importers set by default. The product has existed for three days and has
never been sold, listed or charged at $49.90. **It was never a price.**

### Why that mattered enough to act on immediately

Google's **Misrepresentation** policy names `inaccurate promotions or fake discounts` as a
violation, and it carries **immediate suspension with no warning and no grace period**. The
Merchant Center account was created the day before. An account one day old with no trading
history, suspended for misrepresentation, is very hard to recover.

It also contradicted this project's own founding constraint — no unsupported claims — and the
claim was not confined to a feed: **every visitor to the product page was being shown $29.90 with
$49.90 struck through**, which is the same assertion made directly to the customer.

### Done

`compareAtPrice` set to `null` on all five variants via `productVariantsBulkUpdate`, verified on
the live product JSON and in the generated feed:

| Variant | Price | compare-at |
|---|---|---|
| Porcelain White Set | $29.90 | none |
| Milk Brown Set | $39.90 | none |
| Porcelain White Brush | $29.90 | none |
| Purple Brush | $29.90 | none |
| Set | $29.90 | none |

The feed template needed no change — its `compare_at_price > price` branch simply stops firing,
so each item now carries a single `g:price` and no `g:sale_price`.

**What this costs:** the strike-through display, which does affect conversion. That is a real
loss and worth stating plainly. **What it buys:** a price the store can stand behind, and no
exposure to an instant suspension on the only paid channel that is free to use.

Industry-normal is not the same as safe. Plenty of stores do this; Google suspends for it.

## The screening cost column was wrong all along (29 Aug)

Before pricing the two newly imported products I checked the real per-variant cost, and the check
overturned a number this document has been reasoning from for a week.

**Zendrop's catalog `price` field is the cheapest variant's cost — a "from" price, not the
product's cost.**

Proven on the nail grinder `2000800`. The catalog reports `price: "6.15"`. Shopify received 20
variants, and `$6.15` turns out to be the cost of **`White grinding head`** — a *spare abrasive
head*. The actual rechargeable device costs **$15.67**.

| Variant | Real cost |
|---|---|
| White grinding head (a spare part) | **$6.15** ← the catalog's headline price |
| **White rechargeable sharpener (the device)** | **$15.67** |
| 1pc | $16.57 |
| 1set | $17.89 |
| Grinding Head 20pcs | $49.49 |

Corroborated on the paw cleaner `1997733`: catalog `price: "7.65"` is exactly the **S** variant's
cost, the cheapest of eight. Same rule, second product.

Every "landed cost" in `PRODUCT-SCREENING.md` is therefore a **floor, not a cost**, and every
margin cleared on those numbers was cleared against a spare part. The `$6.76` "Dog Shaver" and
the rest of the sub-$8 US list are almost certainly accessories, not devices.

### The nail grinder is dead, and the retraction did not go far enough

The 28 Aug section resolved the grinder at **$24.90** on the strength of a **$6.15** cost, netting
a claimed **$16.51**. With the real cost:

| | Claimed | Actual |
|---|---|---|
| Cost | $6.15 | **$15.67** |
| Price | $24.90 | $24.90 |
| Net after ~9% fees | **$16.51** | **$6.99** |

To net the $12 the screen demands, the price would have to be **$30.41** — above the top of the
branded band (Wahl, HARDELL, Casfuy at $20–30), with supplier photos and no reviews. And the
bundle escape hatch closes too: brush + grinder at $46.80 costs $33.09 and nets **$9.50**, which
is *less* than selling the brush alone at $29.90 ($9.88). **The bundle destroys value.**

**Deleted from Shopify.** It was never publicly visible.

### Two tools validated in the process

- **`get_catalog_shipping_estimate` is trustworthy.** Run against the brush it returns
  `$9.92 / 8 days` — matching the figure independently verified from the Zendrop product page and
  order #1001. So `$0 / 6 days` on both NexoraUSA products is real, not a default.
- **`inventoryItem.unitCost` carries Zendrop's true per-variant cost on a fresh import** — the
  cheapest variant's `unitCost` equals the catalog `price` on both products, and every price is a
  uniform 3.14× of it. **Caveat:** the legacy brush's `unitCost` ($3.76 / $22.20) does *not* match
  its verified costs ($1.27 / $7.50), so this holds for imports made now, not for that one.

## The roller category, researched by the merchant (29 Aug)

The merchant brought market research on the two US category leaders — **ChomChom Roller**
($20–28, 150k–200k Amazon reviews) and **Hertzko self-cleaning slicker brush** ($15–22, 90k+
reviews) — plus a full margin model for rollers, which are **34.2% of the pet hair-removal
category**, its largest slice.

### It independently confirms the finding this project reached from the other direction

Their own conclusion: *"ChomChom keeps its lead through brand authority, tens of thousands of
positive reviews and superior packaging — not through technological exclusivity,"* and
*"Amazon is flooded with hundreds of Chinese manufacturers selling an identical product at
$9.99–$12.99."*

That is the same structure the nail grinder exposed — the identical device at $2.99 and at $38, a
20× spread — arrived at from a different category and a different data source. **The pattern is
now confirmed twice, independently. It is a property of the market, not of one product.**

### But the margin model describes a different business

| | Their model | This store |
|---|---|---|
| Sourcing | Alibaba bulk / OEM | Zendrop, per order |
| Unit cost | $1.20–2.50 + $1.00–1.80 freight | 50–60% of US retail, proven six times |
| Capital required | **MOQ 500–1,000 units — $1,500–$4,000 upfront**, plus freight and prep | **$0** |
| Channel | Amazon FBA (fees $5.50–7.50 + PPC $4–7) | Shopify, organic |
| Gross margin | 60–70% | ~30–35% |

The 60–70% is real — **it is bought with inventory capital**. It is not available to a
dropshipping store at any product choice, so it is not a reason to add a roller here. It is a
reason to consider a different business model, which is a separate decision and the merchant's
to make.

### The roller has the same shape as the grinder

Applying the proven 50–60% rule to the merchant's own retail figures:

| Position | Price | Competitor | Verdict |
|---|---|---|---|
| Brand tier | $22.90 | ChomChom, $20–28, ~175k reviews | Requires beating a review moat with supplier photos |
| Clone tier | $12.99 | ORDORA/Delomo, $12–16 | Nets ~$4 |

**Recommendation: do not add it now** — not because the demand is wrong (the demand signal is the
strongest in the research) but because it is a review-moat category and the store has no reviews,
no traffic and no photographs of its own.

**Not yet verified:** the actual Zendrop cost of a comparable roller. The Zendrop MCP connection
dropped mid-session, so this is reasoning from the established pattern rather than a measurement.
It is a cheap check to run — and now a reliable one, since `inventoryItem.unitCost` on a fresh
import gives true per-variant cost. **Worth running before the next product decision, not after.**

## The bundle argument, and where it holds (29 Aug)

The merchant argued the store should not sell a single $15–20 Amazon best-seller at all, because
US paid acquisition costs $15–25 per customer: sell a brush at $20 with an $18 CPA and $4 of
product and you **lose $2 a sale**. The proposed fix is a 3-item bundle at $44.99–49.99 with
COGS $7.50–9.00, netting $12–15 at 25–30%.

**The logic is right. Two of its inputs are not ours.**

### Input 1 — our CPA is zero

The whole argument is a **paid-traffic model**. This store cannot run paid traffic: Pinterest ads
are permanently closed (Aleph Israel, ILS 75,125 yearly minimum), and the margin analysis had
already ruled out paid acquisition at ~$10 net. Every channel here is organic — Pinterest Pins,
Google free listings, SEO.

So the $18 CPA that makes a $20 product a $2 loss **does not exist for us**. The paw cup at
$16.90 nets ~$7 in full. Under the merchant's own model that product is unsellable; under ours it
is profitable. **The constraint the argument optimises against is not the one that binds us.**

### Input 2 — COGS $7.50–9.00 is the Alibaba number again

That figure assumes bulk OEM purchase. Our verified per-order Zendrop costs:

| | Cost | Shipping |
|---|---|---|
| Mist brush set | $7.50 | $9.92 |
| Paw wash cup | $7.65–8.56 | $0 |
| A roller (estimated) | ~$6–8 | ~$0 |

A three-item Zendrop bundle costs roughly **$32–34**, not $7.50–9.00. At $49.99 that nets ~$12
*before* advertising — and with the merchant's $18 CPA it would **lose $5–6 a sale**. The bundle
does not rescue paid traffic at our cost base; it only works on the inventory model.

### Input 3 — the high-ticket alternative is already tested and dead

The suggested fallback (a $59.99–79.99 grooming vacuum kit) was screened on 28 Aug against real
Zendrop data: `2000023` lands at **$61.33** and `2001005` at **$55.11**, against a US market of
$35–65. **Landed cost sits inside the retail band.** Recorded then, unchanged now.

### What survives, and it is the valuable part

**The bundle is right for us — for a different reason.** Not to absorb ad spend, but because the
brush carries $9.92 of shipping whether it travels alone or not, while the cup ships free. A
second item adds margin against costs already paid.

**Shipped:** an automatic Buy-X-Get-Y discount — buy the brush, take $3.90 off the cup.

| | Price | Cost | Net after ~9% |
|---|---|---|---|
| Brush alone | $29.90 | $17.42 | **$9.88** |
| **Brush + cup** | **$42.90** | $25.98 | **$13.06** |

**+32% profit per order.** Verified on a live cart: $46.80 → $42.90, the cup at $13.00.

This is a real discount that actually applies at checkout, not a compare-at price — no
Merchant Center exposure, and automatic discounts do not appear in the product feed.

### The question underneath both of the merchant's messages

Two rounds of research have now arrived at the same place from different categories: the numbers
that work require **buying inventory**. That is the real fork — not which product, but which
business model — and it costs $1,500–4,000 upfront. It is the merchant's decision, and it should
be made deliberately rather than drifted into.

## Short-form video: the right diagnosis, three different price tags (29 Aug)

The merchant proposed UGC short-form video as the leading 2026 strategy — "oddly satisfying"
before/after ASMR clips, TikTok Shop integration, a $45–50 bundle, and a four-step plan ending in
TikTok/Meta ad campaigns.

**The format insight is correct and it is the most useful thing brought to this project.** Every
previous entry has named "supplier photography" as the blocker without saying what would replace
it. This does: for pet grooming, the converting asset is **20 seconds of before and after**, not
a better still. That turns a vague weakness into a specific, cheap, achievable ask.

**But the plan bundles four steps whose costs differ by three orders of magnitude.** Split:

| Step | Cost to us | Status |
|---|---|---|
| The creative format (before/after, natural sound) | **$0** | **Do it. This is the path.** |
| Organic posting to TikTok / Reels / Pinterest | **$0** | Open, no eligibility gate |
| Sending samples to 3–5 US creators for 10–15 clips | **$1,000–4,500** + samples + freight | Same order as the inventory decision |
| TikTok Shop checkout | Company formation | **Blocked — verified** |
| TikTok / Meta ad campaigns | $15–25 CPA | Collides with our COGS |

### TikTok Shop is blocked, and it is the Aleph pattern again

Checked rather than assumed. TikTok Shop US requires **a named US person** with government ID,
address verification and a selfie video; **a US business entity**; **a US business bank account
matching the entity**; and alignment across entity, owner, bank and account identity. A non-US
founder can operate through a US LLC, but TikTok reviews beneficial ownership and operational
control, so the LLC alone does not settle it.

This is the third channel to close on the same structural fact — the store is operated from
Israel. Pinterest ads (Aleph), TikTok Shop, and now the US-payments assumption behind both.
**Organic posting has no such gate**, which is exactly why it keeps being the answer.

### The paid step collides with the previous entry

The merchant's own CPA figure is $15–25. The bundle shipped today nets **$13.06**. Paid
acquisition loses money on it, and better creative lowers CPA without changing the fact that our
COGS is 50–60% of retail. UGC does not fix unit economics; it fixes *organic* reach, where CPA
is zero.

### The reframe

**The plan assumes we need creators. We need one dog and one phone.**

Peluma is not buying reach — it is producing content for free channels. Ten creator videos would
be for ad testing we cannot afford to run. One honest before/after clip of the merchant's own dog
serves Pinterest, TikTok organic, Reels and the product page at once, and it is the same single
event this document has now pointed at three times: **the brush arriving.**

### What can be published automatically, and what cannot

Now tested against the Pinterest connector:

- **Still Pins — yes.** Four posted today.
- **Carousel Pins (2–5 images) — yes.** A before/after sequence fits in one Pin.
- **Video Pins — no.** They need a `media_id` from Pinterest's media-registration endpoint, which
  the connector does not expose. Video has to be posted by hand, or through another route.

So the division of labour is: the merchant films; Claude publishes stills and carousels to
Pinterest automatically; video goes up manually on TikTok and Reels.

## The merchant's roadmap, executed rather than debated (29 Aug)

The merchant re-sent the high-ticket grooming-vacuum roadmap. Rather than restate an opinion,
its free steps were **run**.

### Step 1 — Ad intelligence: cannot be run from here

`facebook.com/ads/library`, `ads.tiktok.com/business/creativecenter` and `alibaba.com` all
return `000` at the egress gateway. Only server-side web search reaches them. **This step is the
merchant's to do**, and it remains worth doing.

### Step 3 — sourcing: this is the step that decides it, and it fails

The roadmap's whole case rests on **$20–30 landed cost**. Actual wholesale listings for
5-in-1 / 7-in-1 pet grooming vacuum kits:

| | Roadmap assumption | Found |
|---|---|---|
| Unit price | $20–30 incl. freight | **$30.50–34 FOB at MOQ 500** |
| Plus air freight to US | — | roughly $5–8/unit |
| **Landed** | **$20–30** | **~$36–42** |
| Capital at MOQ 500 | not stated | **$15,250–17,000** |

Reworking the roadmap's own margin table at real prices:

| Retail | Landed | Fees ~9% | Gross | Less CPA $30–40 | Net |
|---|---|---|---|---|---|
| $79.99 | $39 | $7.20 | **$33.79** | | **$0 to −$6** |
| $119.99 | $39 | $10.80 | **$70.19** | | **$30–40** |

**The claimed $60–90 gross does not exist at $79.99.** It appears only at $119.99 — which is
Neakasa's price, and reaching it requires being a brand with reviews. That is the same
review-moat conclusion every previous round reached, now produced by the merchant's own method
instead of by argument.

And the capital requirement is **five times** the $2,500–4,000 previously discussed.

### Step 2 — review mining: this worked exactly as promised

The most valuable part of the document. Recurring complaints on the leading kits:

- **Motors burning out** — one AIRROBO PG100 "died after 5 minutes… turned it to medium, it burned out and started giving off that burnt smell"
- **Dust cup too small** — with a long-haired dog, "constantly had to stop to empty the container"
- **Weak suction** — "less suction than any of my battery-powered handheld vacuums"
- **Hose splitting** in use
- **Flimsy brush teeth** — metal on one head, plastic on the other, hair having to be pushed through by hand

That is a supplier specification and a landing-page hierarchy, written by customers. **It is
reusable whatever the product** — the same technique applied to our own mist brush produced the
distilled-water and tank-seal instructions now live on the product page.

### Verdict

**Method: keep. Product conclusion: not supported by its own step 3.** The roadmap is a good
process that, when actually run, argues against the thing it recommends.

## Pin copy will be rebuilt around gifting, not grooming — 2026-08-30

Pinterest's own US keyword-trend data (see PINTEREST.md, 30 Aug) shows the grooming vocabulary
every existing Pin is written for does not rank at all, and that `dog grooming` is flat 7–11
year-round with no seasonal upside. The only term in the category that multiplies is gifting:
`dog gifts` runs ~8x from its ten-month floor into mid-December, and `dog christmas gifts`
peaks about 2x the grooming baseline.

Decision: the next Pin batch is built on gift framing and published now, not in November,
because Pinterest takes 4–8 weeks to index and distribute. The existing grooming Pins stay up
as a steady trickle; they are not the bet.

This is the first Peluma content decision made from measured demand rather than intuition.
It is still demand data, not conversion data — no Peluma sale has validated it.

## Reconciling session 04's economics against primary sources — 2026-08-30

Session 04 wrote to the live store and produced `HANDOFF.md` on branch
`claude/video-creation-capability-433k8w`. Both were checked against Shopify and against this
project's own records. Three findings, in order of importance.

### 1. The Paw Wash Cup cannot be bought. Storefront-verified.

The Admin API reports `availableForSale: true` on all eight variants. The live cart disagrees:

    POST /cart/add.js  {"id":54400049185081,"quantity":1}
    422 — "The product 'Peluma 2-in-1 Paw Wash Cup - Navy Blue / L' is already sold out."

Root cause, from `inventoryLevels`: every cup variant is stocked only at the **Zendrop**
fulfilment-service location with `available: 0`. The brush sits at the same location with
`available: 50000` and adds to cart fine. `tracked: false` and `inventoryPolicy: DENY` are
identical on both, so the tracked flag is not what decides this — the quantity at the
fulfilment-service location is.

**This is my error, and it is worth naming precisely.** On import I set
`inventoryItemUpdate(tracked:false)` across the cup's eight items and then verified the
*product feed* read `in stock` on all 13 items. The feed was the wrong signal. A feed listing
is not a purchase. Nothing was ever added to a cart.

Everything built on this product since — the description, the eight de-branded images, the two
hero shots, Pins 11, 12, 15, the carousel, the homepage placement, the BXGY bundle — has been
pointing at a product no one could buy.

`HANDOFF.md`'s unverified item 2 was therefore **correct**, and my own read of
`availableForSale` would have concluded the opposite. Storefront behaviour beats Admin fields.

### 2. `unitCost` is the wrong source for the brush, and HANDOFF is built on it

`HANDOFF.md` derives landed cost ≈ $21.70 from the single order's Shopify gross profit.
Shopify computes gross profit from `inventoryItem.unitCost`, which for the ordered variant
(`PE17TFL2V`) reads **$22.20**.

This project already recorded, on 28 Aug, Zendrop's own per-SKU figures for that exact SKU:
product $7.50 + shipping $9.92 = **$17.42 landed**. It also recorded that `unitCost` is
trustworthy on a *fresh* import and **not** on the legacy brush import. HANDOFF used the
unreliable field.

The gap is $4.78 per order, and it changes the conclusion rather than refining it.

### 3. Verified costs, and the ones still missing

| SKU | variant | price | landed | source | trust |
|---|---|---|---|---|---|
| PE17TFL2V | Porcelain White Set | 29.90 | **17.42** | Zendrop page, 28 Aug | verified |
| 1O3NPE8 | Milk Brown Set | 39.90 | **17.42** | Zendrop page, 28 Aug | verified |
| MDYQJZF3J | Porcelain White Brush | 29.90 | — | — | **unknown** |
| ZAF7RY7XJ | Purple Brush | 29.90 | — | — | **unknown** |
| Z75Y6C7M0 | Set | 29.90 | — | — | **unknown** |
| CJGY…S ×4 | Paw Cup, S | 16.90 | **7.65** | `unitCost`, fresh import | verified |
| CJGY…L ×4 | Paw Cup, L | 16.90 | **8.56** | `unitCost`, fresh import | verified |

The cup figures are landed because NexoraUSA ships **$0 to the US**, recorded twice and
re-confirmed against order #1001's fulfilment. The three unknown brush SKUs need Zendrop, and
**the Zendrop MCP server is disconnected in this session**, so they could not be pulled. The
$8.82 landed figure in the 28 Aug table is SKU `FORC9Q8LH`, a brush this store does not sell —
it must not be substituted for the two it does.

### Contribution on verified numbers only

Payment fee 2.9% + $0.30.

| line | Porcelain White Set $29.90 | Milk Brown Set $39.90 | Set + Cup L bundle $52.90 |
|---|---|---|---|
| landed | −17.42 | −17.42 | −25.98 |
| fee | −1.17 | −1.46 | −1.83 |
| **contribution** | **11.31** | **21.02** | **25.09** |
| margin | 37.8% | 52.7% | 47.4% |
| break-even CPA | $11.31 | $21.02 | $25.09 |

HANDOFF put today's contribution at $7.03 / 23.5%. On verified costs it is **$11.31 / 37.8%**.
Its direction was right — $29.90 does not support paid acquisition — but the $39.90 variant
that already exists **clears the ~$17 gate on its own**, at $21.02.

### The demand risk that must not be forgotten

This project already tried repricing the Sets to $39.90 and reverted, because eBay sells the
same generic product at $8.99–$16.94. Margin is not the binding constraint at $39.90; price
acceptance is. Raising the price fixes the spreadsheet and may cost the conversion. That is a
merchant decision, and no price was changed here.

### Correction to the section above — the gaps were smaller than stated (30 Aug)

Three things were already in this repo and were not checked before writing the section above.
Same failure the 28 Aug table records: inference while a check was available.

**1. `HANDOFF.md` re-proposes a change this project already made and reverted.**
It recommends raising to $39.90 as "a field edit rather than a strategic leap". On 28 Aug all
three Set variants *were* moved to $39.90 and verified live, then two were reverted, because
eBay sells the same generic product at $8.99–$16.94. Shopify confirms the reverted state today:
Porcelain White Set $29.90, Set $29.90, Milk Brown Set $39.90. The recommendation is not new
and its counter-evidence is already on file.

**2. The three "unknown" SKUs are not unknown — packed weights pin them.**
Zendrop's weight quotes, written to Shopify and verified on 28 Aug:

| SKU | variant | weight | reasoning | landed |
|---|---|---|---|---|
| MDYQJZF3J | Porcelain White Brush | 0.173 kg | identical to `FORC9Q8LH`, quoted at 0.173 kg and $8.82 landed — same item, different colour | **≈ 8.82** |
| ZAF7RY7XJ | Purple Brush | 0.125 kg | lighter than the above, so shipping is no higher | **≤ 8.82** |
| Z75Y6C7M0 | Set | 0.307 kg | identical to both confirmed Sets at 0.307 kg | **≈ 17.42** |

Estimates, not quotes — but grounded in measured weights from the supplier, not in a ratio.
Calling them "unknown" overstated the gap.

**3. The Paw Cup cannot be fixed from Shopify at all.**
`Location/115449626937` (Zendrop) returns `fulfillmentService.inventoryManagement: true`. The
fulfilment service owns quantities at that location and Shopify rejects manual writes to it.
Asking for permission to run `inventorySetQuantities` was the wrong ask: the action does not
exist on this side. Stock has to come from Zendrop pushing it.

### Contribution per variant at today's live prices

Payment fee 2.9% + $0.30. Landed costs above; cup costs are `unitCost` on a fresh NexoraUSA
import that ships $0 to the US.

| variant | price | landed | fee | **contribution** | margin | clears $17 gate |
|---|---|---|---|---|---|---|
| Purple Brush | 29.90 | ≤8.82 | 1.17 | **≥19.91** | ≥66.6% | **yes** |
| Porcelain White Brush | 29.90 | ≈8.82 | 1.17 | **≈19.91** | 66.6% | **yes** |
| Milk Brown Set | 39.90 | 17.42 | 1.46 | **21.02** | 52.7% | **yes** |
| Porcelain White Set | 29.90 | 17.42 | 1.17 | **11.31** | 37.8% | no |
| Set | 29.90 | ≈17.42 | 1.17 | **≈11.31** | 37.8% | no |
| Paw Cup, S | 16.90 | 7.65 | 0.79 | **8.46** | 50.1% | n/a |
| Paw Cup, L | 16.90 | 8.56 | 0.79 | **7.55** | 44.7% | n/a |

### What this changes about the gate

`HANDOFF.md` frames the store as uniformly unable to support paid acquisition. It is not
uniform. **Three of the five brush variants already clear ~$17 contribution at today's prices,
with no change at all.** Two do not, and one of those two is the variant order #1001 actually
bought.

The binding problem is therefore **mix, not price level**: five variants sit at essentially one
price while landed cost ranges $8.82 → $17.42, so contribution ranges $11.31 → $19.91 for the
same $29.90. This repo already named that on 28 Aug — "the pricing was steering customers to
the worst variant" — and the reprice that was meant to fix it was reverted on market-price
grounds, leaving the anomaly in place.

Two ways out, and they are the merchant's call, not an inference to be made here:
steer the mix toward the single brushes (featured variant, default selection, imagery), or
make the Sets carry their own cost. No price or variant order was changed.

## The brush is repriced by content, not by colour — 2026-08-31

Two changes to the flagship, both verified from the live storefront afterwards.

### 1. Variant names now say what is in the box

`productOptionUpdate` on the single `Style` option. Variant IDs and SKUs unchanged, so the
BXGY bundle — which targets **products**, not variants — could not break, and was re-checked
`ACTIVE` after.

| was | is |
|---|---|
| Porcelain White Brush | White brush |
| Purple Brush | Purple brush |
| Porcelain White Set | White brush + lint roller |
| Milk Brown Set | Milk brown brush + lint roller |
| Set | Two brushes - white + milk brown |

This was written down as needed on 28 Aug — *"the names should become self-explanatory"* — and
then left undone for three days. It took one mutation.

### 2. Renaming immediately exposed a live cannibalisation risk

The moment `Set` became `Two brushes - white + milk brown`, it read as **two brushes for the
price of one**, at $29.90. It is also the worst-margin line on the page (landed ≈$17.42).
Clarity turned a hidden anomaly into the obvious buy.

So the pricing decision stopped being optional. Applied:

| variant | contents | price | landed | fee | **contribution** |
|---|---|---|---|---|---|
| White brush | 1 item | 29.90 | ≈8.82 | 1.17 | **≈19.91** |
| Purple brush | 1 item | 29.90 | ≤8.82 | 1.17 | **≥19.91** |
| White brush + lint roller | 2 items | 29.90 → **39.90** | 17.42 | 1.46 | **21.02** |
| Two brushes | 2 items | 29.90 → **39.90** | ≈17.42 | 1.46 | **≈21.02** |
| Milk brown brush + lint roller | 2 items | 39.90 | 17.42 | 1.46 | **21.02** |

**One item $29.90, two items $39.90.** No compare-at anywhere, so no unsubstantiated discount
claim was introduced.

**Why this is not the 28 Aug reprice that was reverted.** That one raised prices from cost plus
margin, and eBay's $8.99–$16.94 for the same generic product refuted it. This one is justified
by a second physical item in the box — the strongest argument available on the page — and it
deletes the least defensible thing that was there: **$10 for a colour.**

Minimum contribution across the product moves from **$11.31 to $19.91**. Every variant now
clears the ~$17 gate; before, the one that actually sold did not.

### 3. Copy that the rename would have falsified

The live description still read *"The Porcelain White Set and Milk Brown Set also include the
rolling lint remover"* — names that no longer exist. Rewritten to describe the options by
content, and confirmed on the storefront: zero occurrences of the old names remain.

Checked and clear: no live Pin quotes a price, and the "free worldwide shipping" claim in three
Pin descriptions still holds, because the brush sits in the Zendrop profile whose Rest-of-World
zone is free. **Open:** `pin-10`, scheduled 4 Sep, says *"Both Peluma sets"* — stale now that
three options carry two items. Its Routine fires into this session, so the copy gets corrected
at post time rather than by editing the Routine blind.

## Correction: the Paw Cup is genuinely out of stock, and my diagnosis was wrong — 2026-08-31

I told the merchant the cup's zero inventory was "a sync failure, not a stock-out", on the
strength of `get_catalog_product(1997733)` returning `availability.in_stock: true` on all eight
variants. Zendrop support checked the product directly and confirmed it **is out of stock**.
They are right.

The evidence that settles it was already in my own notes and I failed to join it up:
`Location/115449626937` reports `fulfillmentService.inventoryManagement: true`. Zendrop owns
that number. **The 0 in Shopify is Zendrop reporting zero** — it is the supplier's own answer,
not a failed handshake. The catalog `in_stock` flag is evidently a catalog-level availability
marker, not live per-variant stock, and I treated it as authoritative because it agreed with
what I expected.

One claim in their reply is not accurate and should not be carried forward: they said the
50,000 on the brush is "a default placeholder value placed by Shopify". Shopify has no
mechanism that invents a quantity for a fulfilment-service item; that number comes from Zendrop
as an effectively-unlimited marker. It does not change the conclusion — order #1001 proves the
brush is fulfillable — but the explanation is wrong.

### What this breaks, measured

- `available: False` on the storefront, "Sold out" badge on the collection — at least honest.
- The cup appears **7 times on the homepage**. That is a theme-level placement and cannot be
  changed from here.
- **7 of the 16 live Pins point at the sold-out page** — 11, 12, 15, 17, 18, 19, 21. Three of
  them were published today, deliberately timed to the `dog paws` annual search peak. That
  timing is now spent on a product nobody can buy.
- The BXGY bundle pairs the brush with the cup, so it can never trigger.

### Decision: stop propping up the cup, and do not draft it

Keep the product published. Shopify's "Sold out" is honest, the seven Pins keep a valid target,
the URL keeps whatever index value it is accruing, and it revives the moment stock returns.
Drafting it would throw all of that away to fix a badge.

**But every remaining Pin goes to the brush until the cup is back.** The plan was to keep
covering paw care; that would now be building links to a dead page. This is the actual
course-correction, and it is worth more than the badge.

The brush was always the stronger product and this makes it explicit: contribution $19.91–21.02
against the cup's $7.55–8.46, and it is the only thing that has ever sold.

## The SEO description was making claims the product page refuses to make — 2026-08-31

Went looking at where the Pins actually land, rather than making more Pins. The brush's SEO
metadata — the text Google shows in search results, and a likely source for feed fields — read:

> "Self-cleaning mist grooming brush that traps loose fur, **soothes skin** and keeps your home
> cleaner."

Tags included `deshedding brush` and `self-cleaning`.

The live product description, written deliberately, says the opposite in two places: *"Helps
collect loose fur"* — hedged — and, explicitly, *"This is an everyday grooming brush **rather
than a deshedding tool** — it works on the coat rather than stripping out a deep undercoat."*

So the most public copy on the store contradicted the page it pointed at, and `soothes skin` is
a health claim with nothing behind it. It had been sitting there since the product was created.

Replaced with copy that matches the page:

> "An everyday grooming brush for cats and dogs, with soft silicone bristles and a fine water
> mist built into the handle. Rechargeable over USB. Free US shipping."

Tags `deshedding brush` and `self-cleaning` removed. Verified on the live page: the new text
appears, `soothes skin` returns zero. The two remaining hits for "deshedding" are the
disclaimer sentence itself, which is the honest use.

**The Paw Cup's SEO was checked at the same time and is clean** — accurate, and consistent with
its description. This was the brush only.

Method note: the finding came from asking *where does the traffic land* instead of *how do I
make more traffic*. Sixteen Pins pointing at a page whose search snippet makes an unsupported
health claim is worse than fifteen Pins.

## Reading the product page as a buyer — two fixes — 2026-08-31

Loaded the brush page on a 390x844 viewport and read it the way a visitor would, instead of
querying fields.

### 1. The two "+ lint roller" options showed no lint roller

Every variant already had an image attached, so the wiring was fine — the mapping was not.
Both `+ lint roller` options pointed at a photo of the brush **alone**. A buyer paying $39.90
for the second item in the box had no picture of that second item. That is the exact $10 the
reprice earlier today rests on.

There was no supplier photograph of a brush and roller together, so two were composed from the
real photographs already on the product — the white brush beside the pink roller, and the milk
brown brush beside the pink roller, on white, with the roller's cut-out rounded so the pairing
reads as deliberate rather than pasted. Nothing generated, nothing implied that is not in the
box.

`productVariantDetachMedia` then `productVariantAppendMedia` — append alone fails with
*"the supplied variant already has media attached"*.

Verified live, all five:

| variant | price | image |
|---|---|---|
| White brush + lint roller | 39.90 | `combo-brush-roller.png` |
| Milk brown brush + lint roller | 39.90 | `combo-brown-roller.png` |
| White brush | 29.90 | white brush photo |
| Purple brush | 29.90 | purple brush photo |
| Two brushes - white + milk brown | 39.90 | both brushes photo |

### 2. "Why pet owners love it"

The features heading claimed that pet owners love it. **The store has never had a customer.**
That is an implied testimonial, and the standing rule is no fabricated reviews or testimonials.
It had been there since the description was first written and survived every pass, including
the ones where the claims themselves were audited — because it reads as a template heading
rather than as a claim.

Changed to **"What it does:"**. Verified live: the old string returns zero.

### Checked and clear

The `Home & Garden` collection holds only the sold-out cup, but it appears in **no menu** —
main, footer or customer account. It is an orphan, not a dead end for visitors. No action.

## Google Merchant Center suspended the store — Misrepresentation — 2026-09-01

Found by reading the merchant's mailbox, not by any check I was running. Two messages:

- **1 Sep** — *"During our policy review we still found an issue with your account (Peluma,
  Account ID 5845593043): **Misrepresentation**. As a result, your product listings and/or
  Shopping ads are unavailable for display to users."* Google adds that identity verification
  by government ID may be required.
- **2 Sep** — a separate alert about a drop in active items.

This is a policy suspension, not a feed error. **Free Google Shopping listings — one of only
two free traffic channels in the plan — produce nothing until it is lifted.** The word "still"
implies at least one earlier review already failed.

### What the store actually shows, checked

Google's console holds the specific reason; it is not in the email. What is visible from here:

1. **No verifiable business identity anywhere on the storefront.** The Contact Information
   policy contains a single line — `avnerseo@gmail.com`. No business name, no postal address,
   no phone. Fetching `/pages/contact` confirms it: the only occurrences of "Israel" are a
   country dropdown, and the address and phone held in `shopAddress`
   (Adnei-Paz Street 29, Hadera, `0523578812`) appear nowhere on the site.
   **This is the most common trigger for Misrepresentation on a new store.**
2. **A personal free-mail address throughout the legal pages.** `avnerseo@gmail.com` appears in
   Contact Information, the Privacy Policy, the Refund Policy and the Terms — while
   `shop.contactEmail` is already `pelumapets@gmail.com`. Inconsistent, and a free-mail-only
   contact is itself a weak trust signal.
3. **The Shipping Policy is inaccurate.** It states *"Free Worldwide Shipping on all orders"*,
   but the Paw Wash Cup sits in a US-only delivery profile. Google checks stated policy against
   actual shipping configuration.

### What I could not do

`shopPolicyUpdate` returns **"Access denied … Required access: `write_legal_policies`"**. The
policy pages cannot be edited from here at all, so the whole fix is the merchant's.

Two further constraints worth stating: the Refund Policy is ring-fenced by standing
instruction and is not to be touched regardless; and publishing a **home** address and personal
mobile is a privacy decision that belongs to the merchant, not something to do on his behalf.

### Reading the order that shipped

Order #1001's tracking is `4PX3003119499366CN` — the `CN` suffix confirms the brush ships from
China, consistent with the 12–18 day estimate on the page and with the $9.92 shipping component
in its cost.

## 2 Sep 2026 — Merchant Center suspension: what I verified and what I fixed

Read the actual suspension email in full (`googlebase-noreply@google.com`, 1 Sep,
thread `1a05a5442a914f40`). The operative text:

> During our policy review we still found an issue with your account
> (Peluma - Account ID: 5845593043): **Misrepresentation**. As a result, your
> product listings and/or Shopping ads are unavailable for display to users.
> ... You might be asked to submit a government-issued ID to verify your identity.

Only one such email exists in the mailbox (searched 90 days) — "still" is Google's
template wording, not evidence of an earlier notice. The 2 Sep "Drop in Number of
Active Items" alert is the consequence of this suspension, not a separate fault.

The email names no sub-reason. The sub-reason is only visible in the Merchant
Center console, so the merchant has to read it there. What follows is what is
provably wrong on the live storefront right now.

### Verified against the live store (2 Sep)

| # | Finding | Evidence | Who can fix |
|---|---------|----------|-------------|
| 1 | No business identity anywhere on the storefront | Footer is `© 2026 Peluma, Powered by Shopify` and nothing else. `shopAddress` (Adnei-Paz Street 29, Hadera, 3832986) appears on no public page. | Merchant — it is his home address, his call |
| 2 | Shipping Policy promises worldwide, delivery profiles do not deliver it | Policy: *"We offer Free Worldwide Shipping on all orders."* Profile `135010484537` "Paw Wash Cup — US only (NexoraUSA)" has exactly one zone: United States. A non-US buyer gets no rate at all for the cup. | Merchant — `shopPolicyUpdate` needs `write_legal_policies`, denied to this session |
| 3 | Personal free-mail address on four legal pages | `avnerseo@gmail.com` × 6: privacy 1, refund 2, terms 2, contact-information 1 | Merchant — same permission wall |
| 4 | Contact page carried the personal address | — | **Fixed by me, see below** |

Not faults, checked and ruled out:
- `shopLocales` is `en` only, primary and published. The `?locale=he` in the
  admin's policy URLs is an admin artefact, not what a customer sees.
- `/pages/contact` renders a working Shopify contact form (`class="contact-form__form"`)
  in addition to the email address. That is two contact methods, which is what
  Google asks for — so **no phone number needs to be published**.
- Israel and United States markets are both ACTIVE. Not a policy problem.

### What I changed

`pageUpdate` on Page `174333722937` (`/pages/contact`) — I have `write_content`,
which is why this one was possible where the policy pages were not:
- `avnerseo@gmail.com` → `pelumapets@gmail.com`
- Removed *"Sunday to Thursday"* from the reply-time promise. Accurate for an
  Israeli work week, confusing on a US-facing store, and it is not needed to
  keep the sentence true.
- "About us" now reads: *"Peluma is an independent online store, operated from
  Israel and shipping to customers in the United States."* — country of operation
  stated plainly, which is half of what a Misrepresentation reviewer looks for.

Read back from the public URL, not from the admin: `curl https://pelumapets.com/pages/contact`
returns `pelumapets@gmail.com` and no other address.

### What is still missing and cannot be done from here

A physical business address on the storefront. Google's Misrepresentation policy
wants a business that a customer can identify and locate. Peluma currently
publishes a first name and nothing else. The only address the business has is the
merchant's home address, so publishing it is a privacy decision that is his alone
to make — this session will not publish a home address on the merchant's behalf.

## 2 Sep 2026 — the Merchant Center console text, and the real automated trigger

The merchant opened `merchants.google.com/mc/products/diagnostics/accountissues?a=5845593043`.
The console says more than the email did:

- **"Misrepresentation — Prevents all products from showing in Israel and United States."**
  Both markets, not just the US.
- **"Google found this issue through automated checks."** No human reviewed this.
  So the trigger is something a crawler can measure, not a judgement call about tone.
- `I disagree with the issue` is **greyed out** — disputing is not offered. The only
  path is fix → `Verify info` → request review.
- The checklist Google prints is its generic Misrepresentation list, not a diagnosis:
  business transparency; reviews/badges; SSL; **"Provide information in the business
  information settings in your Merchant Center"**; and **"match your product data in
  your Merchant Center with your online store"**.

### Two of those bullets I could test. One came back clean, one came back bad.

**Badges and unearned seals — clean.** Scanned the homepage and the brush product page
for `guarantee|certified|approved|award|seal|badge|trusted|verified|100%|money.?back|
secure checkout|satisfaction|as seen|#1|best.?sell|vet|clinically|official`. **Zero
matches on both pages.** The storefront makes no unearned trust claim. SSL is valid.
Neither of those bullets is our problem.

**Product data match — this is the bad one.** Product `10323824017721` (Paw Wash Cup):

```
status: ACTIVE          tracksInventory: FALSE
all 8 variants: inventoryQuantity 0, inventoryPolicy DENY, availableForSale TRUE
```

`tracksInventory: false` is why every variant reports `availableForSale: true` despite
zero quantity. Zendrop support confirmed in writing on 1 Sep that this product is
**out of stock at the supplier**. So the storefront and the Google feed both advertise
an in-stock, orderable product that cannot be fulfilled, and a customer can pay for it.

That is exactly what an automated Misrepresentation check looks for, and it is the
strongest single candidate for the trigger — stronger than the missing address,
because it is machine-detectable from the feed alone without any crawl of the policies.

### Revised priority

| Order | Action | Owner | Why first |
|-------|--------|-------|-----------|
| 1 | Cup → DRAFT | merchant approval, then me | Kills the false availability, removes it from the feed, drops it off the homepage without a theme edit, and ends the US-only vs "worldwide shipping" contradiction. Four problems, one action |
| 2 | Merchant Center → `Verify info` | merchant | The button Google put on the page. Business information settings is a named bullet |
| 3 | Contact information policy + address | merchant | Business identity, first bullet |
| 4 | Shipping policy rewrite | merchant | `write_legal_policies` denied to this session |
| 5 | Request review | merchant | Only after 1–4. A failed review triggers a waiting period |

Setting a product to DRAFT is gated on the merchant's explicit approval
("אל תשנה מחירים או סטטוס מוצר בלי אישור שלי"), so it is asked, not done.

## 2 Sep 2026 — review requested, and what it took to find the button

Submitted. The card now reads **"Review requested on Sep 2, 2026. It can take a
few days to complete."**

Two things worth remembering, because both cost time today.

**The cup went to DRAFT** (product `10323824017721`), on the merchant's explicit
approval. Verified from the public site, cache-busted: product URL returns **404**,
homepage mentions of the cup went **7 → 0**, `/collections/all` **→ 0**. The brush
is unaffected. This removed the false in-stock signal, took the sold-out product
off the homepage without any theme edit, and retired the US-only delivery profile
that contradicted the shipping policy.

**The merchant fixed all four policy pages.** Read back from the live site:
shipping rewritten and no longer promising worldwide; contact information now
carries `Peluma / Adnei-Paz Street 29 / Hadera 3832986 / Israel` plus the brand
email and the contact-form URL; privacy and terms swapped to `pelumapets@gmail.com`
(0 occurrences of the personal address remain on any page except the refund policy,
which stays ring-fenced).

### Final pre-submission audit — 10 of 10

Business address published · city and postcode · country · working contact form ·
personal email gone · cup 404 · brush in-stock signal true · "Free Worldwide
Shipping" removed · shipping claim matches the delivery profiles · zero unearned
badges · SSL valid.

**One false alarm, mine.** An audit script reported "26 suspicious claims" because
that pass forgot to strip `<script>`/`<style>`. Re-ran it split: 13 matches per page
in raw source, **0 in text a customer sees** — all of them CSS like `width: 100%`
and class names containing `badge`. The earlier clean result was the correct one.
Told the merchant it was my bug, not a store problem.

### The button is mislabeled, and I got it wrong first

There is **no `Request review` button** on the Misrepresentation card. The only
control is **`I disagree with the issue`** — and it opens a dialog titled
**"Before you request a review"** with a checkbox `My account meets the policy
requirements` and a `Request review` action. It is the review-request flow wearing
a dispute label.

I had told the merchant not to touch that button, reading it as a denial that
would burn the appeal. That was wrong, and the page header contradicted me:
*"If you've fixed the issues **or** disagree with them, request a review."* One
action, both paths. Corrected it in writing and had him open the dialog without
submitting, so the reading could be confirmed before anything was sent.

Also learned: **`Fix issue` in the red banner is only an anchor link.** It scrolls
to, or navigates to, the diagnostics page — it is not the submit control. And the
review budget is **3 requests**, with a cooling-off period after a rejection.

### Waiting on

Google's decision, by email to `avnerseo@gmail.com`, a few days out. The Gmail
connector dropped mid-session, so this session cannot poll the inbox until it
reconnects.

## 2 Sep 2026 — Zendrop's stock signal cannot be trusted. Proven.

Queried `get_catalog_product` for the paw wash cup, catalog id `1997733`, supplier
NexoraUSA — the product Zendrop's own support told us in writing on 1 Sep is **out
of stock at the supplier**, and which we pulled to DRAFT today for exactly that
reason. The API returned:

```
availability.in_stock:  true
inventory_level:        "In stock"
variants (all 8):       tracked: false, available: null
```

**Zendrop reports "In stock" for a product its own support says is out of stock.**
This is the same false signal that made me tell the merchant "sync failure, stock
exists" on 31 Aug, before support corrected me. It was not a one-off reading error;
the field is simply wrong, and it stays wrong days later.

Checked whether this is specific to that product. It is not. Across 45 catalog
items sampled from two searches (`pet grooming` and `pet hair remover lint`, both
`ships_from: US`), **every single variant returns `tracked: false` and
`available: null`.** There is no live stock count anywhere in the catalog on this
plan — `get_my_product_inventory` is gated behind "Upgrade to Select".

### Why this matters more than any single product choice

The Merchant Center suspension came from selling something we could not ship. If we
add products under a supplier feed that reports "In stock" unconditionally, we are
not reducing that risk by picking better products — we are multiplying it by the
number of products we add.

### The guardrail, and it belongs on our side

Shopify inventory tracking, currently **off** on both products (`tracksInventory:
false`), is what let all 8 cup variants keep reporting `availableForSale: true` on
zero quantity. Turning it on with a deliberate finite quantity converts an unbounded
exposure — infinite units of something that may not exist — into a bounded one: the
product marks itself Sold out after N orders, and no further customer can pay for
something we have not confirmed. Restocking the number becomes a decision we make
after checking with the supplier, not something that silently never happens.

This is proposed, not done: inventory settings are product state, which is gated on
the merchant's approval.

### On the catalog itself

Separately worth recording, from the same searches: of 45 US-supplier items, all but
two came from a supplier literally named **"Amazon Products"** — Zendrop reselling
Amazon listings, **one image each**, with Amazon marketing copy carrying claims we
are not allowed to repeat ("100% Satisfaction Guaranteen" and similar). A single
stock photo is not enough to build a product page of the standard the brush page
now holds. The one exception found so far is `1640419` (ExactFit Solutions, $11.60,
23 images).

### Pinterest, same session

Two pins published to keyword-named boards, both using real supplier photography
rather than the AI-composited images, both linking to the brush:

- `916552961685488301` → Cat Grooming — "A grooming brush with the water built in"
- `916552961685488300` → Dog Grooming — "Brushing a long coat, no bath needed"

Copy describes the mechanism only — silicone bristles, mist in the handle, USB
rechargeable, free US shipping. No percentages, no health claims.

## 2 Sep 2026 — the inventory cap does not work, and why. Plus what actually improved.

Merchant said go, so I turned Shopify inventory tracking on for the brush
(product `10320315810105`, all 5 variants) intending a finite cap of 20 units.
**The cap failed.** Recording exactly what happened, because the reason is
structural and will apply to every product we ever add.

### What happened, in order

1. `inventoryItemUpdate` set `tracked: true` on all 5 inventory items. Fine.
2. `inventorySetQuantities` against location `115449626937` → **"location not found"**.
3. `locations(first: 10)` returned **one** location, `115449168185` "Adnei-Paz
   Street 29". So I activated 20 units there. It worked — and it was a mistake.
4. Re-reading the product showed `totalInventory: 250099`, roughly 50,020 per
   variant, not 20.
5. `inventoryItem.inventoryLevels` revealed the truth: there are **two** active
   locations. `115449626937` is named **"Zendrop"** and holds **50,000 units per
   variant**. The `locations` query had simply not returned it.
6. Tried to cap the Zendrop location to 25 → **"location not found" again.**

That error is Shopify's wording for *you have no write access to a location owned
by another app's fulfillment service*. **The Zendrop location is read-only to us.**
Zendrop pushes 50,000 as its way of saying "unlimited", and we cannot lower it.

So a numeric cap is not available to us at all, on any Zendrop-sourced product.

### The mistake I made and reverted

Activating 20 units at "Adnei-Paz Street 29" put fictional stock at the merchant's
home address, at a location that physically holds nothing. Shopify could have
routed a real order there instead of to Zendrop and broken fulfilment. Removed it
with `inventoryDeactivate` on all 5 levels. Verified after: each variant now sits
at the Zendrop location only, `availableForSale: true`, store selling normally.

### What did genuinely improve, and it is not nothing

`tracksInventory` is now **true**. Before, it was false — and that is precisely what
let the cup report `availableForSale: true` on `inventoryQuantity: 0` for days.
Shopify was being handed a zero and ignoring it, because untracked items are always
purchasable.

With tracking on, **a zero from Zendrop now marks the product Sold out by itself.**
That closes the failure mode that caused the Google suspension, on Shopify's side.

### The hole that remains, stated plainly

Zendrop may never send that zero. Proven earlier today: `get_catalog_product` still
returns `in_stock: true` for the cup that their own support says is out of stock.
Tracking makes us obey a truthful zero; it cannot manufacture one from a supplier
that does not send it.

There is no API fix for that. What is left is a periodic manual check against the
supplier, and the merchant's "Notify Me" on the Zendrop product page. Any product
we add carries this same unremovable risk, so the decision to add one is a judgement
about upside, not a problem that can be engineered away.

## 2 Sep 2026 — screening candidates: the US catalog is a dead end, the CN one is not

Merchant asked me to keep screening under the criterion "real supplier, real
photography". Result overturns the assumption I started from.

### The US catalog cannot produce a product page

Ran `keyword: deshedding brush dog cat`, `ships_from: US`, `max_price: 18`.
**28 results. All 28 from supplier id 417, "Amazon Products". All 28 with exactly
one image.** Combined with the earlier sweep, that is **71 of 73 US items** from
the same Amazon reseller with a single stock photo each, and copy carrying claims
we cannot repeat — "reduce shedding by up to 95%", "100% Satisfaction Guarantee",
and in one case (`2069212`) a California Proposition 65 cancer and reproductive
harm warning sitting in the product description.

A single stock photo cannot build a page at the standard the brush page holds.
**"Import a US-supplier product with usable photography" is not an option that
exists in this catalog.** Recording that so nobody re-litigates it later.

### What the same search revealed about our own product

The brush we sell is catalog `1972847`, "Cat / Pet Steam Brush", **$1.22**, supplier
**Zendrop Fulfillment, country CN**, 7 images. The US catalog carries the same class
of product — steam/mist brushes with water tanks, USB rechargeable — at **$7.01 to
$16.37**. So switching the brush to a US supplier would cut delivery from 12–18 days
to a few days, at roughly 6 to 13 times the item cost. That is a real trade, not a
free win, and it is not decided here.

### Where the usable products actually are

Queried `supplier_id: 13` (Zendrop Fulfillment, the same supplier as our brush),
`category_id: 48` Pet Supplies, `max_price: 6`. Completely different picture:
clean English product names rather than keyword spam, and **5 to 7 images** on the
better entries.

Ranked by image count, the on-brand candidates:

| id | price | imgs | what it is |
|----|-------|------|------------|
| `2880183` | **$0.75** | 4 + 10 in description | Silicone grooming glove, hair removal, 3 colours |
| `2601723` | $3.40 | 7 | 3-in-1 portable dog water bottle and food dispenser |
| `2768078` | $1.72 | 7 | Biodegradable pet waste bags — a consumable, so repeat purchase |
| `2655648` | $2.63 | 1 | Silicone bath brush — on-brand but one image, rejected |

### Recommendation: `2880183`, the silicone grooming glove

Reasons, in order of weight:

1. **It is the brush's natural companion.** A glove for the hands-on pass, the brush
   for the coat. That is a bundle that raises order value rather than a second
   unrelated product competing for the same visitor.
2. **Same supplier as the brush**, so the shipping path and lead time are ones we
   have already measured and already disclose on the shipping policy page.
3. **$0.75.** Even at a conservative $16.90 the contribution clears our floor with
   room that no US-catalog item comes close to.
4. **14 images** across the catalog entry and its description — enough to build a
   real page.
5. **Three colours**, so it takes the same variant shape the brush already uses.

Its supplied copy claims "reducing shedding" and "promoting relaxation and
well-being". Both get rewritten; we describe the silicone nubs and what they do,
nothing about health.

The stock risk documented earlier applies to this exactly as it applies to
everything else in the catalog, and cannot be engineered away. Import is proposed
as DRAFT, not executed, pending the merchant's word.

## 2 Sep 2026 — deep research on the glove. It kills my own recommendation, and finds something worse.

Merchant asked for demand, volume, competitors and prices before deciding. Did the
research. **It rules out the product I recommended three messages earlier**, and
turns up a bigger problem with the product we already sell.

### Pinterest could not size this niche, and I am not pretending otherwise

`PINTEREST_GET_KEYWORD_TRENDS`, region US. First call silently ignored my terms
because I used `terms` instead of `include_keywords` and got the global top 50 back
("nails", "hairstyles", "wallpaper"). Re-ran correctly against `growing`, `monthly`
and `yearly`:

- `growing` filtered to glove/grooming/shedding/pet hair/dog brush/cat brush → **empty**
- `monthly`, same terms → **empty**
- `yearly` → the only match is the generic **"cats"**, at **−10% year over year**

Absence from a top-50 ranking is not absence of demand — a niche product is not
expected to rank against "nails". So this tells us the category is not a mega-term
and **nothing more**. It is not evidence against the product, and I am not going to
present it as if it were.

### Retail reality for the glove

- The category leader (Delomo) carries **85,000+ reviews at 4.5 stars** on Amazon.
  Demand is real, proven, and very large.
- Street price is **$5.53 to $12.74**, frequently discounted 29–50%.
- There is a listing badged **#1 Best Seller** with a 2026 model date, so the
  category is actively contested right now.

Our landed cost would be roughly $0.75 plus shipping, so margin at $16.90 looks
fine on a spreadsheet. It is not fine in the market. A US shopper who searches
"pet grooming glove" is offered an 85,000-review product at about $8 with two-day
delivery. We would offer an unbranded one at $16.90 with 12–18 day delivery.

**Rejecting my own recommendation as a standalone product.** The economics were
computed against our cost and never against the shelf we would be standing on.
That was the error.

### The bigger finding: our own brush is priced against the same shelf

Searched the retail price of the product Peluma already sells — a 3-in-1
rechargeable mist/steam grooming brush with a water tank. Multiple independent
listings:

| retailer | price |
|----------|-------|
| Walmart, 4-in-1 steam cat brush | **$6.99** |
| Walmart, steam brush 3-in-1 white | **$9.68** |
| Walmart, XYRSRUW steam brush | **$10.69** |
| Walmart, 2026 New Pet Steam Brush | **$11.66** |
| Walmart, cat steam brush for shedding | **$11.99** |
| Amazon, Feelneedy rechargeable steam brush | **$10.99** |

Typical range **$6.99 to $18.99, clustered at $9–$12**.

**Peluma sells it at $29.90 single and $39.90 for the two-item options.** That is
roughly **2.5× to 3.5×** what the same class of product costs on Walmart or Amazon,
against two-day delivery instead of our 12–18 days.

This is a better explanation of zero sales than any traffic theory considered so
far, and it was never checked. It should have been checked before the price was set.

### What it does and does not mean

It is not automatically fatal. Brands sell commodity goods at 3× routinely. It
requires one of: a real brand people buy into, a genuinely differentiated product,
or traffic that does not comparison-shop. Peluma currently has none of the three,
though the third is the closest to reach.

The sharp version, and it matters for the Google fight: **a 3× price survives on
impulse channels and dies on comparison channels.** Pinterest and TikTok show a
product in a moment of desire with no price row next to it. Google Shopping shows
our $29.90 in a grid beside somebody's $9.68. We have spent today restoring the
channel that is worst suited to our current pricing.

### Salvage for the glove

As a **standalone product it is rejected**. As a **bundle add-on** it is a different
proposition: at roughly $9.90 added to a $29.90 brush order it is not competing in
Amazon search results, it is competing against "add one more thing before checkout",
which is a contest we can actually win, at a cost of $0.75.

No import performed. Decision belongs to the merchant.

## 2 Sep 2026 — the real unit economics, and a correction I owe the merchant

Merchant's instinct was to cut the brush price. Before pricing anything I went and
got the numbers that were never actually verified. Two of them overturn things this
project has been treating as settled.

### Correction 1: the $21.70 landed cost is an Israel number, and I conceded it wrongly

Pulled order `#1001` from Zendrop. The full record:

```
country: IL      city: Hadera
product_cost:   $7.50
shipping_cost:  $14.20
total_cost:     $21.70
```

**That is the merchant's own test order, shipped to Hadera.** The $14.20 is
Israel shipping. Peluma sells to the United States, so $21.70 has never been the
landed cost of anything we sell.

Zendrop's own estimate for the same product to the US:

```
regular   $9.92   8 days
```

Earlier in this project I calculated $17.42, was told the other session's $21.70
was right, and wrote "הצ'אט השני צדק. אני טעיתי." **That concession was wrong.**
$7.50 product + $9.92 US shipping = **$17.42**, which is exactly the figure I had.
Both numbers were correct for different destinations; I abandoned the one that
applies to our actual market. Correcting it here in writing.

Also worth noting: Zendrop quotes **8 days** to the US, while our shipping policy
promises 12–18. We are under-promising, which is safe, but it is not accurate.

### Correction 2: per-variant costs, from Shopify's own `unitCost`

| variant | price | unitCost | weight |
|---------|-------|----------|--------|
| White brush | $29.90 | **$3.76** | 173 g |
| Purple brush | $29.90 | **$3.61** | 125 g |
| White brush + lint roller | $39.90 | $22.20 | 307 g |
| Milk brown brush + lint roller | $39.90 | $22.20 | 307 g |
| Two brushes | $39.90 | $20.16 | 307 g |

The $22.20 and $20.16 are landed-to-Israel figures Zendrop wrote back after order
`#1001`; the $3.76 and $3.61 are product-only. Different units in the same column,
so the table cannot be read straight. Using the invoice instead:

**US landed cost, single brush:** $3.76 + $9.92 = **$13.68**
**US landed cost, set:** $7.50 + $9.92 = **$17.42**

**Contribution at today's prices** (payment fees ~3.5%):
- Single at $29.90 → **≈ $15.17**
- Set at $39.90 → **≈ $21.08**

Both clear the $17 gate the merchant set, or come close. The margin was never the
problem.

### Why cutting the price does not work

Market retail for this product, verified across six listings today: **$6.99 to
$11.99**, clustered $9–$12.

**Our landed cost of $13.68 is higher than the price Walmart charges a consumer.**

So the merchant's instinct — drop the price to compete — is arithmetically
unavailable:

| our price | contribution |
|-----------|--------------|
| $29.90 (today) | $15.17 |
| $24.90 | $10.35 |
| $19.90 | $5.52 |
| $16.90 | $2.62 |
| $11.99 (market) | **negative** |

We cannot reach the shelf price. Walmart sells the finished item to a shopper for
less than it costs us to buy one and ship it.

### Where the cost actually sits, and the one lever that moves it

Shipping is **$9.92 of a $13.68 landed cost — 73%.** The product is $3.76. Any
attempt to fix this by negotiating the product price is chasing the small number.

Tested whether a US-stocked supplier changes it. Product `2041986`, a US-supplier
item, ships to the US for **$6.99** against our **$9.92** from China. So domestic
sourcing saves about $3 a unit and cuts delivery from 8 days to a few — but US
catalog items cost $7–$16 rather than $3.76, so total landed cost rises. It buys
speed, not margin.

### What this means for the decision in front of us

The brush's economics are fine and its price is not the problem to solve. The
problem is which shelf we stand on. Restating the conclusion from the pricing
research, now with the cost data behind it: **we cannot win a comparison, so we
must not be shown in one.** That is an argument about channel, not price.

No price was changed. This is analysis for the merchant's decision.

## 2 Sep 2026 — full product screen against verified US retail. One survivor.

Merchant's point, and he is right: the brush was chosen without anyone checking
what it retails for in the US. Ran the screen that should have run first. Rule
applied: **we must be able to price at or below US retail and still clear ~$17
contribution.** Equivalent to landed cost ≤ market price − $18.50.

Every landed cost below is Zendrop product price + Zendrop's own US shipping quote
(all 8 days). Every market price is from live Walmart / Chewy / Amazon listings
pulled today, not estimated.

| candidate | product | ship US | landed | verified US retail | verdict |
|-----------|---------|---------|--------|--------------------|---------|
| Mist brush *(what we sell)* | $3.76 | $9.92 | **$13.68** | $6.99–$11.99 | **fail** — costs more than the shelf price |
| Silicone grooming glove | $0.75 | ~$9 | ~$9.75 | $5.53–$12.74 | **fail** |
| Ultrasonic bark deterrent | $12.02 | $8.34 | **$20.36** | $8.99–$20.99 | **fail** — lands at the top of the range |
| Window cat hammock | $15.08 | **$32.09** | $47.17 | not verified | **fail** — shipping is 2× the product |
| Expandable cat backpack | $16.80 | **$34.10** | $50.90 | $34.00–$51.99 | **fail** — lands at the top of the range |
| **Smart wireless water fountain** | $20.61 | $19.34 | **$39.95** | **$30s–$90.99** | **pass** |

### The structural reason five of six failed

Shipping scales with volume, and it squeezes from both ends:

- Anything **cheap** dies against a ~$9 shipping floor. A $0.75 glove lands near
  $10 against an $8 shelf price. No cheap product in this catalog can ever work.
- Anything **bulky** dies against shipping that outgrows the product. The cat
  hammock costs $15 and ships for $32.

The window that survives is narrow: **dense, compact, and expensive** — high value
per gram. That is the whole rule, and it explains every row above.

### The survivor: `2922283`, Smart Pet Wireless Water Dispenser

2.6 L, stainless steel tray, cordless, silent, four colours, **0.67 kg**. Five
catalog images plus four more in the description — nine usable.

Landed **$39.95**. Verified comparables: a Walmart cordless stainless fountain with
the same 2.6 L tank sits at **$90.99**; the wider category runs from the $30s up.

| our price | contribution after ~3.5% fees |
|-----------|-------------------------------|
| $54.90 | $13.03 |
| **$59.90** | **$17.85** |
| $64.90 | $22.68 |

**$59.90 clears the gate and sits well under the $90.99 comparable** — the first
time in this project a price is defensible from below rather than 3× from above.

### Risks, stated rather than buried

- The **$19.34 shipping is a Zendrop quote, not a paid invoice.** No US order has
  ever been placed by this store. Confirmed only by a real order.
- Cheaper fountains exist in the $30s. We beat the premium listings, not the floor.
- It is an **electrical product with a pump**, so defect and return rates run higher
  than a brush. Refund exposure is real at $59.90.
- The Zendrop stock-signal problem documented this morning applies unchanged.

### On the brush

Not proposing a price cut. At $29.90 it contributes ~$15 when it sells; cutting the
price cannot reach a shelf that sits below our cost, it only shrinks the margin.
It stays as an impulse-channel product while Pinterest runs.

Nothing imported. Decision belongs to the merchant.
