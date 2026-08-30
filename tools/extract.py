#!/usr/bin/env python3
"""Extract the Converge dashboards into a versioned JSON data layer.

Until now every number lived inside the HTML, so a partially written file lost
data outright and "carried forward from yesterday" survived only as a sentence
in a commit message. This turns each dashboard into data + presentation, and
makes staleness an explicit field instead of prose.

    python3 tools/extract.py                  # -> data/stocks/<as_of>.json, data/crypto/<as_of>.json
    python3 tools/extract.py --stdout stocks  # print one to stdout
"""

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import domlite  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_VERSION = 1

# Month names appear with and without the "ב" prefix across the two dashboards.
HE_MONTHS = {
    "ינואר": 1, "פברואר": 2, "מרץ": 3, "אפריל": 4, "מאי": 5, "יוני": 6,
    "יולי": 7, "אוגוסט": 8, "ספטמבר": 9, "אוקטובר": 10, "נובמבר": 11,
    "דצמבר": 12,
}

# The dashboards use a real minus sign in price deltas.
MINUS = "−"


# --------------------------------------------------------------------------
# value parsing
# --------------------------------------------------------------------------

def parse_price(raw):
    """Turn a free-text price line into a structured, honest reading.

    Recognises the three shapes the dashboards actually produce:
      "$199.77 -0.22% (28.8, לא עודכן היום)"   -> a stale quote, dated
      "מחיר: לא זמין היום (מכסת Alpha Vantage)" -> no quote, with a reason
      "$64,350.93"                              -> a fresh quote
    """
    raw = " ".join((raw or "").split())
    price = {"raw": raw, "available": False, "stale": False,
             "value": None, "change_pct": None, "as_of": None, "note": None}
    if not raw:
        return price

    if "לא זמין" in raw:
        reason = re.search(r"\(([^)]*)\)", raw)
        price["note"] = reason.group(1) if reason else "לא זמין"
        return price

    m = re.search(r"\$([\d,]+(?:\.\d+)?)", raw)
    if m:
        price["available"] = True
        price["value"] = float(m.group(1).replace(",", ""))

    m = re.search(r"([+\-" + MINUS + r"])\s*([\d.]+)\s*%", raw)
    if m:
        sign = -1 if m.group(1) in ("-", MINUS) else 1
        price["change_pct"] = sign * float(m.group(2))

    paren = re.search(r"\(([^)]*)\)", raw)
    if paren:
        inner = paren.group(1)
        d = re.match(r"\s*(\d{1,2}\.\d{1,2})\s*(?:,\s*(.*))?$", inner)
        if d:
            price["as_of"] = d.group(1)
            price["note"] = (d.group(2) or "").strip() or None
        else:
            price["note"] = inner.strip()
        # "not updated today" is the dashboard's own words for stale.
        price["stale"] = "לא עודכן" in inner or price["as_of"] is not None

    return price


def parse_updated(badge_text):
    """'🕐 עודכן: 29 באוגוסט 2026 · 05:32 UTC' -> ('2026-08-29', '05:32 UTC')."""
    m = re.search(r"(\d{1,2})\s+ב?([א-ת]+)\s+(\d{4})", badge_text or "")
    date = None
    if m and m.group(2) in HE_MONTHS:
        date = "%s-%02d-%02d" % (m.group(3), HE_MONTHS[m.group(2)], int(m.group(1)))
    t = re.search(r"(\d{1,2}:\d{2}\s*\w*)", badge_text or "")
    return date, (t.group(1).strip() if t else None)


def rich(node):
    """Content that carries inline markup (<b>, <a>) as part of its meaning."""
    if node is None:
        return None
    return " ".join(node.inner_html().split()) or None


def sources_prefix(node):
    """Leading label before the links, e.g. 'מקורות:' on the crypto cards."""
    if node is None:
        return None
    head = node.inner_html().split("<a", 1)[0]
    return " ".join(head.split()) or None


def links(node):
    out = []
    for a in node.find_all("a"):
        if not a.get("href"):
            continue
        link = {"name": a.clean_text(), "url": a.get("href")}
        if a.get("target"):
            link["target"] = a.get("target")
        out.append(link)
    return out


def chips(node):
    """Chips in a chip-row, including the bare *-tag spans crypto uses."""
    out = []
    row = node.find("div", "chip-row") or node
    for c in row.find_all("span"):
        cls = c.classes
        if "chip" in cls:
            kind = [k for k in cls if k != "chip"]
            out.append({"text": c.clean_text(), "kind": kind[0] if kind else None})
        elif any(k.endswith("-tag") for k in cls):
            out.append({"text": c.clean_text(), "kind": cls[0], "bare": True})
    return out


