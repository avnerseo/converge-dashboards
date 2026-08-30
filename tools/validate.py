#!/usr/bin/env python3
"""Validate a Converge dashboard before it is allowed to ship.

Runs against the HTML by extracting it first, so it checks what a reader would
actually get. Three groups of checks:

  structure    every required section exists and carries content
               (a truncated write fails here instead of reaching main)
  consistency  the headline KPI numbers still match the rows behind them
  freshness    stale or missing prices must say so; the run date is reported

    python3 tools/validate.py            # both dashboards, from the HTML
    python3 tools/validate.py --strict   # warnings become failures
"""

import argparse
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import extract  # noqa: E402

MAX_AGE_DAYS = int(os.environ.get("CONVERGE_MAX_AGE_DAYS", "3"))

# Sections that must be present and populated, per dashboard.
REQUIRED = {
    "stocks": ["tier1", "tier2", "tables", "highrisk", "sentiment",
               "compare", "methodology", "transparency"],
    "crypto": ["tier1", "tier2", "tables", "sentiment", "methodology"],
}

# Present on one dashboard but not the other. Not a failure, but worth saying
# out loud rather than letting the gap go unnoticed.
EXPECTED = {"crypto": ["transparency"]}


class Report:
    def __init__(self, name):
        self.name = name
        self.errors = []
        self.warnings = []
        self.notes = []

    def error(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)

    def note(self, msg):
        self.notes.append(msg)

    def print(self):
        print("\n%s" % self.name)
        print("-" * len(self.name))
        for m in self.notes:
            print("  ·  %s" % m)
        for m in self.warnings:
            print("  !  %s" % m)
        for m in self.errors:
            print("  ✗  %s" % m)
        if not self.errors and not self.warnings:
            print("  ✓  all checks passed")


def kpi_value(data, needle):
    """Read a headline number by the label it is shown under."""
    for k in data.get("kpis", []):
        if needle in (k.get("label") or ""):
            raw = (k.get("value") or "").replace(",", "")
            try:
                return int(raw)
            except ValueError:
                return None
    return None


def check_structure(data, rep):
    for key in REQUIRED[data["dashboard"]]:
        block = data.get(key)
        if not block:
            rep.error("section '%s' is missing entirely" % key)
            continue
        if isinstance(block, dict):
            filled = any(block.get(f) for f in
                         ("cards", "rows", "items", "paragraphs", "groups",
                          "fear_greed", "pillars"))
            if not filled and key != "tables":
                rep.error("section '%s' rendered empty" % key)

    for key in EXPECTED.get(data["dashboard"], []):
        if not data.get(key):
            rep.warn("no '%s' section — the other dashboard has one" % key)

    tables = data.get("tables") or {}
    groups = tables.get("groups") or tables.get("tabs") or {}
    found = 0
    for name, tbl in groups.items():
        if not isinstance(tbl, dict) or "rows" not in tbl:
            continue
        found += 1
        if not tbl["rows"]:
            rep.error("table '%s' has no rows" % name)
            continue
        width = len(tbl.get("columns") or [])
        ragged = [i for i, r in enumerate(tbl["rows"])
                  if width and len(r["cells"]) != width]
        if ragged:
            rep.error("table '%s': %d row(s) do not match the %d columns (first: row %d)"
                      % (name, len(ragged), width, ragged[0] + 1))
    if not found:
        rep.error("no methodology tables were found")

    for tier in ("tier1", "tier2", "highrisk"):
        for card in (data.get(tier) or {}).get("cards", []):
            who = card.get("ticker") or "<unnamed>"
            if not card.get("ticker"):
                rep.error("%s: a card has no ticker" % tier)
            if not card.get("rationale"):
                rep.error("%s/%s: no rationale text" % (tier, who))
            if tier != "highrisk" and not card.get("sources"):
                rep.warn("%s/%s: no source links" % (tier, who))


