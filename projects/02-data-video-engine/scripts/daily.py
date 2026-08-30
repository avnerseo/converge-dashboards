#!/usr/bin/env python3
"""
The unattended daily run.

Extracts today's payload from the dashboard, renders it, and appends one line
to out/ledger.jsonl. Safe to run repeatedly: a payload that has already been
rendered is skipped, so a cron that fires twice does not burn CPU twice.

    python3 scripts/daily.py                 # render today's dashboard
    python3 scripts/daily.py --check         # extract and record, do not render
    python3 scripts/daily.py --force         # re-render even if unchanged

Exit codes
  0  rendered, or skipped because nothing changed
  1  the run failed (and the failure is recorded in the ledger)

Videos are deliberately not archived. The render is deterministic, so the
payload plus the pinned toolchain *is* the video: 3 KB of JSON regenerates the
1.75 MB file byte for byte. Keeping payloads means a year of daily proof costs
about a megabyte instead of 640.
"""
import argparse
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "out" / "ledger.jsonl"
HISTORY = ROOT / "payload" / "history"


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_ledger():
    if not LEDGER.exists():
        return []
    return [json.loads(l) for l in LEDGER.read_text(encoding="utf-8").splitlines() if l.strip()]


def append(entry):
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")


def extract(source):
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "extract_feed.py"), str(source)],
        capture_output=True, text=True)
    if r.returncode != 0:
        return None, r.stderr.strip()
    return r.stdout, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default=str(ROOT.parent.parent / "index.html"))
    ap.add_argument("--out-dir", default=str(ROOT / "out"))
    ap.add_argument("--check", action="store_true", help="extract only, do not render")
    ap.add_argument("--force", action="store_true", help="re-render even if unchanged")
    ap.add_argument("--keep-video", action="store_true",
                    help="keep the mp4 (default: delete it, the payload regenerates it)")
    args = ap.parse_args()

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    raw, err = extract(args.source)
    if err:
        # A layout change must be loud. Recording it and failing beats shipping
        # a video built from a half-parsed dashboard.
        append({"ts": now, "status": "extract_failed", "source": str(args.source),
                "error": err})
        print(f"daily: extraction failed — {err}", file=sys.stderr)
        return 1

    payload = json.loads(raw)
    date = payload["date"]
    payload_sha = sha(raw)

    HISTORY.mkdir(parents=True, exist_ok=True)
    payload_path = HISTORY / f"{date}.json"
    payload_path.write_text(raw, encoding="utf-8")

    # a backfill row that actually rendered counts: same payload, same video
    done = {e.get("payload_sha") for e in read_ledger()
            if e.get("status") == "rendered"
            or (e.get("status") == "backfill" and e.get("rendered"))}
    if payload_sha in done and not args.force:
        print(f"daily: {date} already rendered from this payload — nothing to do")
        return 0

    if args.check:
        append({"ts": now, "status": "extracted", "date": date,
                "payload_sha": payload_sha,
                "featured": [r["ticker"] for r in payload["featured"]]})
        print(f"daily: {date} extracted ({payload_sha[:12]}), not rendered")
        return 0

    out = Path(args.out_dir) / f"converge-{date}.mp4"
    manifest = Path(args.out_dir) / f"converge-{date}.manifest.json"
    t0 = time.perf_counter()
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "capture.py"), str(payload_path),
         "--out", str(out), "--manifest", str(manifest)],
        capture_output=True, text=True)
    elapsed = round(time.perf_counter() - t0, 2)

    if r.returncode != 0:
        append({"ts": now, "status": "render_failed", "date": date,
                "payload_sha": payload_sha, "error": r.stderr.strip()[-500:]})
        print(f"daily: render failed\n{r.stderr}", file=sys.stderr)
        return 1

    m = json.loads(manifest.read_text())
    append({
        "ts": now, "status": "rendered", "date": date,
        "payload_sha": payload_sha,
        "file_sha256": m["file_sha256"],
        "frame_stream_sha256": m["frame_stream_sha256"],
        "frames": m["frames"], "duration_s": m["duration_s"], "mb": m["mb"],
        "render_s": elapsed, "chromium": Path(m["chromium"]).parent.parent.name,
        "featured": [r_["ticker"] for r_ in payload["featured"]],
    })

    if not args.keep_video:
        out.unlink(missing_ok=True)
        note = " (video discarded — regenerable from the payload)"
    else:
        note = f" -> {out}"
    print(f"daily: {date} rendered in {elapsed}s, {m['mb']} MB{note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
