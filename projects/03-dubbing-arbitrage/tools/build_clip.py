#!/usr/bin/env python3
"""
Build the Hebrew source clip fixture — project 03.

Two modes:

  --synthetic   Render a placeholder from espeak-ng. Lets the whole harness be
                exercised end to end before a human recording exists.
                *** NOT a valid test input for the vendors. *** espeak-ng is a
                formant synthesiser; its output is not representative of human
                Hebrew speech and would fail vendor ASR for reasons that say
                nothing about real-world performance. Use it to debug the
                pipeline, never to judge a tool.

  --from-recording FILE
                Take a real human recording, verify its length, and cut it to
                the segment boundaries in ground_truth.json. This is the real
                fixture. See source_clip/RECORDING_INSTRUCTIONS.md.

Both modes also emit a timecode video track, so timing drift (rubric dimension
4) can be measured against visible segment boundaries.

Outputs land in source_clip/build/.
"""
import argparse, json, os, subprocess, sys, wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GT = ROOT / "source_clip" / "ground_truth.json"
OUT = ROOT / "source_clip" / "build"


def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"FAILED: {' '.join(str(c) for c in cmd[:6])}...\n{r.stderr[-1500:]}")
    return r


def load():
    return json.loads(GT.read_text(encoding="utf-8"))


def wav_dur(p):
    with wave.open(str(p)) as w:
        return w.getnframes() / w.getframerate()


def build_synthetic(gt):
    OUT.mkdir(parents=True, exist_ok=True)
    parts, report = [], []
    segs = gt["segments"]
    for idx, seg in enumerate(segs):
        raw = OUT / f"seg{seg['id']}_raw.wav"
        run(["espeak-ng", "-v", "he", "-s", "145", "-w", str(raw), seg["text_he"]])
        # Pad each segment out to the NEXT segment's start, so the rendered
        # boundaries land exactly where ground_truth.json says they do --
        # otherwise the inter-segment gaps vanish and drift is scored against
        # boundaries the fixture never actually had.
        nxt = segs[idx + 1]["start"] if idx + 1 < len(segs) else seg["end"]
        want = nxt - seg["start"]
        got = wav_dur(raw)
        # Pad to the segment slot so boundaries land where ground_truth says.
        padded = OUT / f"seg{seg['id']}.wav"
        if got < want:
            run([ffmpeg(), "-y", "-loglevel", "error", "-i", str(raw),
                 "-af", f"apad=whole_dur={want}", str(padded)])
        else:
            run([ffmpeg(), "-y", "-loglevel", "error", "-i", str(raw),
                 "-t", str(want), str(padded)])
        parts.append(padded)
        report.append((seg["id"], want, got, got - want))

    listing = OUT / "concat.txt"
    listing.write_text("".join(f"file '{p.name}'\n" for p in parts), encoding="utf-8")
    audio = OUT / "source_he_synthetic.wav"
    run([ffmpeg(), "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", str(listing), "-ar", "22050", "-ac", "1", str(audio)])

    print(f"\n  {'seg':>4} {'slot(s)':>9} {'spoken(s)':>10} {'headroom':>10}")
    print("  " + "-" * 38)
    for i, want, got, d in report:
        flag = "  <-- OVERRUNS SLOT" if d > 0 else ""
        print(f"  {i:>4} {want:>9.1f} {got:>10.2f} {-d:>10.2f}{flag}")
    total = wav_dur(audio)
    print(f"\n  total: {total:.2f}s (target {gt['target_duration_sec']}s)")
    if not 60 <= total <= 90:
        print("  WARNING: outside the brief's 60-90s window.")
    return audio


def build_from_recording(gt, src):
    OUT.mkdir(parents=True, exist_ok=True)
    audio = OUT / "source_he.wav"
    run([ffmpeg(), "-y", "-loglevel", "error", "-i", str(src),
         "-ar", "22050", "-ac", "1", str(audio)])
    total = wav_dur(audio)
    print(f"  recording: {total:.2f}s")
    if not 60 <= total <= 90:
        print(f"  WARNING: {total:.1f}s is outside the brief's 60-90s window.")
    expected = gt["target_duration_sec"]
    if abs(total - expected) > 8:
        print(f"  NOTE: {abs(total-expected):.1f}s from the scripted {expected}s. "
              f"Segment boundaries in ground_truth.json will need rescaling "
              f"before timing drift can be scored -- run with --rescale.")
    return audio


