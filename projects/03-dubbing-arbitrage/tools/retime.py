#!/usr/bin/env python3
"""Derive realistic segment boundaries by measuring actual synthesised duration.

The first pass at ground_truth.json used estimated timings and five of six
segments overran their slot -- the script was ~95s of content in a 78s frame,
over the brief's 90s ceiling. Rather than guess again, this measures each
segment and writes boundaries that the content actually fits into.

espeak-ng is a rough proxy for a human read: it is slower than a human on long
spoken-number phrases, which is most of this fixture. So these boundaries are an
UPPER bound. Final boundaries should be re-derived from the human recording
before timing drift (rubric dimension 4) is scored against them.
"""
import json, io, subprocess, wave, tempfile, os, sys

GAP = 0.35  # inter-segment breath

def dur(text):
    f = tempfile.mktemp(suffix=".wav")
    subprocess.run(["espeak-ng","-v","he","-s","145","-w",f,text],
                   capture_output=True, check=True)
    with wave.open(f) as w: d = w.getnframes()/w.getframerate()
    os.unlink(f); return d

p = "source_clip/ground_truth.json"
d = json.load(io.open(p, encoding="utf-8"))

t = 0.0
print(f"  {'seg':>4} {'measured':>10} {'start':>8} {'end':>8}")
print("  " + "-"*34)
for s in d["segments"]:
    m = round(dur(s["text_he"]) + 0.15, 1)   # small tail
    s["start"], s["end"] = round(t, 2), round(t + m, 2)
    print(f"  {s['id']:>4} {m:>10.1f} {s['start']:>8.2f} {s['end']:>8.2f}")
    t += m + GAP

total = round(t - GAP, 2)
d["target_duration_sec"] = total
d["timing_note"] = ("Boundaries measured from espeak-ng at 145 wpm, an UPPER bound "
                    "on a human read. Re-derive from the human recording before "
                    "scoring timing drift.")
json.dump(d, io.open(p,"w",encoding="utf-8"), ensure_ascii=False, indent=2)

print(f"\n  total {total:.1f}s", end="  ")
print("OK, within the brief's 60-90s window" if 60 <= total <= 90
      else f"OUT OF RANGE -- trim further", end="\n")
sys.exit(0 if 60 <= total <= 90 else 1)
