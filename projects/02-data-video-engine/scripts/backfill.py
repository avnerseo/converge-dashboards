#!/usr/bin/env python3
"""
Walks the git history of the dashboard and records what the adapter can read.

Not a way to fake a track record: a backfilled render is evidence the adapter is
robust across real historical inputs, not evidence the pipeline ran unattended.
The ledger labels them `backfill` for exactly that reason.

Failures are recorded too. A dashboard generation the adapter cannot read is the
single most useful thing to know about, and "it refused rather than guessed" is
the property worth being able to show a customer.

    python3 scripts/backfill.py            # extract + record, no rendering
    python3 scripts/backfill.py --render   # also render one video per date
"""
import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT.parent.parent
LEDGER = ROOT / "out" / "ledger.jsonl"
HISTORY = ROOT / "payload" / "history"


def git(*a):
    return subprocess.run(["git", "-C", str(REPO), *a],
                          capture_output=True, text=True).stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--render", action="store_true")
    ap.add_argument("--path", default="index.html")
    args = ap.parse_args()

    commits = git("log", "--format=%H %ad", "--date=short", "--", args.path).split("\n")
    commits = [c.split() for c in commits if c.strip()]

    ok, failed, seen = {}, [], set()
    for h, cdate in commits:
        blob = git("show", f"{h}:{args.path}")
        if not blob:
            continue
        tmp = Path("/tmp/_backfill.html")
        tmp.write_text(blob, encoding="utf-8")
        r = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "extract_feed.py"), str(tmp)],
            capture_output=True, text=True)
        if r.returncode != 0:
            failed.append((h[:8], cdate, r.stderr.strip().replace("extract_feed: ", "")))
            continue
        p = json.loads(r.stdout)
        # git log is newest-first, so the first success for a date is that day's
        # final dashboard; later (older) commits are that day's work in progress
        if p["date"] in seen:
            continue
        seen.add(p["date"])
        ok[p["date"]] = (h[:8], r.stdout, p)

    HISTORY.mkdir(parents=True, exist_ok=True)
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    print(f"readable dashboards: {len(ok)}")
    lines = []
    for date in sorted(ok):
        commit, raw, p = ok[date]
        (HISTORY / f"{date}.json").write_text(raw, encoding="utf-8")
        entry = {
            "ts": now, "status": "backfill", "date": date, "commit": commit,
            "payload_sha": hashlib.sha256(raw.encode()).hexdigest(),
            "featured": [r["ticker"] for r in p["featured"]],
            "universe": p["kpi"]["universe"],
        }
        if args.render:
            out = ROOT / "out" / f"converge-{date}.mp4"
            man = ROOT / "out" / f"converge-{date}.manifest.json"
            rr = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "capture.py"),
                 str(HISTORY / f"{date}.json"), "--out", str(out), "--manifest", str(man)],
                capture_output=True, text=True)
            if rr.returncode == 0:
                m = json.loads(man.read_text())
                entry.update(rendered=True, file_sha256=m["file_sha256"],
                             frames=m["frames"], mb=m["mb"], render_s=m["total_s"])
                out.unlink(missing_ok=True)
            else:
                entry.update(rendered=False, error=rr.stderr.strip()[-300:])
        lines.append(entry)
        print(f"  {date}  {commit}  {', '.join(entry['featured'])}"
              + (f"  [{entry.get('render_s')}s]" if args.render else ""))

    # one summary row for the generations the adapter refused, so the refusal is
    # part of the record rather than a thing that happened in a terminal once
    if failed:
        reasons = {}
        for _, _, why in failed:
            reasons[why] = reasons.get(why, 0) + 1
        lines.append({"ts": now, "status": "backfill_unreadable",
                      "commits": len(failed),
                      "oldest": failed[-1][1], "newest": failed[0][1],
                      "reasons": reasons})
        print(f"\nunreadable commits: {len(failed)}")
        for why, n in sorted(reasons.items(), key=lambda x: -x[1]):
            print(f"  {n:3}  {why}")

    with LEDGER.open("a", encoding="utf-8") as f:
        for e in lines:
            f.write(json.dumps(e, ensure_ascii=False, sort_keys=True) + "\n")
    print(f"\nledger: {LEDGER}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
