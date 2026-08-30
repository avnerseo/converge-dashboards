#!/usr/bin/env python3
"""
Converge dashboard  ->  render payload (the "feed adapter").

This is the only customer-specific file in the pipeline. Everything downstream
(scene, capture, encode) consumes the generic payload schema and knows nothing
about stocks. A second customer means a second adapter, not a second engine.

Reads:  index.html  (the daily Converge dashboard, already produced by this repo)
Writes: a payload JSON on stdout or to --out

Deliberately stdlib-only: a feed adapter that pulls in a dependency tree is a
thing that breaks unattended at 05:00.
"""
import argparse
import json
import re
import sys
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

HEB_MONTHS = ["בינואר", "בפברואר", "במרץ", "באפריל", "במאי", "ביוני",
              "ביולי", "באוגוסט", "בספטמבר", "באוקטובר", "בנובמבר", "בדצמבר"]

# "$381.60 +0.51% (28.8)"  /  "$1,174.61 −0.13% (28.8)"
PRICE_RE = re.compile(
    r"\$(?P<price>[\d,]+\.?\d*)\s*(?P<sign>[+−-])(?P<pct>[\d.]+)%"
)


class CardParser(HTMLParser):
    """Pulls .stock-card blocks out of the dashboard, per section."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.section = None
        self.cards = []
        self._card = None
        self._depth = 0
        self._capture = None
        self._buf = []
        self._meta_badges = []
        self._in_badge = False

    # -- helpers ---------------------------------------------------------
    def _flush(self):
        if self._capture and self._card is not None:
            txt = re.sub(r"\s+", " ", "".join(self._buf)).strip()
            if txt:
                prev = self._card.get(self._capture, "")
                self._card[self._capture] = (prev + " " + txt).strip()
        self._buf = []
        self._capture = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = a.get("class", "")

        if tag == "section" and a.get("id"):
            self.section = a["id"]

        if "badge" in cls.split() and self._card is None:
            self._in_badge = True
            self._buf = []

        if self._card is not None:
            self._depth += 1
            if self._capture:
                # nested markup inside a captured block: keep the text, drop tags
                return
            if "ticker" in cls:
                self._capture, self._buf = "_ticker", []
            elif "price" in cls:
                self._capture, self._buf = "price_raw", []
            elif "chip" in cls.split() or "risk-badge" in cls:
                self._capture, self._buf = "_chip", []
            elif "rationale" in cls:
                self._capture, self._buf = "rationale", []
            return

        if tag == "div" and "stock-card" in cls.split():
            self._card = {
                "ticker": a.get("data-ticker", ""),
                "name": a.get("data-name", ""),
                "sector": a.get("data-sector", ""),
                "section": self.section,
                "chips": [],
            }
            self._depth = 1

    def handle_endtag(self, tag):
        if self._in_badge and tag in ("span", "div"):
            self._meta_badges.append(re.sub(r"\s+", " ", "".join(self._buf)).strip())
            self._in_badge = False
            self._buf = []
            return
        if self._card is None:
            return
        if self._capture:
            key = self._capture
            self._flush()
            if key == "_chip":
                chip = self._card.pop("_chip", "").strip()
                if chip:
                    self._card["chips"].append(chip)
        self._depth -= 1
        if self._depth <= 0:
            self.cards.append(self._card)
            self._card = None

    def handle_data(self, data):
        if self._capture or self._in_badge:
            self._buf.append(data)


def parse_price(raw):
    m = PRICE_RE.search(raw or "")
    if not m:
        return None, None
    price = float(m.group("price").replace(",", ""))
    pct = float(m.group("pct"))
    if m.group("sign") in ("−", "-"):
        pct = -pct
    return price, pct


def extract_updated(badges, html):
    for b in badges:
        m = re.search(r"(\d{1,2})\s+(" + "|".join(HEB_MONTHS) + r")\s+(\d{4})", b)
        if m:
            day, month, year = int(m.group(1)), HEB_MONTHS.index(m.group(2)) + 1, int(m.group(3))
            return f"{year:04d}-{month:02d}-{day:02d}", b.replace("🕐", "").strip()
    return None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", nargs="?", default="index.html",
                    help="path to the Converge dashboard HTML")
    ap.add_argument("--out", "-o", help="write payload here (default: stdout)")
    ap.add_argument("--top", type=int, default=5, help="how many tier-1 cards to feature")
    args = ap.parse_args()

    html = Path(args.source).read_text(encoding="utf-8")
    p = CardParser()
    p.feed(html)

    date_iso, updated_label = extract_updated(p._meta_badges, html)
    if not date_iso:
        print("extract_feed: could not find the run date in the dashboard header",
              file=sys.stderr)
        return 2

    rows = []
    for c in p.cards:
        price, pct = parse_price(c.get("price_raw", ""))
        if price is None:
            continue
        rows.append({
            "ticker": c["ticker"],
            "name": c["name"] or c["ticker"],
            "sector": c["sector"],
            "tier": c["section"],
            "price": price,
            "change_pct": pct,
            "chip": (c["chips"][0] if c["chips"] else ""),
            "rationale": c.get("rationale", ""),
        })

    tier1 = [r for r in rows if r["tier"] == "tier1"]
    risk = [r for r in rows if r["tier"] == "highrisk"]
    if not tier1:
        print("extract_feed: no tier-1 cards found — dashboard layout changed?",
              file=sys.stderr)
        return 2

    # Deterministic ordering: strongest conviction first, ties broken by ticker.
    # No clock, no randomness — the same dashboard always yields the same payload.
    def conviction(r):
        m = re.match(r"(\d)/3", r["chip"])
        return int(m.group(1)) if m else 0

    tier1.sort(key=lambda r: (-conviction(r), r["ticker"]))
    featured = tier1[: args.top]

    movers = sorted(rows, key=lambda r: (-abs(r["change_pct"]), r["ticker"]))[:3]

    payload = {
        "schema": "converge.video.v1",
        "date": date_iso,
        "brand": {
            "name": "Converge",
            "tagline": "Stock Intelligence",
            "accent": "#3d7bff",
        },
        "title": "מניות שכבה 1",
        "subtitle": "התכנסות בין שלוש מתודולוגיות עצמאיות",
        "updated_label": updated_label,
        "kpi": {
            "tier1_count": len(tier1),
            "risk_count": len(risk),
            "universe": len(rows),
        },
        "featured": featured,
        "movers": movers,
        "disclaimer": "לא ייעוץ השקעות. למחקר בלבד.",
    }

    out = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(out + "\n", encoding="utf-8")
        print(f"extract_feed: {args.out}  "
              f"({len(featured)} featured, {len(rows)} rows, date {date_iso})",
              file=sys.stderr)
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