def table_rows(table):
    head = []
    for th in table.find_all("th"):
        col = {"text": th.clean_text(), "sortable": bool(th.get("onclick"))}
        if "numeric" in (th.get("onclick") or "") or ",true)" in (th.get("onclick") or ""):
            col["numeric"] = True
        if th.get("class"):
            col["class"] = th.get("class")
        head.append(col)
    rows = []
    body = table.find("tbody") or table
    for tr in body.find_all("tr"):
        tds = tr.find_all("td")
        if not tds:
            continue
        cells = []
        for td in tds:
            cell = {"html": rich(td)}
            if td.attrs:
                # class, and the data-sort hooks the crypto tables sort on
                cell["attrs"] = dict(td.attrs)
            cells.append(cell)
        row = {"cells": cells}
        # Filter/search hooks vary by dashboard (data-ticker, data-q, ...),
        # so keep whatever the row actually carries.
        data_attrs = {k: v for k, v in tr.attrs.items() if k.startswith("data-")}
        if data_attrs:
            row["data"] = data_attrs
        rows.append(row)
    return {"columns": head, "rows": rows}


def kpis(container):
    out = []
    for tile in container.find_all("div", "kpi-tile"):
        v = tile.find("div", "kpi-value")
        l = tile.find("div", "kpi-label")
        out.append({"value": v.clean_text() if v else None,
                    "label": l.clean_text() if l else None})
    return out


def section(doc, sid):
    for s in doc.find_all("section"):
        if s.get("id") == sid:
            return s
    return None


def heading(sec):
    """Section title, its icon, and its sub-line, kept apart so the renderer
    does not have to pick the emoji back out of the heading text."""
    if sec is None:
        return {"title": None, "icon": None, "subtitle": None}
    h = sec.find("h2")
    badge = h.find("span", "icon-badge") if h else None
    title = h.clean_text() if h else None
    icon = badge.clean_text() if badge else None
    if icon and title and title.startswith(icon):
        title = title[len(icon):].strip()
    out = {"title": title, "icon": icon,
           "subtitle": rich(sec.find("div", "section-sub"))}
    # crypto puts a space between the icon and the title, stocks does not.
    if icon and h and re.search(r"</span>\s", h.inner_html()):
        out["icon_gap"] = True
    if badge and "risk" in badge.classes:
        out["icon_variant"] = "risk"
    return out


# --------------------------------------------------------------------------
# shared pieces
# --------------------------------------------------------------------------

def common_head(doc):
    title_el = doc.find("title")
    h1 = doc.find("h1")
    sub = doc.find("div", "subtitle")
    badges = [b.clean_text() for b in doc.find_all("span", "badge")]
    updated_date, updated_time = parse_updated(" ".join(badges))
    note = doc.find("div", "today-note")
    disc = doc.find("div", "disclaimer")
    foot = doc.find("footer")
    tagline = doc.find("span", "brand-tagline")
    back = doc.find("a", "back-link")
    return {
        "page_title": title_el.clean_text() if title_el else None,
        "title": h1.clean_text() if h1 else None,
        "subtitle": rich(sub),
        "badges": badges,
        "brand_tagline": tagline.clean_text() if tagline else None,
        "back_link": ({"href": back.get("href"), "label": back.clean_text()}
                      if back else None),
        "as_of": updated_date,
        "updated_time": updated_time,
        "run_note": rich(note),
        "disclaimer": rich(disc),
        "footer": rich(foot),
    }


def prose_paragraphs(sec):
    if not sec:
        return []
    return [rich(p) for p in sec.find_all("p") if p.clean_text()]


def list_items(sec, cls=None):
    if not sec:
        return []
    ul = sec.find("ul", cls) if cls else sec.find("ul")
    if not ul:
        return []
    return [rich(li) for li in ul.find_all("li") if li.clean_text()]


# --------------------------------------------------------------------------
# stocks
# --------------------------------------------------------------------------

def stock_card(card):
    price_el = card.find("span", "price") or card.find("div", "price")
    rat = card.find("div", "rationale")
    risk = card.find("div", "risk-note")
    badge = card.find("span", "risk-badge")
    src = card.find("div", "sources")
    ticker_el = card.find("span", "ticker")
    name_el = card.find("div", "company-name")

    out = {
        "ticker": card.get("data-ticker") or (ticker_el.clean_text() if ticker_el else None),
        "name": card.get("data-name") or (name_el.clean_text() if name_el else None),
        "sector": card.get("data-sector") or None,
        "price": parse_price(price_el.clean_text() if price_el else ""),
        "chips": chips(card),
        "rationale": rich(rat),
    }
    if badge:
        out["risk_badge"] = badge.clean_text()
    if risk:
        out["risk_note"] = rich(risk)
    out["sources"] = links(src) if src else []
    return out


