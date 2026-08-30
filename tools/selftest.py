#!/usr/bin/env python3
"""Prove the validator catches the failures that have actually happened here.

Each case rebuilds a damaged version of today's dashboard and asserts that the
validator refuses it. Run it after touching anything under tools/.

    python3 tools/selftest.py
"""

import copy
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import extract   # noqa: E402
import validate  # noqa: E402

TODAY = dt.date(2026, 8, 30)


def errors(data):
    return validate.validate_data(copy.deepcopy(data), TODAY).errors


CASES = []


def case(name):
    def wrap(fn):
        CASES.append((name, fn))
        return fn
    return wrap


@case("file truncated mid-page (the 27.8 failure): later sections disappear")
def _(data):
    for key in ("highrisk", "sentiment", "compare", "methodology", "transparency"):
        data.pop(key, None)
    return data


@case("a methodology table is written but left empty")
def _(data):
    data["tables"]["B"]["rows"] = []
    return data


@case("a table row loses a cell")
def _(data):
    data["tables"]["A"]["rows"][0]["cells"].pop()
    return data


@case("headline count drifts from the rows behind it")
def _(data):
    data["tier1"]["cards"].pop()
    return data


@case("a tier-1 card ships without its reasoning")
def _(data):
    data["tier1"]["cards"][0]["rationale"] = ""
    return data


@case("a carried-over price is presented with no date")
def _(data):
    p = data["tier1"]["cards"][0]["price"]
    p["stale"], p["as_of"], p["note"] = True, None, None
    return data


@case("a missing price is presented with no reason")
def _(data):
    p = data["highrisk"]["cards"][0]["price"]
    p["available"], p["note"] = False, None
    return data


def main():
    base = extract.build("stocks")

    clean = errors(base)
    if clean:
        print("✗ the real dashboard fails validation before any damage:")
        for e in clean:
            print("    %s" % e)
        return 1

    print("✓ the real dashboard passes")
    failures = 0
    for name, mutate in CASES:
        found = errors(mutate(copy.deepcopy(base)))
        if found:
            print("✓ caught: %s" % name)
            print("    → %s" % found[0])
        else:
            print("✗ NOT caught: %s" % name)
            failures += 1

    print("\n%d/%d damage cases caught" % (len(CASES) - failures, len(CASES)))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
