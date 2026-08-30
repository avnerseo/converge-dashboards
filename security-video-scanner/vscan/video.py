"""ffmpeg/ffprobe plumbing: probing, sampled frame decoding, stills and clips."""
from __future__ import annotations

import datetime as dt
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import numpy as np

from .util import LOG, require_binary, start_time_from_name


@dataclass
class VideoInfo:
    path: Path
    duration: float
    fps: float
    width: int
    height: int
    codec: str
    started_at: dt.datetime | None = None

    @property
    def name(self) -> str:
        return self.path.name


def probe(path: str | Path, time_from_name: bool = True) -> VideoInfo:
    """Read stream metadata with ffprobe."""
    ffprobe = require_binary("ffprobe")
    p = Path(path).expanduser().resolve()
    if not p.exists():
        raise FileNotFoundError(p)
    out = subprocess.run(
        [ffprobe, "-v", "error", "-print_format", "json",
         "-show_streams", "-show_format", str(p)],
        capture_output=True, text=True, check=True,
    ).stdout
    meta = json.loads(out)
    vstreams = [s for s in meta.get("streams", []) if s.get("codec_type") == "video"]
    if not vstreams:
        raise ValueError(f"no video stream in {p}")
    v = vstreams[0]

    duration = float(v.get("duration") or meta.get("format", {}).get("duration") or 0.0)
    fps = _parse_rate(v.get("avg_frame_rate") or v.get("r_frame_rate") or "0/0")
    if duration <= 0 and fps > 0 and v.get("nb_frames"):
        duration = int(v["nb_frames"]) / fps

    started = None
    tags = {**meta.get("format", {}).get("tags", {}), **v.get("tags", {})}
    for key in ("creation_time", "date", "DATE"):
        if tags.get(key):
            try:
                started = dt.datetime.fromisoformat(tags[key].replace("Z", "+00:00"))
                started = started.replace(tzinfo=None)
                break
            except ValueError:
                pass
    if started is None and time_from_name:
        started = start_time_from_name(p)

    return VideoInfo(
        path=p, duration=duration, fps=fps,
        width=int(v.get("width") or 0), height=int(v.get("height") or 0),
        codec=str(v.get("codec_name") or "?"), started_at=started,
    )


def _parse_rate(rate: str) -> float:
    try:
        num, _, den = rate.partition("/")
        den_f = float(den or 1)
        return float(num) / den_f if den_f else 0.0
    except (TypeError, ValueError):
        return 0.0


def scaled_size(info: VideoInfo, max_width: int) -> tuple[int, int]:
    """Target decode size, preserving aspect ratio, both dimensions even."""
    if not info.width or not info.height:
        raise ValueError(f"unknown frame size for {info.path}")
    if max_width <= 0 or info.width <= max_width:
        w, h = info.width, info.height
    else:
        w = max_width
        h = max(2, round(info.height * max_width / info.width))
    return (w - w % 2, h - h % 2)


def iter_frames(
    info: VideoInfo,
    sample_fps: float = 2.0,
    max_width: int = 1280,
    start: float = 0.0,
    end: float | None = None,
) -> Iterator[tuple[float, np.ndarray]]:
    """Yield (timestamp_seconds, BGR frame) sampled at `sample_fps`.

    Frames are pulled straight from an ffmpeg rawvideo pipe, so any codec
    ffmpeg can open works (H.264/H.265/MJPEG DVR dumps included). Timestamps
    are accurate to about one sampling interval.
    """
    ffmpeg = require_binary("ffmpeg")
    w, h = scaled_size(info, max_width)
    cmd = [ffmpeg, "-hide_banner", "-nostdin", "-loglevel", "error"]
    if start:
        cmd += ["-ss", f"{start:.3f}"]
    cmd += ["-i", str(info.path)]
    if end is not None and end > start:
        cmd += ["-t", f"{end - start:.3f}"]
    cmd += ["-vf", f"fps={sample_fps},scale={w}:{h}", "-an", "-sn",
            "-f", "rawvideo", "-pix_fmt", "bgr24", "-"]

    LOG.debug("ffmpeg: %s", " ".join(cmd))
    frame_bytes = w * h * 3
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            bufsize=frame_bytes * 2)
    idx = 0
    try:
        assert proc.stdout is not None
        while True:
            buf = proc.stdout.read(frame_bytes)
            if len(buf) < frame_bytes:
                break
            frame = np.frombuffer(buf, dtype=np.uint8).reshape(h, w, 3)
            yield start + idx / sample_fps, frame
            idx += 1
    finally:
        if proc.stdout:
            proc.stdout.close()
        err = b""
        if proc.poll() is None:
            proc.terminate()
        try:
            err = proc.stderr.read() if proc.stderr else b""
        finally:
            if proc.stderr:
                proc.stderr.close()
            proc.wait(timeout=10)
        if proc.returncode not in (0, None) and err:
            LOG.debug("ffmpeg stderr: %s", err.decode("utf-8", "replace")[:2000])


def grab_frame(path: str | Path, t: float, max_width: int = 0) -> np.ndarray | None:
    """Decode a single full-quality frame at time `t`."""
    import cv2  # local import: keeps `vscan models` usable without opencv

    ffmpeg = require_binary("ffmpeg")
    vf = f"scale={max_width}:-2" if max_width else "null"
    cmd = [ffmpeg, "-hide_banner", "-nostdin", "-loglevel", "error",
           "-ss", f"{max(0.0, t):.3f}", "-i", str(path), "-frames:v", "1",
           "-vf", vf, "-f", "image2pipe", "-vcodec", "mjpeg", "-q:v", "2", "-"]
    res = subprocess.run(cmd, capture_output=True)
    if res.returncode != 0 or not res.stdout:
        LOG.debug("grab_frame failed at %.2fs: %s", t, res.stderr[:400])
        return None
    return cv2.imdecode(np.frombuffer(res.stdout, np.uint8), cv2.IMREAD_COLOR)


def extract_clip(path: str | Path, start: float, end: float, out: str | Path,
                 pad: float = 2.0, reencode: bool = True) -> Path:
    """Cut [start-pad, end+pad] out of the source into `out`."""
    ffmpeg = require_binary("ffmpeg")
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    s = max(0.0, start - pad)
    dur = max(0.4, (end + pad) - s)
    base = [ffmpeg, "-hide_banner", "-nostdin", "-loglevel", "error", "-y",
            "-ss", f"{s:.3f}", "-i", str(path), "-t", f"{dur:.3f}"]
    attempts = []
    if reencode:
        attempts.append(base + ["-c:v", "libx264", "-preset", "veryfast",
                                "-crf", "23", "-c:a", "aac", str(out)])
    attempts.append(base + ["-c", "copy", str(out)])
    last = None
    for cmd in attempts:
        res = subprocess.run(cmd, capture_output=True)
        if res.returncode == 0 and out.exists() and out.stat().st_size > 0:
            return out
        last = res.stderr.decode("utf-8", "replace")[:400]
    raise RuntimeError(f"clip extraction failed: {last}")