def check_consistency(data, rep):
    if data["dashboard"] != "stocks":
        return
    tabs = (data.get("tables") or {}).get("tabs") or {}
    unique = set()
    for key in ("A", "B", "C"):
        for row in (tabs.get(key) or {}).get("rows", []):
            unique.add(row.get("ticker") or row["cells"][0].get("html"))

    def count(key):
        return len((data.get(key) or {}).get("cards", []))

    pairs = [
        ("מניות ייחודיות", len(unique), "unique tickers across tables A+B+C"),
        ("שכבה 1", count("tier1"), "tier-1 cards"),
        ("סיכון גבוה", count("highrisk"), "high-risk cards"),
    ]
    for label, actual, what in pairs:
        claimed = kpi_value(data, label)
        if claimed is None:
            rep.warn("no headline number found for '%s'" % label)
        elif claimed != actual:
            rep.error("headline says %d %s, but the page contains %d"
                      % (claimed, what, actual))
        else:
            rep.note("%d %s — matches the headline" % (actual, what))


def check_freshness(data, rep, today):
    as_of = data.get("as_of")
    if not as_of:
        rep.error("no run date could be read from the page")
    else:
        age = (today - dt.date.fromisoformat(as_of)).days
        line = "run date %s (%d day%s old)" % (as_of, age, "" if age == 1 else "s")
        if age > MAX_AGE_DAYS:
            rep.warn(line + " — older than %d days" % MAX_AGE_DAYS)
        else:
            rep.note(line)

    fresh = stale = missing = 0
    for tier in ("tier1", "tier2", "highrisk"):
        for card in (data.get(tier) or {}).get("cards", []):
            p = card.get("price") or {}
            who = card.get("ticker") or "<unnamed>"
            if not p.get("available"):
                missing += 1
                if not p.get("note"):
                    rep.error("%s: price is unavailable and the page does not say why" % who)
            elif p.get("stale"):
                stale += 1
                if not (p.get("as_of") or p.get("note")):
                    rep.error("%s: price is carried over but is not dated on the page" % who)
            else:
                fresh += 1
    total = fresh + stale + missing
    if total:
        rep.note("prices: %d fresh · %d carried over · %d unavailable (of %d)"
                 % (fresh, stale, missing, total))
        if fresh == 0:
            rep.warn("no price on this page was fetched today")


CHECKS = {
    "structure": lambda d, r, today: check_structure(d, r),
    "consistency": lambda d, r, today: check_consistency(d, r),
    "freshness": check_freshness,
}


def validate_data(data, today, label=None, only=None):
    rep = Report(label or data.get("dashboard", "dashboard"))
    for name in (only or CHECKS):
        CHECKS[name](data, rep, today)
    return rep


def validate(name, today, only=None):
    label = "%s (%s)" % (name, extract.DASHBOARDS[name][0])
    try:
        data = extract.build(name)
    except Exception as exc:  # a parse failure is itself a validation failure
        rep = Report(label)
        rep.error("could not read the dashboard: %s" % exc)
        return rep
    return validate_data(data, today, label, only)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dashboards", nargs="*", metavar="DASHBOARD",
                    help="one or more of: %s (default: all)" % ", ".join(sorted(extract.DASHBOARDS)))
    ap.add_argument("--strict", action="store_true", help="treat warnings as failures")
    ap.add_argument("--only", action="append", choices=sorted(CHECKS), metavar="CHECK",
                    help="run only these checks (%s); repeatable" % ", ".join(sorted(CHECKS)))
    ap.add_argument("--today", help="override today's date (YYYY-MM-DD), for testing")
    args = ap.parse_args()

    today = dt.date.fromisoformat(args.today) if args.today else dt.date.today()
    names = args.dashboards or sorted(extract.DASHBOARDS)
    unknown = [n for n in names if n not in extract.DASHBOARDS]
    if unknown:
        ap.error("unknown dashboard(s): %s" % ", ".join(unknown))
    reports = [validate(n, today, args.only) for n in names]
    for rep in reports:
        rep.print()

    errors = sum(len(r.errors) for r in reports)
    warnings = sum(len(r.warnings) for r in reports)
    print("\n%d error(s), %d warning(s)" % (errors, warnings))
    if errors or (args.strict and warnings):
        print("FAILED — this dashboard should not be published as-is.")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
