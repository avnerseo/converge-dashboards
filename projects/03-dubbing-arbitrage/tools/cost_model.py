#!/usr/bin/env python3
"""
Dubbing cost model — project 03.

Parameterised by rate, target-language count and source minutes, so that
confirmed vendor numbers drop straight in once someone can read the real
pricing pages (see VERIFICATION_REQUEST.md).

NOTHING HERE IS A MEASUREMENT. Every default rate below is an UNVERIFIED
placeholder taken from the brief's own quoted range. The point of the script is
to show how much the answer moves when the unknowns move -- not to assert a
number. Pass --rate to override with a real figure.

Usage:
    python3 cost_model.py                          # sensitivity table over the unknowns
    python3 cost_model.py --rate 0.55 --langs 5 --minutes 10
    python3 cost_model.py --rate 0.55 --langs 5 --minutes 10 --monthly-videos 20
"""
import argparse

# --- Unverified inputs -------------------------------------------------------
# Source: projects/03-dubbing-arbitrage/BRIEF.md, which itself sources vendor
# blogs and marketing comparison pages. Treat as a range to explore, not a price.
CLAIMED_RATE_LOW = 0.10   # $/finished minute, bottom of the quoted range
CLAIMED_RATE_ENTRY_LOW = 0.55
CLAIMED_RATE_ENTRY_HIGH = 2.40
CLAIMED_RATE_HIGH = 3.00

# Studio dubbing, $/hour/language, from the same unverified quote.
STUDIO_PER_HOUR_LOW = 5000
STUDIO_PER_HOUR_HIGH = 15000


def cost(rate, minutes, langs, per_source_minute):
    """Cost of dubbing one `minutes`-long source video into `langs` languages.

    per_source_minute=True  -> the CLAIMED model: billed once, language count free.
    per_source_minute=False -> the per-target-language model.
    """
    return rate * minutes * (1 if per_source_minute else langs)


def studio_cost(minutes, langs, per_hour):
    return per_hour * (minutes / 60.0) * langs


def fmt(x):
    return f"${x:,.2f}" if x < 1000 else f"${x:,.0f}"


def report(rate, minutes, langs, monthly_videos=None):
    claimed = cost(rate, minutes, langs, True)
    actual = cost(rate, minutes, langs, False)
    delta = actual - claimed

    print(f"\n  One {minutes:g}-minute source video into {langs} language(s), at ${rate:g}/finished min")
    print("  " + "-" * 66)
    print(f"  {'Billed per source minute (the CLAIM)':<46}{fmt(claimed):>18}")
    print(f"  {'Billed per target language':<46}{fmt(actual):>18}")
    print(f"  {'Cost of the claim being wrong':<46}{fmt(delta):>18}")
    print(f"  {'YouTube auto-dub, source->English':<46}{'$0.00':>18}   <- see FINDINGS.md")

    print(f"\n  Studio dubbing, same job")
    print("  " + "-" * 66)
    lo = studio_cost(minutes, langs, STUDIO_PER_HOUR_LOW)
    hi = studio_cost(minutes, langs, STUDIO_PER_HOUR_HIGH)
    print(f"  {'at $5,000/hr/lang':<46}{fmt(lo):>18}")
    print(f"  {'at $15,000/hr/lang':<46}{fmt(hi):>18}")
    if actual > 0:
        print(f"  {'AI is cheaper by (per-language model)':<46}{f'{lo/actual:,.0f}x - {hi/actual:,.0f}x':>18}")

    # Break-even: at what $/min does AI stop beating the cheapest studio quote?
    # studio_cost == cost  =>  rate_be = per_hour * minutes/60 * langs / (minutes * langs)
    #                                  = per_hour / 60   (independent of minutes and langs)
    print(f"\n  Break-even rate vs studio")
    print("  " + "-" * 66)
    print(f"  {'AI stops winning above':<46}{fmt(STUDIO_PER_HOUR_LOW/60.0)+'/min':>18}")
    print("  (independent of video length and language count -- both sides scale")
    print("   identically, so the comparison collapses to $/hour vs $/minute.)")
    print("  The quoted AI range tops out at $3.00/min, i.e. ~2.8% of break-even.")
    print("  => The AI-vs-studio comparison is not close, and never was the")
    print("     decision. The real comparison is AI-vs-$0 (YouTube).")

    if monthly_videos:
        print(f"\n  At {monthly_videos} videos/month")
        print("  " + "-" * 66)
        print(f"  {'Per-target-language model':<46}{fmt(actual*monthly_videos)+'/mo':>18}")
        print(f"  {'Annualised':<46}{fmt(actual*monthly_videos*12)+'/yr':>18}")


def sensitivity(minutes=10, langs=5):
    print(f"\n  Sensitivity: {minutes:g}-min video, {langs} languages")
    print("  All rates UNVERIFIED -- from the brief's quoted range.\n")
    print(f"  {'$/min':>8} {'per-source-min':>16} {'per-language':>14} {'delta':>12}")
    print("  " + "-" * 54)
    for rate, label in [
        (CLAIMED_RATE_LOW, "range low"),
        (CLAIMED_RATE_ENTRY_LOW, "entry low"),
        (CLAIMED_RATE_ENTRY_HIGH, "entry high"),
        (CLAIMED_RATE_HIGH, "range high"),
    ]:
        c = cost(rate, minutes, langs, True)
        a = cost(rate, minutes, langs, False)
        print(f"  {rate:>8.2f} {fmt(c):>16} {fmt(a):>14} {fmt(a-c):>12}   {label}")
    print("\n  Read across: even at the top of the quoted range, the entire")
    print("  billing-model question is worth under $150 per video. That is the")
    print("  whole prize the project was chartered to capture.")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--rate", type=float, help="$ per finished minute (per language)")
    p.add_argument("--langs", type=int, default=5, help="number of target languages")
    p.add_argument("--minutes", type=float, default=10, help="source video length in minutes")
    p.add_argument("--monthly-videos", type=int, default=None)
    a = p.parse_args()

    print("=" * 70)
    print("  DUBBING COST MODEL -- all vendor rates are UNVERIFIED placeholders")
    print("=" * 70)
    if a.rate:
        report(a.rate, a.minutes, a.langs, a.monthly_videos)
    else:
        sensitivity(a.minutes, a.langs)
        report(CLAIMED_RATE_ENTRY_LOW, a.minutes, a.langs, a.monthly_videos)
    print()
