#!/usr/bin/env python3
"""
Score the Converge tier-1 ledger against a benchmark.

Reads  track/tier1_ledger.jsonl  (produced by extract_ledger.py)
Writes track/scorecard.json

Design notes that matter more than the code:

  * Absolute return is not evidence. Everything here is EXCESS return vs a
    benchmark (default SPY). A basket that returns +4% in a month the market
    returned +5% is a losing engine, not a winning one.

  * A pick is an EVENT, not a row in today's table. Entry is the first day a
    ticker appears in tier-1; it stays open until scored at a fixed horizon.
    Dropping a ticker from the dashboard does NOT close the position — that is
    precisely the accounting hole this file exists to close.

  * Horizons are fixed in advance (1w/1m/3m/6m/12m). Choosing the horizon after
    seeing the outcome is the most common way retail track records lie.

  * Statistical power: with n picks and typical single-name monthly vol of
    ~8%, detecting a 1%/month edge at 95% confidence needs roughly n>250
    pick-months. Below that the honest output is "no signal yet", and this
    script says so rather than printing a number that invites over-reading.

  * Methodology version is part of the sample definition. Picks made under
    different rule sets are different experiments; pooling them is how a
    moving definition launders itself into a single track record. This script
    does not refuse to pool — with n this small there is nothing else to do —
    but it reports the version mix beside every aggregate, so no number can be
    quoted without the reader seeing how many definitions it spans. A pick
    whose commit no version claims is not scored at all.
"""
import json, sys, os, math
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(HERE, "tier1_ledger.jsonl")
HORIZONS = {"1w": 7, "1m": 30, "3m": 91, "6m": 182, "12m": 365}
MIN_PICK_MONTHS = 250  # below this, report "no signal yet"


def load():
    with open(LEDGER) as f:
        return [json.loads(l) for l in f if l.strip()]


def positions(rows):
    """First appearance of each ticker = one opened position.

    A carried-forward row re-publishes an earlier run's pick without new
    research behind it, so it can never open a position. First-appearance
    already excludes it, but a run that carried a ticker forward before its
    own first appearance would not be an entry either — hence the explicit
    check rather than relying on ordering.
    """
    seen, out, dropped = set(), [], []
    for r in sorted(rows, key=lambda r: r["date"]):
        if r["ticker"] in seen or r["price"] is None:
            continue
        if r.get("methodology_version") is None:
            dropped.append(r)          # unstamped: rule set unknown, not scoreable
            continue
        if r.get("carried_forward"):
            continue
        seen.add(r["ticker"])
        out.append({
            "ticker": r["ticker"], "entry_date": r["date"],
            "entry_price": r["price"], "sector": r["sector"],
            "conviction": r["conviction"], "sha": r["sha"],
            "methodology_version": r["methodology_version"],
            "methodology_rule_hash": r.get("methodology_rule_hash"),
        })
    return out, dropped


def score(pos, prices, bench):
    """prices/bench: {(ticker, horizon): pct_return}. Missing -> unscored."""
    per_h = defaultdict(list)
    for p in pos:
        for h in HORIZONS:
            r, b = prices.get((p["ticker"], h)), bench.get(h)
            if r is None or b is None:
                continue
            per_h[h].append(r - b)

    card = {"positions": len(pos), "horizons": {}}
    total_pick_months = 0
    for h, xs in per_h.items():
        if not xs:
            continue
        n = len(xs)
        mean = sum(xs) / n
        sd = math.sqrt(sum((x - mean) ** 2 for x in xs) / (n - 1)) if n > 1 else None
        total_pick_months += n * (HORIZONS[h] / 30.0)
        card["horizons"][h] = {
            "n": n,
            "mean_excess_pct": round(mean, 3),
            "hit_rate": round(sum(1 for x in xs if x > 0) / n, 3),
            "stdev_pct": round(sd, 3) if sd else None,
            "t_stat": round(mean / (sd / math.sqrt(n)), 2) if sd and sd > 0 else None,
        }

    mix = defaultdict(int)
    for p in pos:
        mix[p["methodology_version"]] += 1
    card["methodology_mix"] = dict(sorted(mix.items(), key=lambda kv: int(kv[0][1:])))
    card["methodology_versions_spanned"] = len(mix)
    card["pick_months"] = round(total_pick_months, 1)
    card["powered"] = total_pick_months >= MIN_PICK_MONTHS
    card["verdict"] = (
        "scored" if card["powered"] else
        f"NO SIGNAL YET — {round(total_pick_months,1)} of ~{MIN_PICK_MONTHS} "
        f"pick-months needed before any number here means anything."
    )
    return card


if __name__ == "__main__":
    rows = load()
    pos, unstamped = positions(rows)
    # Price fetching is deliberately not wired in yet: it needs a daily
    # close-price store, not ad-hoc quote calls against a rate-limited key.
    card = score(pos, prices={}, bench={})
    card["opened_positions"] = pos
    with open(os.path.join(HERE, "scorecard.json"), "w") as f:
        json.dump(card, f, ensure_ascii=False, indent=2)
    print(json.dumps({k: v for k, v in card.items() if k != "opened_positions"},
                     ensure_ascii=False, indent=2))
    print(f"\n{len(pos)} positions opened, earliest {pos[0]['entry_date']}, "
          f"latest {pos[-1]['entry_date']}, "
          f"spanning {card['methodology_versions_spanned']} methodology versions "
          f"({', '.join(card['methodology_mix'])})")
    if unstamped:
        print(f"{len(unstamped)} row(s) not scored: no methodology version claims "
              f"their commit.")
