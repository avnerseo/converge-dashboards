#!/usr/bin/env python3
"""
Catch the methodology changing before the ledger absorbs the change in silence.

The version files in this directory are a record of what already happened. On
their own they rot: the dashboard rewrites index.html every day, and tomorrow's
run will publish under some rule set nobody registered. Its picks would land in
the ledger with a null stamp, or — worse — under a version whose rules they were
never produced by.

So this runs after the daily update and answers one question: does the file that
was just committed still publish the rules of the newest registered version?

The detector is the evidence itself. Every version quotes the clauses in
index.html that establish its rules, and `resolve.py --verify` already checks
those quotes are really there. Here the same quotes are checked against a commit
no version claims. A quote that has gone missing IS the rule change, and the
script says which one.

Quotes tagged run_context are excluded — "this run found two candidates" is not
a rule and never recurs verbatim. Only rule quotes gate.

Two other things get checked, because both have already gone wrong once:

  * markup. Ticker markup moved from data-q to data-ticker on 2026-08-27 and
    six publication days silently left the ledger. If the cards in a new commit
    carry neither, the extractor is about to go quiet again.
  * carry-forward. A version that persists picks between runs turns a
    republication into something that must never be scored as a new entry. It
    appeared once, unannounced, and lasted a day.

  python3 drift.py            check every commit no version claims
  python3 drift.py --commit X check one

Exit codes, so this can gate a daily job:
  0  every publishing commit is claimed, rules verified
  1  unclaimed commit, rules unchanged -> add the commit to the newest version
  2  the rules changed -> write the next version before scoring anything
"""
import re, sys, json, argparse, difflib
import resolve as meth

SECTIONS = ("methodology", "tier1", "transparency")


def raw_section(html, sid):
    # Terminate on the closing tag, not on the next <section: transparency is
    # the last section on the page, and a lookahead for a following section
    # silently returns nothing for it — which reads as "the rule is gone".
    m = re.search(rf'<section id="{sid}">.*?</section>', html, re.S)
    return m.group(0) if m else ""


def section(html, sid):
    """The rule-bearing part of a section, normalised.

    For tier1 that is the section-sub line, which states the selection rule —
    not the cards, which are the output of the rule. Diffing the cards would
    bury every real change under a wall of that day's picks.
    """
    raw = raw_section(html, sid)
    if sid == "tier1":
        sub = re.search(r'<div class="section-sub">(.*?)</div>', raw, re.S)
        raw = sub.group(1) if sub else re.sub(r'<div class="stock-card".*', "", raw, flags=re.S)
    return meth._norm(raw)


def rule_text(html):
    """The parts of the page that can carry a rule, normalised."""
    return {s: section(html, s) for s in SECTIONS}


def claimed_commits(vs):
    return {c for v in vs.values() for c in v["published"]["commits"]}


def publishing_commits():
    """Commits touching index.html that actually publish a tier-1 section."""
    out = []
    for line in meth.git("log", "--reverse", "--format=%H %ad", "--date=short",
                         "--", "index.html").strip().split("\n"):
        if not line:
            continue
        sha, date = line.split()
        html = meth.git("show", f"{sha}:index.html")
        if re.search(r'<section id="tier1"', html) and "stock-card" in html:
            out.append((sha[:7], date, html))
    return out


def check(sha, date, html, vs, newest):
    """Compare one unclaimed commit against the newest registered rule set."""
    problems, notes = [], []

    missing = []
    for ev in newest.get("evidence", []):
        if ev.get("kind") != "rule":
            continue
        where = ev["where"].split("§")[1].split(" ")[0] if "§" in ev["where"] else None
        hay = section(html, where) if where in SECTIONS else \
            " ".join(rule_text(html).values())
        if meth._norm(ev["quote_he"]) not in hay:
            missing.append(ev)
    if missing:
        problems.append(
            f"{len(missing)} rule(s) quoted by {newest['version']} are no longer "
            f"in the published file:")
        for ev in missing:
            problems.append(f"    [{ev['where']}] {ev['quote_he'][:90]}…")

    # markup: can the extractor still read a ticker off these cards?
    b = raw_section(html, "tier1")
    if b:
        cards = len(re.findall(r'<div class="stock-card"', b))
        readable = len(re.findall(r'data-ticker="', b)) + \
            len(re.findall(r'class="ticker ltr">\s*[A-Z.\-]{1,6}\s*<', b))
        if cards and not readable:
            problems.append(
                f"    tier-1 has {cards} cards and the extractor can read a ticker "
                f"off none of them — the markup changed again")
        elif cards:
            notes.append(f"tier-1 cards {cards}, tickers readable {min(readable, cards)}")

    # carry-forward, stated in prose rather than in any attribute
    cf = "נשמרות בין הרצות" in " ".join(rule_text(html).values())
    was = newest["selection"]["carry_forward"]["enabled"]
    if cf != was:
        problems.append(
            f"    carry-forward is now {'ON' if cf else 'OFF'} but {newest['version']} "
            f"records it {'ON' if was else 'OFF'} — picks under this commit are "
            f"{'re-publications, not entry events' if cf else 'fresh entries again'}")

    return problems, notes


def diff_against(newest, html):
    """Show what actually changed in the rule-bearing prose."""
    if not newest["published"]["commits"]:
        return []          # a version still being written has nothing to diff against
    anchor = newest["published"]["commits"][-1]
    old = rule_text(meth.git("show", f"{anchor}:index.html"))
    new = rule_text(html)
    out = []
    for s in SECTIONS:
        if old[s] == new[s]:
            continue
        d = list(difflib.unified_diff(
            old[s].split(". "), new[s].split(". "),
            fromfile=f"{s}@{anchor} ({newest['version']})", tofile=f"{s}@new",
            lineterm="", n=0))
        out += d
    return out


def main(only=None):
    vs = meth.load_all()
    newest = vs[meth.ORDER[len(vs) - 1]]
    done = claimed_commits(vs)
    pub = publishing_commits()
    unclaimed = [(s, d, h) for s, d, h in pub
                 if s not in done and (not only or s.startswith(only) or only.startswith(s))]

    print(f"newest registered : {newest['version']}  "
          f"({newest['published']['last_date']}, {newest['rule_hash']})")
    print(f"publishing commits: {len(pub)}, claimed {len(pub) - len([1 for s,_,_ in pub if s not in done])}")

    if not unclaimed:
        print("\nOK — every publishing commit is claimed by a version.")
        return 0

    worst = 1
    for sha, date, html in unclaimed:
        print(f"\n--- {date}  {sha}  UNCLAIMED " + "-" * 34)
        problems, notes = check(sha, date, html, vs, newest)
        for n in notes:
            print(f"    {n}")
        if not problems:
            print(f"    rules match {newest['version']} — this is the same rule set, "
                  f"published again.")
            print(f"    ACTION: add \"{sha}\" to {newest['version']}.json "
                  f"published.commits, then re-run extract_ledger.py.")
            continue
        worst = 2
        for p in problems:
            print("    " + p if not p.startswith("    ") else p)
        d = diff_against(newest, html)
        if d:
            print("\n    what changed in the rule text:")
            for line in d[:40]:
                print("      " + line)
        print(f"\n    ACTION: write versions/v{len(vs)+1}.json superseding "
              f"{newest['version']}, record the change and its type, quote the new "
              f"rule, then resolve.py --freeze && resolve.py --verify.")
        print("    Do not score picks from this commit until that exists.")
    return worst


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", default=None)
    sys.exit(main(ap.parse_args().commit))
