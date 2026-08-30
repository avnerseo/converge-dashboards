"""Serving pixels: index thumbnails, single frames, and range-seekable video."""
from __future__ import annotations

import hashlib
import mimetypes
import os
import re
import subprocess
import threading
from functools import lru_cache
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from fastapi import HTTPException, Request, status
from fastapi.responses import Response, StreamingResponse

from vscan.db import Index

from .config import Settings

_RANGE_RE = re.compile(r"bytes=(\d*)-(\d*)")
_CHUNK = 1 << 18  # 256 KiB


@contextmanager
def open_index(settings: Settings) -> Iterator[Index]:
    """One short-lived SQLite connection per request/job - safe across threads."""
    index = Index(settings.index_dir)
    try:
        yield index
    finally:
        index.close()


def safe_index_file(settings: Settings, relative: str) -> Path:
    """Resolve a path that came from the browser against the index directory."""
    root = settings.index_dir.resolve()
    target = (root / relative).resolve()
    if target != root and root not in target.parents:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "path outside the index")
    if not target.is_file():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "no such file")
    return target


def image_response(path: Path, max_age: int = 3600) -> Response:
    data = path.read_bytes()
    media_type = mimetypes.guess_type(path.name)[0] or "image/jpeg"
    return Response(data, media_type=media_type,
                    headers={"Cache-Control": f"private, max-age={max_age}"})


def stream_file(path: Path, request: Request, media_type: str | None = None) -> Response:
    """HTTP range support, so the player can seek straight to a hit."""
    if not path.is_file():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "no such file")
    size = path.stat().st_size
    media_type = media_type or mimetypes.guess_type(path.name)[0] or "video/mp4"
    range_header = request.headers.get("range")

    start, end = 0, size - 1
    partial = False
    if range_header:
        match = _RANGE_RE.fullmatch(range_header.strip())
        if match:
            raw_start, raw_end = match.groups()
            if raw_start:
                start = int(raw_start)
                if raw_end:
                    end = min(int(raw_end), size - 1)
            elif raw_end:                       # suffix range: last N bytes
                start = max(0, size - int(raw_end))
            if start >= size or start > end:
                return Response(status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
                                headers={"Content-Range": f"bytes */{size}"})
            partial = True

    length = end - start + 1

    def body() -> Iterator[bytes]:
        with path.open("rb") as fh:
            fh.seek(start)
            remaining = length
            while remaining > 0:
                chunk = fh.read(min(_CHUNK, remaining))
                if not chunk:
                    break
                remaining -= len(chunk)
                yield chunk

    headers = {
        "Accept-Ranges": "bytes",
        "Content-Length": str(length),
        "Cache-Control": "private, max-age=0",
    }
    if partial:
        headers["Content-Range"] = f"bytes {start}-{end}/{size}"
    return StreamingResponse(
        body(), status_code=status.HTTP_206_PARTIAL_CONTENT if partial else status.HTTP_200_OK,
        media_type=media_type, headers=headers)


# ------------------------------------------------------------------ previews
_preview_locks: dict[str, threading.Lock] = {}
_preview_locks_guard = threading.Lock()
PREVIEW_MAX_SECONDS = 180
PREVIEW_CACHE_FILES = 300


def _preview_lock(key: str) -> threading.Lock:
    with _preview_locks_guard:
        return _preview_locks.setdefault(key, threading.Lock())


PREVIEW_CODECS = {
    "h264": (".mp4", "video/mp4",
             ["-c:v", "libx264", "-preset", "veryfast", "-crf", "26",
              "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k",
              "-movflags", "+faststart"]),
    "vp9": (".webm", "video/webm",
            ["-c:v", "libvpx-vp9", "-b:v", "0", "-crf", "34", "-deadline", "realtime",
             "-cpu-used", "5", "-pix_fmt", "yuv420p", "-c:a", "libopus", "-b:a", "96k"]),
    "vp8": (".webm", "video/webm",
            ["-c:v", "libvpx", "-b:v", "1M", "-deadline", "realtime",
             "-cpu-used", "5", "-pix_fmt", "yuv420p", "-c:a", "libvorbis"]),
}


@lru_cache(maxsize=1)
def preview_codec() -> tuple[str, str, tuple[str, ...]]:
    """Pick a preview codec this ffmpeg build can actually produce.

    H.264 is what every real browser plays, so it is the default; minimal
    ffmpeg builds ship without libx264, and VSCAN_PREVIEW_CODEC can pin the
    choice either way.
    """
    wanted = os.environ.get("VSCAN_PREVIEW_CODEC", "auto").strip().lower()
    available = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"],
                               capture_output=True, text=True).stdout
    order = [wanted] if wanted in PREVIEW_CODECS else ["h264", "vp9", "vp8"]
    encoder_of = {"h264": "libx264", "vp9": "libvpx-vp9", "vp8": "libvpx"}
    for name in order:
        if f" {encoder_of[name]} " in available:
            suffix, media_type, args = PREVIEW_CODECS[name]
            return suffix, media_type, tuple(args)
    raise RuntimeError(
        "this ffmpeg build has no libx264, libvpx-vp9 or libvpx encoder, so "
        "recordings cannot be transcoded for browser playback")


def ensure_preview(settings: Settings, source: Path, start: float, duration: float,
                   width: int = 1280) -> tuple[Path, str]:
    """Transcode one window of a recording so a browser can play it.

    DVRs write whatever their chipset likes - MPEG-4 part 2, H.265, MJPEG - and
    browsers refuse most of it. Rather than hand the raw file to the player and
    hope, the moments an operator actually opens are transcoded once and cached.
    """
    start = max(0.0, float(start))
    duration = max(1.0, min(float(duration), PREVIEW_MAX_SECONDS))
    suffix, media_type, args = preview_codec()
    key = f"{source}|{start:.1f}|{duration:.1f}|{width}"
    name = hashlib.sha256(key.encode()).hexdigest()[:24] + suffix
    out = settings.previews_dir / name
    with _preview_lock(name):
        if out.exists() and out.stat().st_size > 0:
            return out, media_type
        cmd = ["ffmpeg", "-hide_banner", "-nostdin", "-loglevel", "error", "-y",
               "-ss", f"{start:.3f}", "-i", str(source), "-t", f"{duration:.3f}",
               "-vf", f"scale='min({width},iw)':-2", *args, str(out)]
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0 or not out.exists() or out.stat().st_size == 0:
            out.unlink(missing_ok=True)
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                "ffmpeg could not produce a preview for this recording: "
                + result.stderr.decode("utf-8", "replace")[-300:])
    _prune_previews(settings)
    return out, media_type


def _prune_previews(settings: Settings, keep: int = PREVIEW_CACHE_FILES) -> None:
    files = sorted((f for f in settings.previews_dir.iterdir() if f.is_file()),
                   key=lambda f: f.stat().st_mtime)
    for stale in files[:-keep]:
        stale.unlink(missing_ok=True)
