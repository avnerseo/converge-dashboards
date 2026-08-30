#!/usr/bin/env python3
"""
Deterministic frame capture + encode.

Headless Chromium renders scene/scene.html, the harness seeks the scene to
each frame time and grabs a PNG, and the PNG stream is piped straight into
ffmpeg. No frame ever touches disk, so a 20s 1080x1920 render needs no
scratch space.

Determinism is enforced, not trusted:
  * every non-file:// request is aborted
  * Date / performance.now / Math.random / rAF / timers are trapped and
    neutralised, and each use is recorded
  * the run fails if the scene touched any of them
  * every frame's PNG is hashed; the hashes go into a manifest so two runs can
    be compared byte for byte
"""
import argparse
import hashlib
import json
import os
import subprocess
import tempfile
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
# Pinned deliberately. Reproducibility is guaranteed *for a given Chromium
# build*: two builds rasterise text fractionally differently. Pin it, record it,
# and a re-render years later still matches. See notes/determinism.md.
CHROME = os.environ.get(
    "CONVERGE_CHROME",
    "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell",
)

# Installed before any page script runs. Nothing here throws: a throw mid-render
# would just produce a broken frame. Instead every non-deterministic source is
# pinned to a constant and the use is recorded, and the harness fails the run
# afterwards with a list of exactly what was touched.
GUARD = r"""
(() => {
  const hits = [];
  const note = (what) => { if (hits.indexOf(what) < 0) hits.push(what); };
  const EPOCH = 0;

  const RealDate = Date;
  const FakeDate = function (...a) {
    if (!(this instanceof FakeDate)) { note('Date()'); return new RealDate(EPOCH).toString(); }
    if (a.length === 0) { note('new Date()'); return new RealDate(EPOCH); }
    return new RealDate(...a);
  };
  FakeDate.prototype = RealDate.prototype;
  FakeDate.now = () => { note('Date.now'); return EPOCH; };
  FakeDate.parse = RealDate.parse;
  FakeDate.UTC = RealDate.UTC;
  window.Date = FakeDate;

  performance.now = () => { note('performance.now'); return 0; };
  Math.random = () => { note('Math.random'); return 0.5; };
  window.requestAnimationFrame = (cb) => { note('requestAnimationFrame'); return 0; };
  window.cancelAnimationFrame = () => 0;
  const st = window.setTimeout, si = window.setInterval;
  window.setTimeout = (fn, ms, ...r) => { note('setTimeout'); return st(fn, ms, ...r); };
  window.setInterval = (fn, ms, ...r) => { note('setInterval'); return si(fn, ms, ...r); };
  window.fetch = () => { note('fetch'); return Promise.reject(new Error('network disabled')); };

  window.__determinism = () => hits;
})();
"""


