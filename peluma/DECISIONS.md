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
