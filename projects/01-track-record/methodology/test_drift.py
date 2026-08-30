#!/usr/bin/env python3
"""
Tests for the drift detector.

These exist because writing them found two bugs in drift.py that made it pass
for the wrong reason. A detector that reports "no drift" because its own section
regex silently returns nothing is worse than no detector: it is a green light
that means nothing, on the one check standing between a rule change and a
ledger that absorbs it in silence.

The fixtures are real commits, not synthetic HTML. 2026-08-30 really did remove
the carry-forward rule that 08-29 introduced, so it is the honest test of
whether a substantive change is caught.

  python3 test_drift.py
"""
import json, os, shutil, tempfile, sys
import drift
import resolve as meth

HERE = os.path.dirname(os.path.abspath(__file__))
V11 = os.path.join(HERE, "versions", "v11.json")
FIXTURE = "ae95024"          # 2026-08-30, the run that removed carry-forward
results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}{'  ' + detail if detail and not ok else ''}")


class without_v11:
    """Temporarily unregister v11 so 08-30 looks like an unseen run."""

    def __init__(self, strip_commits_only=False):
        self.strip = strip_commits_only

    def __enter__(self):
        self.backup = tempfile.mktemp(suffix=".json")
        shutil.copy(V11, self.backup)
        if self.strip:
            v = json.load(open(V11))
            v["published"]["commits"] = []
            json.dump(v, open(V11, "w"), ensure_ascii=False, indent=2)
        else:
            os.remove(V11)
        return self

    def __exit__(self, *a):
        shutil.copy(self.backup, V11)
        os.remove(self.backup)


html = meth.git("show", f"{FIXTURE}:index.html")

print("section extraction")
for sid in drift.SECTIONS:
    check(f"{sid} is non-empty at {FIXTURE}", len(drift.section(html, sid)) > 0)

print("\nevery rule quote is findable in the section it cites")
for p in sorted(os.listdir(os.path.join(HERE, "versions"))):
    v = json.load(open(os.path.join(HERE, "versions", p)))
    for ev in v["evidence"]:
        if ev["kind"] != "rule" or "§" not in ev["where"]:
            continue
        sid = ev["where"].split("§")[1].split(" ")[0]
        sha = ev["where"].split("@")[1]
        h = meth.git("show", f"{sha}:index.html")
        check(f"{v['version']} {sid}@{sha}",
              meth._norm(ev["quote_he"]) in drift.section(h, sid))

print("\nclean state")
check("every publishing commit claimed -> exit 0", drift.main() == 0)

print("\na real rule change is caught")
with without_v11():
    vs = meth.load_all()
    probs, _ = drift.check(FIXTURE, "2026-08-30", html, vs, vs["v10"])
    joined = " ".join(probs)
    check("exit code is 2", drift.main(FIXTURE) == 2)
    check("names the removed carry-forward rule", "נשמרות בין הרצות" in joined)
    check("reports the carry-forward state flip", "carry-forward is now OFF" in joined)

print("\nan unclaimed commit whose rules did not change is distinguished")
with without_v11(strip_commits_only=True):
    vs = meth.load_all()
    probs, _ = drift.check(FIXTURE, "2026-08-30", html, vs, vs["v11"])
    check("no problems reported", probs == [], str(probs))
    check("exit code is 1, not 2", drift.main(FIXTURE) == 1)

print("\nmarkup regression is caught")
vs = meth.load_all()
broken = html.replace('data-ticker="', 'data-sym="').replace('class="ticker ltr"', 'class="tk"')
probs, notes = drift.check(FIXTURE, "2026-08-31", broken, vs, vs["v11"])
check("unreadable tickers flagged", any("markup changed again" in p for p in probs))
probs, notes = drift.check(FIXTURE, "2026-08-31", html, vs, vs["v11"])
check("readable tickers not flagged", not any("markup" in p for p in probs))

failed = [n for n, ok, _ in results if not ok]
print(f"\n{len(results) - len(failed)}/{len(results)} passed")
sys.exit(1 if failed else 0)