def run(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("payload", help="payload JSON produced by extract_feed.py")
    ap.add_argument("--out", "-o", required=True, help="output .mp4")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--width", type=int, default=1080)
    ap.add_argument("--height", type=int, default=1920)
    ap.add_argument("--crf", type=int, default=19)
    # Frame transport. PNG is lossless but Chromium's PNG encoder costs ~340ms
    # a frame and is the entire bottleneck; JPEG q95 measures 44.4 dB PSNR
    # against the PNG reference and runs 6.5x faster. The residual is chroma
    # subsampling, which yuv420p h264 applies regardless. Benchmarks: README.
    ap.add_argument("--frame-format", choices=("jpeg", "png"), default="jpeg")
    ap.add_argument("--frame-quality", type=int, default=95,
                    help="JPEG quality for the frame transport (ignored for png)")
    ap.add_argument("--preset", default="medium")
    ap.add_argument("--scene", default=str(ROOT / "scene" / "scene.html"))
    ap.add_argument("--manifest", help="write per-frame hashes here")
    ap.add_argument("--silent-audio", action="store_true", default=True,
                    help="mux a silent AAC track (most social platforms want one)")
    ap.add_argument("--no-silent-audio", dest="silent_audio", action="store_false")
    args = ap.parse_args(argv)

    from playwright.sync_api import sync_playwright

    payload = json.loads(Path(args.payload).read_text(encoding="utf-8"))
    scene_uri = Path(args.scene).resolve().as_uri()
    out = Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    try:
        import imageio_ffmpeg
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        sys.exit("capture: need `pip install imageio-ffmpeg` "
                 "(the Playwright-bundled ffmpeg is stripped and cannot encode h264)")

    t_start = time.perf_counter()
    blocked = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROME,
            args=[
                "--force-color-profile=srgb",   # identical colour on any host
                "--font-render-hinting=none",   # hinting varies with the platform
                "--disable-lcd-text",           # subpixel AA is display-dependent
                "--disable-skia-runtime-opts",  # CPU-feature-dependent raster paths
                "--hide-scrollbars",
                # NOT --deterministic-mode: despite the name it turns on
                # begin-frame-control, so the compositor only draws when a
                # client drives frames. Playwright's screenshot path does not,
                # and every capture hangs. Determinism here comes from the
                # seek(t) contract, not from a Chromium flag.
                "--disable-dev-shm-usage",
            ],
        )
        ctx = browser.new_context(
            viewport={"width": args.width, "height": args.height},
            device_scale_factor=1,
            locale="he-IL",
            timezone_id="UTC",
            reduced_motion="reduce",
            color_scheme="dark",
        )
        ctx.add_init_script(GUARD)

        # Hard network cut: only the scene's own files on disk may load.
        def route(r):
            if r.request.url.startswith("file://"):
                r.continue_()
            else:
                blocked.append(r.request.url)
                r.abort()

        ctx.route("**/*", route)

        page = ctx.new_page()
        page.goto(scene_uri, wait_until="load")
        page.wait_for_function("document.fonts.status === 'loaded'")

        loaded = page.evaluate("[...document.fonts].map(f => f.family + ' ' + f.weight)")
        if not any("Heebo" in f for f in loaded):
            browser.close()
            sys.exit("capture: Heebo did not load — Hebrew would fall back to a "
                     "host font and the render would not be reproducible")

        duration = page.evaluate("(p) => window.SCENE.init(p)", payload)
        n_frames = int(round(duration * args.fps))
        t_setup = time.perf_counter() - t_start

        cmd = [
            ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
            "-fflags", "+bitexact", "-flags", "+bitexact",
            "-f", "image2pipe",
            "-c:v", "png" if args.frame_format == "png" else "mjpeg",
            "-framerate", str(args.fps), "-i", "-",
        ]
        if args.silent_audio:
            cmd += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                    "-c:a", "aac", "-b:a", "96k", "-shortest"]
        cmd += [
            "-c:v", "libx264", "-preset", args.preset, "-crf", str(args.crf),
            "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.0",
            "-g", str(args.fps * 2), "-threads", "4",
            # bitexact keeps the encoder version and a creation date out of the
            # container, so the same input yields the same bytes
            "-flags:v", "+bitexact", "-fflags", "+bitexact",
            "-movflags", "+faststart",
            "-r", str(args.fps), str(out),
        ]
        # ffmpeg's stderr goes to a temp file, not a pipe. A pipe deadlocks:
        # once 64K of decoder warnings fill it ffmpeg stops reading stdin, we
        # block writing the next frame, and the render hangs forever.
        errf = tempfile.TemporaryFile()
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=errf)

        hashes = []
        t_cap = time.perf_counter()
        try:
            for i in range(n_frames):
                page.evaluate("(t) => window.SCENE.seek(t)", i / args.fps)
                # No animations="disabled": scene.css already kills every
                # transition and animation with !important, and the option adds
                # a per-frame font/animation settling pass that stalls on
                # headless_shell.
                shot_kw = {"type": args.frame_format, "timeout": 20000}
                if args.frame_format == "jpeg":
                    shot_kw["quality"] = args.frame_quality
                frame = page.screenshot(**shot_kw)
                hashes.append(hashlib.sha256(frame).hexdigest())
                proc.stdin.write(frame)
                if (i + 1) % 60 == 0 or i + 1 == n_frames:
                    el = time.perf_counter() - t_cap
                    print(f"  frame {i+1}/{n_frames}  "
                          f"{el:.1f}s  ({(i+1)/el:.1f} fps)", file=sys.stderr)
        finally:
            if not proc.stdin.closed:
                proc.stdin.close()

        violations = page.evaluate("window.__determinism()")
        rc = proc.wait()
        errf.seek(0)
        err = errf.read()
        errf.close()
        t_capture = time.perf_counter() - t_cap
        browser.close()

    if rc != 0:
        sys.exit(f"capture: ffmpeg failed ({rc})\n{err.decode(errors='replace')}")
    if blocked:
        sys.exit("capture: the scene tried to reach the network — refusing the "
                 "render, it would not be reproducible:\n  " +
                 "\n  ".join(sorted(set(blocked))[:10]))
    if violations:
        sys.exit("capture: the scene used a non-deterministic API: " +
                 ", ".join(violations))

    total = time.perf_counter() - t_start
    size = out.stat().st_size
    stream_hash = hashlib.sha256("".join(hashes).encode()).hexdigest()
    file_hash = hashlib.sha256(out.read_bytes()).hexdigest()

    report = {
        "output": str(out),
        "date": payload.get("date"),
        "frames": len(hashes),
        "fps": args.fps,
        "duration_s": round(len(hashes) / args.fps, 3),
        "resolution": f"{args.width}x{args.height}",
        "frame_format": args.frame_format,
        "chromium": CHROME,
        "setup_s": round(t_setup, 2),
        "capture_s": round(t_capture, 2),
        "total_s": round(total, 2),
        "capture_fps": round(len(hashes) / t_capture, 2),
        "bytes": size,
        "mb": round(size / 1e6, 2),
        "frame_stream_sha256": stream_hash,
        "file_sha256": file_hash,
        "determinism_violations": violations,
        "blocked_requests": blocked,
    }
    if args.manifest:
        Path(args.manifest).write_text(
            json.dumps({**report, "frame_hashes": hashes}, indent=2) + "\n",
            encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(run())