def build_video(gt, audio):
    """Timecode + segment-boundary video, for measuring drift (rubric dim 4).

    Frames are drawn with PIL rather than ffmpeg's drawtext: the imageio-ffmpeg
    build available here is compiled without libfreetype, so drawtext does not
    exist in it (see ../README.md on which ffmpeg builds work).
    """
    from PIL import Image, ImageDraw, ImageFont
    FPS, W, H = 10, 640, 360
    dur = wav_dur(audio)
    n = int(dur * FPS) + 1
    frames = OUT / "frames"
    frames.mkdir(exist_ok=True)
    for f in frames.glob("*.png"):
        f.unlink()

    def font(sz):
        for c in ("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
                  "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
            if os.path.exists(c):
                return ImageFont.truetype(c, sz)
        return ImageFont.load_default()

    big, small = font(64), font(18)
    bounds = [(s["start"], s["id"]) for s in gt["segments"]]

    for i in range(n):
        t = i / FPS
        img = Image.new("RGB", (W, H), (13, 27, 42))
        d = ImageDraw.Draw(img)
        # flash a bar at each segment boundary so drift is visible frame by frame
        seg = next((sid for st, sid in bounds if st <= t < st + 0.4), None)
        if seg:
            d.rectangle([0, H - 46, W, H], fill=(26, 61, 92))
            d.text((12, H - 38), f"SEGMENT {seg}", font=small, fill=(255, 255, 255))
        label = f"{t:05.1f}s"
        bb = d.textbbox((0, 0), label, font=big)
        d.text(((W - bb[2]) / 2, (H - bb[3]) / 2 - 10), label, font=big, fill=(255, 255, 255))
        d.text((12, 10), "CONVERGE FIXTURE - not for publication",
               font=small, fill=(120, 130, 140))
        img.save(frames / f"f{i:05d}.png")

    out = OUT / (audio.stem + ".mp4")
    run([ffmpeg(), "-y", "-loglevel", "error",
         "-framerate", str(FPS), "-i", str(frames / "f%05d.png"),
         "-i", str(audio),
         "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", "25",
         "-c:a", "aac", "-b:a", "128k", "-shortest", str(out)])
    for f in frames.glob("*.png"):
        f.unlink()
    frames.rmdir()
    return out


def write_transcript(gt, stem):
    """Plain transcript + SRT, the two forms vendors accept."""
    txt = OUT / f"{stem}_transcript_he.txt"
    txt.write_text("\n".join(s["text_he"] for s in gt["segments"]) + "\n", encoding="utf-8")

    def ts(x):
        h, r = divmod(x, 3600); m, s = divmod(r, 60)
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int((s%1)*1000):03d}"

    srt = OUT / f"{stem}_he.srt"
    srt.write_text("".join(
        f"{s['id']}\n{ts(s['start'])} --> {ts(s['end'])}\n{s['text_he']}\n\n"
        for s in gt["segments"]), encoding="utf-8")
    return txt, srt


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--synthetic", action="store_true")
    g.add_argument("--from-recording", metavar="FILE")
    a = p.parse_args()

    gt = load()
    print("=" * 62)
    if a.synthetic:
        print("  BUILDING SYNTHETIC PLACEHOLDER -- pipeline debug only,")
        print("  NOT a valid input for judging any vendor.")
        print("=" * 62)
        audio = build_synthetic(gt)
    else:
        print("  BUILDING FIXTURE FROM HUMAN RECORDING")
        print("=" * 62)
        audio = build_from_recording(gt, a.from_recording)

    video = build_video(gt, audio)
    txt, srt = write_transcript(gt, audio.stem)
    print(f"\n  audio      {audio.relative_to(ROOT)}")
    print(f"  video      {video.relative_to(ROOT)}  ({video.stat().st_size/1024:.0f} KB)")
    print(f"  transcript {txt.relative_to(ROOT)}")
    print(f"  subtitles  {srt.relative_to(ROOT)}")
    print()
