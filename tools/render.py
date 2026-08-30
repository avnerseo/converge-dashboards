#!/usr/bin/env python3
"""Build a dashboard's HTML from its JSON.

This is the half that removes the failure class: the daily run produces data,
and the page is assembled deterministically from it. CSS and JS live in
templates/ and are no longer rewritten on every run, so they cannot be
corrupted by a partial write.

    python3 tools/render.py stocks              # -> stdout
    python3 tools/render.py stocks -o index.html
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import domlite  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES = os.path.join(ROOT, "templates")

BRAND = ('<div class="brand-lockup"><span class="brand-mark"></span>'
         '<span class="brand-text"><span class="brand-word">Converge'
         '<span class="brand-tm">™</span></span>'
         '<span class="brand-tagline">Stock Intelligence</span></span></div>')

esc = domlite.escape_text
att = domlite.escape_attr


def asset(name):
    with open(os.path.join(TEMPLATES, name), encoding="utf-8") as fh:
        return fh.read().strip()


def tag(name, inner="", **attrs):
    parts = []
    for k, v in attrs.items():
        if v in (None, False):
            continue
        parts.append(' %s="%s"' % (k.rstrip("_").replace("_", "-"), att(str(v))))
    return "<%s%s>%s</%s>" % (name, "".join(parts), inner, name)


# --------------------------------------------------------------------------
# shared blocks
# --------------------------------------------------------------------------

def h2(block):
    icon = block.get("icon")
    cls = "icon-badge" + (" " + block["icon_variant"] if block.get("icon_variant") else "")
    badge = tag("span", esc(icon), class_=cls) if icon else ""
    return tag("h2", badge + esc(block.get("title") or ""))


def section_head(block):
    out = h2(block)
    if block.get("subtitle"):
        out += tag("div", block["subtitle"], class_="section-sub")
    return out


def kpi_row(items, cls="kpi-row"):
    tiles = "".join(
        tag("div",
            tag("div", esc(k["value"] or ""), class_="kpi-value ltr") +
            tag("div", esc(k["label"] or ""), class_="kpi-label"),
            class_="kpi-tile")
        for k in items)
    return tag("div", tiles, class_=cls)


def sources_block(sources):
    if not sources:
        return ""
    inner = " ".join(tag("a", esc(s["name"]), href=s["url"]) for s in sources)
    return tag("div", inner, class_="sources")


def chip_row(chips):
    if not chips:
        return ""
    inner = " ".join(
        tag("span", esc(c["text"]),
            class_="chip" + (" " + c["kind"] if c.get("kind") else ""))
        for c in chips)
    return tag("div", inner, class_="chip-row")


def table_block(spec, table_id=None, table_class=None):
    head = "".join(
        tag("th", esc(col["text"]),
            onclick=("sortTable('%s',%d)" % (table_id, i)) if col.get("sortable") and table_id else None)
        for i, col in enumerate(spec.get("columns", [])))
    body = []
    for row in spec.get("rows", []):
        cells = "".join(tag("td", c.get("html") or "", class_=c.get("class"))
                        for c in row["cells"])
        body.append(tag("tr", cells,
                        data_ticker=row.get("ticker"), data_sector=row.get("sector")))
    return tag("div",
               tag("table", tag("thead", tag("tr", head)) + tag("tbody", "\n".join(body)),
                   id=table_id, class_=table_class),
               class_="tbl-wrap")


# --------------------------------------------------------------------------
# stocks
# --------------------------------------------------------------------------

def stock_card(card, risk=False):
    ticker = tag("span", esc(card.get("ticker") or ""), class_="ticker ltr")
    price = tag(("div" if risk else "span"), esc(card["price"]["raw"]), class_="price ltr")
    if risk:
        badge = tag("span", esc(card.get("risk_badge") or ""), class_="risk-badge")
        head = tag("div", ticker + badge, class_="stock-head") + price
    else:
        head = tag("div", ticker + price, class_="stock-head")

    body = chip_row(card.get("chips"))
    if card.get("rationale"):
        body += tag("div", card["rationale"], class_="rationale")
    if card.get("risk_note"):
        body += tag("div", card["risk_note"], class_="risk-note")
    body += sources_block(card.get("sources"))

    return tag("div", head + body,
               class_="stock-card risk-card" if risk else "stock-card",
               data_ticker=card.get("ticker"),
               data_name=None if risk else card.get("name"),
               data_sector=None if risk else card.get("sector"))


def sectors_in(data):
    """Filter options come from the rows themselves, so they cannot drift."""
    found = set()
    for tier in ("tier1", "tier2"):
        for c in (data.get(tier) or {}).get("cards", []):
            if c.get("sector"):
                found.add(c["sector"])
    for tab in ((data.get("tables") or {}).get("tabs") or {}).values():
        for row in tab.get("rows", []):
            if row.get("sector"):
                found.add(row["sector"])
    return sorted(found)


def quicknav(data):
    qn = data.get("quicknav") or {}
    opts = tag("option", esc(qn.get("all_sectors_label") or ""), value="")
    opts += "".join(tag("option", esc(s), value=s) for s in sectors_in(data))
    row = tag("div",
              '<input id="globalSearch" class="search-input" placeholder="%s" oninput="filterAll()">'
              % att(qn.get("search_placeholder") or "") +
              tag("select", opts, id="sectorFilter", class_="sector-select",
                  onchange="filterAll()"),
              class_="qn-row")
    links = "".join(tag("a", esc(l["label"]), href=l["href"]) for l in qn.get("links", []))
    return tag("nav", row + tag("div", links, class_="qn-links"),
               class_="quicknav", id="quicknav")


def render_stocks(data):
    out = []
    add = out.append

    header = tag("div",
                 BRAND + "\n" + tag("h1", esc(data["title"] or "")) +
                 tag("div", data.get("subtitle") or "", class_="subtitle") +
                 tag("div", "".join(tag("span", esc(b), class_="badge")
                                    for b in data.get("badges", [])),
                     class_="meta-row"))
    header += tag("button", "🌓 מצב כהה/בהיר", class_="theme-toggle", onclick="toggleTheme()")
    add(tag("header", header, class_="top"))

    if data.get("disclaimer"):
        add(tag("div", data["disclaimer"], class_="disclaimer"))
    if data.get("run_note"):
        add(tag("div", data["run_note"], class_="today-note"))
    add(quicknav(data))
    add(tag("section", kpi_row(data.get("kpis", []))))

    for key in ("tier1", "tier2"):
        block = data[key]
        cards = "\n".join(stock_card(c) for c in block["cards"])
        add(tag("section", section_head(block) + tag("div", cards, class_="tier1-grid"), id=key))

    tables = data.get("tables") or {}
    tabs = tables.get("tabs") or {}
    btns = "".join(
        tag("button", esc(tabs[k]["label"]),
            class_="tab-btn active" if i == 0 else "tab-btn",
            onclick="switchTab('tab%s')" % k)
        for i, k in enumerate(sorted(tabs)))
    inner = section_head(tables) + tag(
        "div",
        tag("div", btns, class_="tabs") +
        tag("button", "⬇ CSV", class_="csv-btn", onclick="exportCSV()"),
        class_="tabs-row")
    for i, k in enumerate(sorted(tabs)):
        spec = tabs[k]
        panel = table_block(spec, table_id="table" + k)
        for note in spec.get("notes", []):
            panel += tag("div", note, class_="excluded-box")
        inner += "\n" + tag("div", panel, id="tab" + k,
                            class_="tab-panel active" if i == 0 else "tab-panel")
    add(tag("section", inner, id="tables"))

    hr = data["highrisk"]
    inner = section_head(hr)
    if hr.get("banner"):
        inner += tag("div", hr["banner"], class_="highrisk-banner")
    if hr.get("kpis"):
        inner += kpi_row(hr["kpis"], cls="risk-kpi-row")
    inner += tag("div", "\n".join(stock_card(c, risk=True) for c in hr["cards"]),
                 class_="tier1-grid")
    if hr.get("flag_note"):
        inner += tag("div", hr["flag_note"], class_="flag-note")
    add(tag("section", inner, id="highrisk"))

    sent = data["sentiment"]
    head = "".join(tag("th", esc(t)) for t in ("טיקר", "מהות", "סיווג"))
    rows = "\n".join(
        tag("tr",
            tag("td", esc(r["ticker"]), class_="tk") +
            tag("td", r["note"] or "") +
            tag("td", tag("span", esc(r["classification"]), class_=r.get("tag_kind"))
                if r.get("tag_kind") else esc(r["classification"]),
                class_="dir-%s" % r["direction"] if r.get("direction") else None))
        for r in sent["rows"])
    add(tag("section",
            section_head(sent) +
            tag("div", tag("table", tag("thead", tag("tr", head)) + tag("tbody", rows),
                           class_="sent-table"), class_="tbl-wrap"),
            id="sentiment"))

    chart = data["sector_chart"]
    add(tag("section",
            section_head(chart) +
            tag("div",
                '<svg class="bar-chart" id="sectorSvg" viewBox="0 0 900 320"></svg>' +
                tag("div", chart.get("legend") or "", class_="chart-legend"),
                class_="chart-wrap"),
            id="sectorchart"))

    cmp_ = data["compare"]
    add(tag("section",
            section_head(cmp_) + table_block(cmp_, table_class="compare-table"),
            id="compare"))

    meth = data["methodology"]
    add(tag("section",
            section_head(meth) +
            tag("div", "".join(tag("p", p) for p in meth["paragraphs"]), class_="prose"),
            id="methodology"))

    tr = data.get("transparency")
    if tr:
        add(tag("section",
                section_head(tr) +
                tag("ul", "\n".join(tag("li", i) for i in tr["items"]),
                    class_="transparency-list"),
                id="transparency"))

    add(tag("footer", data.get("footer") or ""))
    return document(data, "stocks", "\n".join(out))


# --------------------------------------------------------------------------

def document(data, template, body):
    title = data.get("page_title") or data.get("title") or "Converge"
    return (
        "<!DOCTYPE html>\n"
        '<html lang="he" dir="rtl">\n<head>\n<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        "<title>%s</title>\n<style>\n%s\n</style>\n</head>\n<body>\n"
        '<div class="wrap">\n%s\n</div>\n<script>\n%s\n</script>\n</body>\n</html>\n'
        % (esc(title), asset(template + ".css"), body, asset(template + ".js"))
    )


RENDERERS = {"stocks": render_stocks}


def render(name, data=None):
    if data is None:
        with open(os.path.join(ROOT, "data", name, "latest.json"), encoding="utf-8") as fh:
            data = json.load(fh)
    return RENDERERS[name](data)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dashboard", choices=sorted(RENDERERS))
    ap.add_argument("-o", "--out", help="write here instead of stdout")
    ap.add_argument("--data", help="render this JSON file instead of data/<name>/latest.json")
    args = ap.parse_args()

    data = None
    if args.data:
        with open(args.data, encoding="utf-8") as fh:
            data = json.load(fh)
    html = render(args.dashboard, data)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(html)
        print("wrote %s (%d bytes)" % (args.out, len(html)))
    else:
        sys.stdout.write(html)
    return 0


if __name__ == "__main__":
    sys.exit(main())
