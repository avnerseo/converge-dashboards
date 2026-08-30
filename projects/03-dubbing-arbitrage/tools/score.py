#!/usr/bin/env python3
"""
Score a dubbing output against the fixture — project 03.

  python3 score.py --hebrew-transcript out_he.txt          # rubric dim 1
  python3 score.py --output out_en.txt --lang en           # rubric dim 2
  python3 score.py --output out_es.txt --lang es

Dimension 1 (Hebrew ASR) needs the vendor's intermediate Hebrew transcript. If
the vendor does not expose one, say so in FINDINGS.md rather than skipping the
dimension.

Dimensions 3 (naturalness) and 4 (timing) are NOT scored here -- 3 is human
judgement and 4 needs the rendered audio. See RUBRIC.md.

Scope note: the Hebrew number normaliser below covers the number words that
appear in THIS fixture. It is not a general Hebrew number parser and will not
behave sensibly on other text.
"""
import argparse, json, re, sys, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GT = json.loads((ROOT / "source_clip" / "ground_truth.json").read_text(encoding="utf-8"))

NIQQUD = re.compile(r"[֑-ׇ]")
PUNCT = re.compile(r"[^\w\s%$₪.,]", re.UNICODE)


def norm(t):
    t = unicodedata.normalize("NFKC", t)
    t = NIQQUD.sub("", t)
    t = t.replace("״", '"').replace("׳", "'").replace("–", "-").replace("—", "-")
    t = t.replace("־", " ").replace("־", " ")   # maqaf: split spelled-out letters
    t = PUNCT.sub(" ", t)
    return re.sub(r"\s+", " ", t).strip().lower()


def wer(ref, hyp):
    r, h = norm(ref).split(), norm(hyp).split()
    d = [[0] * (len(h) + 1) for _ in range(len(r) + 1)]
    for i in range(len(r) + 1):
        d[i][0] = i
    for j in range(len(h) + 1):
        d[0][j] = j
    for i in range(1, len(r) + 1):
        for j in range(1, len(h) + 1):
            d[i][j] = min(d[i-1][j] + 1, d[i][j-1] + 1,
                          d[i-1][j-1] + (r[i-1] != h[j-1]))
    return (d[len(r)][len(h)] / len(r) if r else 0.0), len(r)


def found(needles, hay):
    hl = norm(hay)
    return any(norm(n) in hl for n in needles)


def score_hebrew(path):
    hyp = Path(path).read_text(encoding="utf-8")
    ref = " ".join(s["text_he"] for s in GT["segments"])
    rate, nwords = wer(ref, hyp)
    thr = GT["scoring"]["wer_threshold"]
    ok = rate < thr
    print(f"\n  DIMENSION 1 - Hebrew transcription")
    print("  " + "-" * 52)
    print(f"  reference words        {nwords}")
    print(f"  word error rate        {rate:.1%}   (threshold <{thr:.0%})")
    print(f"  verdict                {'PASS' if ok else 'FAIL'}")

    print(f"\n  Gender agreement")
    gender_ok = True
    for g in GT["critical_tokens"]["gender_agreement"]:
        hit = found([g["phrase"]], hyp)
        gender_ok &= hit
        print(f"    {'ok ' if hit else 'MISS'}  {g['phrase']}  ({g['gender']})")
    return ok and gender_ok


def score_output(path, lang):
    hyp = Path(path).read_text(encoding="utf-8")
    ct = GT["critical_tokens"]
    print(f"\n  DIMENSION 2 - critical token survival  [{lang}]")
    print("  " + "-" * 52)

    fails = []
    print("  tickers")
    for t in ct["tickers"]:
        hit = found(t["accept"], hyp)
        if not hit:
            fails.append(f"ticker {t['id']}")
        print(f"    {'ok ' if hit else 'FAIL'}  {t['id']:<6} (spoken: {t['spoken_he']})")

    print("  numbers")
    for nseg in ct["numbers"]:
        hit = found(nseg["accept"], hyp)
        if not hit:
            fails.append(f"number {nseg['value']}")
        trap = "  <-- SCALE TRAP" if "trap" in nseg else ""
        print(f"    {'ok ' if hit else 'FAIL'}  {nseg['value']:<16g} {nseg['kind']:<8}{trap}")
        if not hit and "trap" in nseg:
            print(f"          {nseg['trap']}")

    print()
    if fails:
        print(f"  KILL RULE TRIGGERED - {len(fails)} critical token error(s):")
        for f in fails:
            print(f"    - {f}")
        print("  This tool FAILS for this language. See RUBRIC.md.")
    else:
        print("  All 16 critical tokens survived. Dimension 2 PASS.")
    return not fails


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--hebrew-transcript")
    p.add_argument("--output")
    p.add_argument("--lang", default="en")
    a = p.parse_args()
    if not (a.hebrew_transcript or a.output):
        p.error("give --hebrew-transcript and/or --output")

    print("=" * 56)
    print("  SCORING AGAINST FROZEN RUBRIC (RUBRIC.md)")
    print("=" * 56)
    ok = True
    if a.hebrew_transcript:
        ok &= score_hebrew(a.hebrew_transcript)
    if a.output:
        ok &= score_output(a.output, a.lang)
    print(f"\n  {'PASS' if ok else 'FAIL'}\n")
    sys.exit(0 if ok else 1)
