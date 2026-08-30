"""Small shared helpers: time parsing/formatting, logging, filesystem bits."""
from __future__ import annotations

import datetime as dt
import hashlib
import logging
import os
import re
import shutil
import sys
from pathlib import Path

LOG = logging.getLogger("vscan")

_TC_RE = re.compile(r"^(?:(?P<h>\d+):)?(?:(?P<m>\d{1,2}):)?(?P<s>\d{1,2}(?:\.\d+)?)$")

# Common DVR / NVR filename stamps, e.g.
#   ch01_20260830140000.mp4 | cam3-2026-08-30_14-00-00.mkv | 20260830_140000.avi
_NAME_TS_RES = [
    re.compile(r"(?P<Y>20\d{2})[-_.]?(?P<M>\d{2})[-_.]?(?P<D>\d{2})"
               r"[-_ T]?(?P<h>\d{2})[-_.:]?(?P<m>\d{2})[-_.:]?(?P<s>\d{2})"),
    re.compile(r"(?P<Y>20\d{2})[-_.]?(?P<M>\d{2})[-_.]?(?P<D>\d{2})"
               r"[-_ T]?(?P<h>\d{2})[-_.:]?(?P<m>\d{2})()"),
]


def setup_logging(verbose: bool = False) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stderr,
    )


def parse_timecode(value: str | float | int) -> float:
    """'90' | '1:30' | '00:01:30.5' -> seconds."""
    if isinstance(value, (int, float)):
        return float(value)
    value = value.strip()
    m = _TC_RE.match(value)
    if not m:
        raise ValueError(f"bad timecode: {value!r} (use SS, MM:SS or HH:MM:SS)")
    h = int(m.group("h") or 0)
    mi = int(m.group("m") or 0)
    if m.group("h") and not m.group("m"):  # "1:30" -> mm:ss
        h, mi = 0, int(m.group("h"))
    return h * 3600 + mi * 60 + float(m.group("s"))


def fmt_timecode(seconds: float, ms: bool = False) -> str:
    seconds = max(0.0, float(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if ms:
        return f"{int(h):02d}:{int(m):02d}:{s:06.3f}"
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d}"


def parse_datetime(value: str) -> dt.datetime:
    """Accepts ISO-ish datetimes: '2026-08-30 14:00:00', '2026-08-30T14:00'."""
    v = value.strip().replace("/", "-")
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M",
                "%Y-%m-%dT%H:%M", "%Y-%m-%d"):
        try:
            return dt.datetime.strptime(v, fmt)
        except ValueError:
            continue
    try:
        return dt.datetime.fromisoformat(v)
    except ValueError as exc:
        raise ValueError(f"bad datetime: {value!r}") from exc


def start_time_from_name(path: str | Path) -> dt.datetime | None:
    """Best-effort wall-clock start time parsed out of a DVR filename."""
    name = Path(path).name
    for rx in _NAME_TS_RES:
        m = rx.search(name)
        if not m:
            continue
        try:
            return dt.datetime(
                int(m.group("Y")), int(m.group("M")), int(m.group("D")),
                int(m.group("h")), int(m.group("m")), int(m.group("s") or 0),
            )
        except (ValueError, IndexError):
            continue
    return None


def fingerprint(path: str | Path) -> str:
    """Cheap content fingerprint: size + first/last 1 MiB. Avoids hashing 40 GB."""
    p = Path(path)
    size = p.stat().st_size
    h = hashlib.sha256(str(size).encode())
    chunk = 1 << 20
    with p.open("rb") as fh:
        h.update(fh.read(chunk))
        if size > chunk * 2:
            fh.seek(-chunk, os.SEEK_END)
            h.update(fh.read(chunk))
    return h.hexdigest()[:32]


def human_size(num: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(num) < 1024.0:
            return f"{num:.0f}{unit}" if unit == "B" else f"{num:.1f}{unit}"
        num /= 1024.0
    return f"{num:.1f}PB"


def require_binary(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise RuntimeError(
            f"'{name}' not found on PATH. Install ffmpeg "
            "(apt install ffmpeg / brew install ffmpeg) and retry."
        )
    return path


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p
