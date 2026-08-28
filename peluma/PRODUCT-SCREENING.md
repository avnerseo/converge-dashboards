# Screening a product before it goes in the store

Written 28 Aug, after a full day was spent pricing, repricing and reverting a product that
Google Shopping would have disqualified in thirty seconds.

## The rule

**No product enters the store before it is screened.** Screening is free and takes minutes.
Adding a product costs description writing, SEO, images, variant setup, shipping profile work —
and then has to be undone if the product was never viable.

## Division of labour, established by testing rather than assumption

| Task | Who | Why |
|---|---|---|
| Pull names and costs from Zendrop's US catalog | **Merchant only** | `app.zendrop.com` returns `EGRESS_BLOCKED`, and it needs the merchant's own login. Verified, not assumed. |
| Market prices, reviews, competitor check | **Claude** | `WebSearch` runs server-side and works |
| Pass / fail decision | **Claude**, on numbers | |
| Building the product in the store | **Claude** | |

`WebFetch` is blocked for every domain outside Shopify — Amazon, Walmart, eBay, Temu and
Zendrop all return `EGRESS_BLOCKED`. `WebSearch` is the only external research tool available.

## What the merchant sends

1. Zendrop → **Find Products**
2. Filter **`Ships From: US`**
3. Search `pet`, `dog`, `cat`, `grooming`
4. Pick **6–8** candidates. Do not pre-filter — send too many, screening is free.
5. Open each, click **All SKUs**, screenshot
6. Send the screenshots. Typing is not needed.

Each screenshot needs to show: product name, the `app.zendrop.com/product/…` URL, product cost,
shipping cost, total, and average shipping time.

## The four screens, in order

**1. Commodity check — Google Shopping.**
Search the product. If Temu, AliExpress or Joom carry it at a small fraction of any workable
price, it is a commodity and it is dead. The brush failed here: Temu sells it at **$3.80–$4.10
with free shipping** against a $29.90 store price and a $17.42 landed cost.

**2. Review check.**
Search for complaints. Systemic defects — leaking, buttons breaking, mould, safety — mean a
return rate that eats the margin, and returns from overseas are close to a total loss. The
brush failed here too.

**3. Margin check.**
Landed cost against the price the market actually tolerates, minus roughly 8–9% in PayPal and
Shopify fees. Below about $12 net, it does not carry the cost of acquiring a customer.

**4. Basket fit.**
Does someone buying the existing product plausibly add this one? Same-supplier products ship in
one package, so the second item avoids a second shipping charge — that is where the margin
actually compounds. Worth asking Zendrop support which candidates share a supplier.

A product must pass all four. Expect most candidates to fail; that is the screen working.

## Standing instruction from the merchant

When something is needed from the merchant, it is written as numbered steps — where to click,
what to copy, what to send back — not as a general request. And before asking, check whether it
can be done without them, and say what was checked.
