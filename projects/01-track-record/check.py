#!/usr/bin/env python3
"""
The gate to run after every daily dashboard update.

The whole apparatus in this directory is only worth anything if it is run before
the ledger absorbs another day. This runs the pieces in the order that matters
and refuses to be quiet about what it finds.

  1. methodology/resolve.py --verify   the frozen rule sets still hash clean and
                                       every rule they quote is still in the
                                       committed HTML it cites
  2. methodology/drift.py              did today's commit publish under a rule
                                       set nobody registered?
  3. track/extract_ledger.py           rebuild the ledger; every pick stamped
  4. track/score.py                    the power gate, untouched
  5. track/store.py status             how much of the close store is filled

Exit codes:
  0  clean
  1  needs attention (an unregistered commit with unchanged rules, unstamped
     rows, or cards the extractor cannot read)
  2  the methodology changed — write the next version before scoring anything

  python3 check.py
"""
import subprocess, sys, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
STEPS = [
    ("methodology", ["resolve.py", "--verify"], "rule sets verified"),
    ("methodology", ["drift.py"], "methodology drift"),
    ("track", ["extract_ledger.py"], "ledger rebuilt"),
    ("track", ["score.py"], "scorecard"),
    ("track", ["store.py", "status"], "close store"),
]


def run(cwd, argv):
    p = subprocess.run([sys.executable, *argv], cwd=os.path.join(HERE, cwd),
                       capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


worst, notes = 0, []
for cwd, argv, label in STEPS:
    code, out = run(cwd, argv)
    tail = [l for l in out.strip().split("\n") if l.strip()]

    if argv[0] == "drift.py":
        worst = max(worst, code)
        if code == 2:
            notes.append("METHODOLOGY CHANGED — the newest registered version no "
                         "longer describes what the dashboard publishes.")
        elif code == 1:
            notes.append("An unregistered commit publishes the current rules — "
                         "add it to the newest version's commit list.")
        print(f"\n=== {label} (exit {code}) ===")
        print(out.strip())
        continue

    if argv[0] == "resolve.py" and code:
        worst = max(worst, 2)
        notes.append("A frozen rule set no longer matches its own evidence.")

    if argv[0] == "extract_ledger.py":
        for line in tail:
            if line.startswith("UNSTAMPED") or line.startswith("NOT IN THE LEDGER"):
                worst = max(worst, 1)
                notes.append(line)

    print(f"\n=== {label} (exit {code}) ===")
    keep = {"resolve.py": tail[-1:], "extract_ledger.py": tail[:4] + [
        l for l in tail if l.startswith(("UNSTAMPED", "NOT IN THE LEDGER", "  2026"))],
        "score.py": [l for l in tail if re.search(r'verdict|positions|version', l)],
        "store.py": tail[-1:]}
    for line in keep.get(argv[0], tail):
        print(line)

print("\n" + "=" * 66)
if notes:
    for n in notes:
        print("  " + n)
print("  clean" if not notes else "")
sys.exit(worst)