def extract_stocks(html):
    doc = domlite.parse(html)
    data = {"schema_version": SCHEMA_VERSION, "dashboard": "stocks"}
    data.update(common_head(doc))

    nav = doc.find("nav", "quicknav")
    if nav:
        inp = nav.find("input")
        blank = next((o for o in nav.find_all("option") if o.get("value") == ""), None)
        data["quicknav"] = {
            "search_placeholder": inp.get("placeholder") if inp else None,
            "all_sectors_label": blank.clean_text() if blank else None,
            # Short labels, deliberately not the full section headings.
            "links": [{"href": a.get("href"), "label": a.clean_text()}
                      for a in nav.find_all("a")],
        }

    top_kpi = doc.find("div", "kpi-row")
    data["kpis"] = kpis(top_kpi) if top_kpi else []

    for key in ("tier1", "tier2"):
        sec = section(doc, key)
        data[key] = {
            **heading(sec),
            "cards": [stock_card(c) for c in sec.find_all("div", "stock-card")] if sec else [],
        }

    tables_sec = section(doc, "tables")
    tabs = {}
    if tables_sec:
        labels = [b.clean_text() for b in tables_sec.find_all("button", "tab-btn")]
        panels = tables_sec.find_all("div", "tab-panel")
        for i, tid in enumerate(("tableA", "tableB", "tableC")):
            t = next((x for x in tables_sec.find_all("table") if x.get("id") == tid), None)
            if not t:
                continue
            panel = next((p for p in panels if p.get("id") == "tab" + tid[-1]), None)
            tabs[tid[-1]] = {"label": labels[i] if i < len(labels) else tid,
                             **table_rows(t)}
            if panel:
                notes = [rich(b) for b in panel.find_all("div", "excluded-box")]
                if notes:
                    tabs[tid[-1]]["notes"] = notes
    data["tables"] = {**heading(tables_sec), "tabs": tabs}

    hr = section(doc, "highrisk")
    data["highrisk"] = {
        **heading(hr),
        "banner": rich(hr.find("div", "highrisk-banner")) if hr else None,
        "kpis": kpis(hr.find("div", "risk-kpi-row")) if hr and hr.find("div", "risk-kpi-row") else [],
        "cards": [stock_card(c) for c in hr.find_all("div", "risk-card")] if hr else [],
        "flag_note": rich(hr.find("div", "flag-note")) if hr else None,
    }

    sent = section(doc, "sentiment")
    rows = []
    if sent:
        t = sent.find("table", "sent-table")
        if t:
            for tr in (t.find("tbody") or t).find_all("tr"):
                tds = tr.find_all("td")
                if len(tds) < 3:
                    continue
                direction = next((c.split("-")[1] for c in tds[2].classes
                                  if c.startswith("dir-")), None)
                tag = next((sp for sp in tds[2].find_all("span")
                            if any(c.endswith("-tag") for c in sp.classes)), None)
                rows.append({"ticker": tds[0].clean_text(),
                             "note": rich(tds[1]),
                             "classification": tds[2].clean_text(),
                             "tag_kind": tag.get("class") if tag else None,
                             "direction": direction})
    data["sentiment"] = {**heading(sent), "rows": rows}

    chart = section(doc, "sectorchart")
    data["sector_chart"] = {**heading(chart),
                            "legend": rich(chart.find("div", "chart-legend")) if chart else None}

    cmp_sec = section(doc, "compare")
    cmp_tbl = cmp_sec.find("table", "compare-table") if cmp_sec else None
    data["compare"] = {**heading(cmp_sec), **(table_rows(cmp_tbl) if cmp_tbl else {})}

    meth = section(doc, "methodology")
    data["methodology"] = {**heading(meth), "paragraphs": prose_paragraphs(meth),
                           "sources": links(meth) if meth else []}

    trans = section(doc, "transparency")
    data["transparency"] = {**heading(trans), "items": list_items(trans, "transparency-list")}
    return data


# --------------------------------------------------------------------------
# crypto
# --------------------------------------------------------------------------

def crypto_card(card):
    ticker_el = card.find("span", "ticker")
    name_el = card.find("div", "company-name")
    price_el = card.find("div", "price") or card.find("span", "price")
    rat = card.find("div", "rationale")
    src = card.find("div", "sources")
    return {
        "ticker": ticker_el.clean_text() if ticker_el else None,
        "name": name_el.clean_text() if name_el else None,
        "variant": "tier2" if "tier2-card" in card.classes else None,
        "query": card.get("data-q") or None,
        "price": parse_price(price_el.clean_text() if price_el else ""),
        "chips": chips(card),
        "rationale": rich(rat),
        "risk_note": rich(card.find("div", "risk-note")),
        "sources_prefix": sources_prefix(src),
        "sources": links(src) if src else [],
    }


