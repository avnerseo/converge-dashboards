#!/usr/bin/env python3
"""
Renders the same payload twice and diffs the results.

Proves the claim in notes/determinism.md rather than asserting it: identical
frame hashes, and an identical MP4 down to the byte. If a frame diverges, the
first differing frame index is printed — that is the debugging handle the whole
seek(t) design exists to provide.

    python3 checks/determinism_check.py [payload.json]
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def render(payload, out, manifest):
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "capture.py"), str(payload),
         "--out", str(out), "--manifest", str(manifest)],
        capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"render failed:\n{r.stderr}")
    return json.loads(manifest.read_text())


def main():
    payload = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "payload" / "converge.json"
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        print("render 1/2 ...")
        a = render(payload, d / "a.mp4", d / "a.json")
        print("render 2/2 ...")
        b = render(payload, d / "b.mp4", d / "b.json")

    ok = True
    if a["frames"] != b["frames"]:
        print(f"FAIL frame count {a['frames']} vs {b['frames']}")
        return 1

    diff = [i for i, (x, y) in enumerate(zip(a["frame_hashes"], b["frame_hashes"])) if x != y]
    if diff:
        ok = False
        print(f"FAIL {len(diff)}/{a['frames']} frames differ; first at index {diff[0]} "
              f"(t={diff[0]/a['fps']:.3f}s)")
    else:
        print(f"ok   all {a['frames']} frames identical")

    if a["file_sha256"] == b["file_sha256"]:
        print(f"ok   mp4 bit-identical  sha256={a['file_sha256'][:16]}...")
    else:
        ok = False
        print(f"FAIL mp4 differs\n     {a['file_sha256']}\n     {b['file_sha256']}")

    for k in ("determinism_violations", "blocked_requests"):
        if a[k] or b[k]:
            ok = False
            print(f"FAIL {k}: {a[k] or b[k]}")
        else:
            print(f"ok   no {k.replace('_', ' ')}")

    print(f"\nrender time: {a['total_s']}s / {b['total_s']}s   size: {a['mb']} MB")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
