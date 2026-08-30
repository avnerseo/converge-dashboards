#!/usr/bin/env python3
"""Acceptance test for the renderer: prove it reproduces the live page.

Two independent checks, because either one alone can pass while something is
quietly lost:

  data   extract(render(data)) == data          nothing is dropped in transit
  page   render(extract(page)) == page          the page itself is reproducible
                                                (compared with whitespace and
                                                HTML entities normalised)

    python3 tools/roundtrip.py
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import extract  # noqa: E402
import render   # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Semantically identical spellings that neither browsers nor readers can tell
# apart; comparing them would only chase our own escaping choices.
EQUIVALENT = {"&#x27;": "'", "&#39;": "'", "&quot;": '"', "&apos;": "'"}


def normalise(html):
    html = re.sub(r">\s+<", "><", html)
    html = re.sub(r"\s+", " ", html)
    for a, b in EQUIVALENT.items():
        html = html.replace(a, b)
    return html.strip()


def walk(a, b, path=""):
    if type(a) is not type(b):
        return ["%s: %s vs %s" % (path, type(a).__name__, type(b).__name__)]
    out = []
    if isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a:
                out.append("%s.%s: appeared only after rendering" % (path, k))
            elif k not in b:
                out.append("%s.%s: lost in rendering" % (path, k))
            else:
                out += walk(a[k], b[k], "%s.%s" % (path, k))
    elif isinstance(a, list):
        if len(a) != len(b):
            out.append("%s: %d items became %d" % (path, len(a), len(b)))
        for i, (x, y) in enumerate(zip(a, b)):
            out += walk(x, y, "%s[%d]" % (path, i))
    elif a != b:
        out.append("%s:\n      before: %r\n      after:  %r"
                   % (path, str(a)[:160], str(b)[:160]))
    return out


def check_data(name):
    before = extract.build(name)
    after = extract.DASHBOARDS[name][1](render.render(name, before))
    after.setdefault("source_file", before.get("source_file"))
    return walk(before, after)


def check_page(name):
    src = os.path.join(ROOT, extract.DASHBOARDS[name][0])
    with open(src, encoding="utf-8") as fh:
        original = fh.read()
    rebuilt = render.render(name, extract.build(name))
    if normalise(original) == normalise(rebuilt):
        return []
    a, b = normalise(original), normalise(rebuilt)
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return ["%s differs from the rendered output at offset %d:\n"
                    "      page:     ...%s...\n      rendered: ...%s..."
                    % (extract.DASHBOARDS[name][0], i,
                       a[max(0, i - 70):i + 70], b[max(0, i - 70):i + 70])]
    return ["%s and the rendered output differ in length (%d vs %d)"
            % (extract.DASHBOARDS[name][0], len(a), len(b))]


def main():
    failures = 0
    for name in sorted(render.RENDERERS):
        for label, check in (("data survives a render", check_data),
                             ("the live page is reproducible", check_page)):
            problems = check(name)
            if problems:
                failures += 1
                print("✗ %s — %s" % (name, label))
                for p in problems[:10]:
                    print("    %s" % p)
                if len(problems) > 10:
                    print("    ... and %d more" % (len(problems) - 10))
            else:
                print("✓ %s — %s" % (name, label))

    skipped = sorted(set(extract.DASHBOARDS) - set(render.RENDERERS))
    if skipped:
        print("\nno renderer yet: %s" % ", ".join(skipped))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