def extract_crypto(html):
    doc = domlite.parse(html)
    data = {"schema_version": SCHEMA_VERSION, "dashboard": "crypto"}
    data.update(common_head(doc))

    nav = doc.find("nav", "quicknav")
    if nav:
        inp = nav.find("input")
        data["quicknav"] = {
            "search_placeholder": inp.get("placeholder") if inp else None,
            "links": [{"href": a.get("href"), "label": a.clean_text()}
                      for a in nav.find_all("a")],
        }

    top_kpi = doc.find("div", "kpi-row")
    data["kpis"] = kpis(top_kpi) if top_kpi else []

    for key, grid in (("tier1", "tier1-grid"), ("tier2", "tier2-grid")):
        sec = section(doc, key)
        data[key] = {
            **heading(sec),
            "grid_class": grid,
            "cards": [crypto_card(c) for c in sec.find_all("div", "stock-card")] if sec else [],
        }

    # One tab per category; order is meaningful, so keep it a list.
    tables_sec = section(doc, "tables")
    tabs = []
    if tables_sec:
        labels = {b.get("data-tab"): b.clean_text()
                  for b in tables_sec.find_all("button", "tab-btn")}
        for panel in tables_sec.find_all("div", "tab-panel"):
            key = (panel.get("id") or "").replace("panel-", "")
            t = panel.find("table")
            if not t:
                continue
            cap = panel.find("span", "section-sub")
            btn = panel.find("button", "csv-btn")
            tabs.append({
                "key": key,
                "label": labels.get(key),
                "caption": cap.clean_text() if cap else None,
                "csv_label": btn.clean_text() if btn else None,
                "table_id": t.get("id"),
                **table_rows(t),
            })
    data["tables"] = {**heading(tables_sec), "tabs": tabs}

    # The crypto sentiment section is a Fear & Greed dial, not a table.
    sent = section(doc, "sentiment")
    fg = {}
    if sent:
        val = sent.find("div", "fg-value")
        lbl = sent.find("div", "fg-label")
        sub = sent.find("div", "fg-sub")
        div = sent.find("div", "fg-divergence")
        fg = {
            "value": val.clean_text() if val else None,
            "label": lbl.clean_text() if lbl else None,
            "scale": sub.clean_text() if sub else None,
            "history": [h.clean_text() for h in sent.find_all("span", "fg-hist-item")],
            "divergence_note": div.clean_text() if div else None,
            "sources_prefix": sources_prefix(sent.find("div", "sources")),
            "sources": links(sent.find("div", "sources")) if sent.find("div", "sources") else [],
        }
    data["sentiment"] = {**heading(sent), "fear_greed": fg,
                         "paragraphs": prose_paragraphs(sent)}

    meth = section(doc, "methodology")
    pillars = []
    if meth:
        for col in meth.find_all("div", "converge-col"):
            h3 = col.find("h3")
            pillars.append({"title": h3.clean_text() if h3 else None,
                            "paragraphs": [rich(p) for p in col.find_all("p")]})
    prose = meth.find("div", "prose") if meth else None
    data["methodology"] = {**heading(meth), "pillars": pillars,
                           "paragraphs": prose_paragraphs(prose),
                           "sources": links(prose) if prose else []}

    trans = section(doc, "transparency")
    data["transparency"] = {**heading(trans), "items": list_items(trans)} if trans else None
    return data


# --------------------------------------------------------------------------

DASHBOARDS = {
    "stocks": ("index.html", extract_stocks),
    "crypto": ("crypto.html", extract_crypto),
}


def build(name):
    src, fn = DASHBOARDS[name]
    with open(os.path.join(ROOT, src), encoding="utf-8") as fh:
        data = fn(fh.read())
    data["source_file"] = src
    return data


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stdout", choices=sorted(DASHBOARDS), help="print one dashboard instead of writing files")
    ap.add_argument("--outdir", default=os.path.join(ROOT, "data"))
    args = ap.parse_args()

    if args.stdout:
        json.dump(build(args.stdout), sys.stdout, ensure_ascii=False, indent=2)
        print()
        return 0

    for name in sorted(DASHBOARDS):
        data = build(name)
        as_of = data.get("as_of") or "undated"
        d = os.path.join(args.outdir, name)
        os.makedirs(d, exist_ok=True)
        for path in (os.path.join(d, as_of + ".json"), os.path.join(d, "latest.json")):
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(data, fh, ensure_ascii=False, indent=2)
                fh.write("\n")
        print("%-7s as_of=%s  ->  data/%s/%s.json (+ latest.json)" % (name, as_of, name, as_of))
    return 0


if __name__ == "__main__":
    sys.exit(main())
