"""Watched zones: draw a rectangle once, then ask what happened inside it.

Object detection answers "a person is here". It cannot answer "the door
opened", "the gate was left open", "the box by the wall is gone" - those are
not objects, they are changes to one part of the picture, and every camera
watches a different part.

So the operator draws the rectangle. The door, the till, the gate, the parking
bay. We then compare that patch of every indexed frame against how it usually
looks, and report the runs where it was different. On a twelve-hour recording
this reads thumbnails that were written during indexing, so it costs seconds of
local CPU and nothing else - which is the only shape that works for a question
an operator asks fifty times while investigating one incident.

Two questions, two modes:

  change  each frame against the patch's usual state (its per-pixel median),
          so a door standing open for four minutes is one four-minute event.
  motion  each frame against the frame before it, so only the moments of
          change are reported - the door swinging, not the door being open.
"""
from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Callable, Sequence

import cv2
import numpy as np

from .db import Index
from .events import Event, Hit, arrivals as first_arrivals, group_hits
from .util import LOG

MODES = ("change", "motion")
DEFAULT_SENSITIVITY = 0.15
# How different one pixel must be before it counts as changed. JPEG noise on a
# still camera sits around 4-8 grey levels; 25 is comfortably clear of it.
PIXEL_TOLERANCE = 25
PATCH = 64                    # the zone is resampled to this square
BASELINE_SAMPLES = 240        # frames the "usual state" is taken from


@dataclass
class Box:
    """A rectangle in fractions of the frame, so it survives every resolution."""
    x: float
    y: float
    w: float
    h: float

    @classmethod
    def parse(cls, value: Sequence[float] | str) -> "Box":
        if isinstance(value, str):
            parts = [p for p in value.replace(" ", "").split(",") if p]
            if len(parts) != 4:
                raise ValueError("a zone is x,y,w,h as fractions of the frame")
            value = [float(p) for p in parts]
        x, y, w, h = (float(v) for v in value)
        if w <= 0 or h <= 0:
            raise ValueError("a zone needs a positive width and height")
        # Clip to the picture rather than refuse: a rectangle dragged past the
        # edge of the frame means "up to the edge".
        x, y = max(0.0, min(1.0, x)), max(0.0, min(1.0, y))
        w, h = min(w, 1.0 - x), min(h, 1.0 - y)
        if w <= 0 or h <= 0:
            raise ValueError("that zone falls outside the picture")
        return cls(x, y, w, h)

    def as_tuple(self) -> tuple[float, float, float, float]:
        return (self.x, self.y, self.w, self.h)

    def pixels(self, width: int, height: int) -> tuple[int, int, int, int]:
        x0 = int(round(self.x * width))
        y0 = int(round(self.y * height))
        x1 = max(x0 + 1, int(round((self.x + self.w) * width)))
        y1 = max(y0 + 1, int(round((self.y + self.h) * height)))
        return x0, y0, min(x1, width), min(y1, height)


@dataclass
class ZoneScan:
    hits: list[Hit]
    frames_examined: int
    frames_missing: int
    seconds: float
    mode: str
    sensitivity: float

    @property
    def rate(self) -> float:
        return self.frames_examined / self.seconds if self.seconds > 0 else 0.0


def _patch_of(path: str, box: Box, patch: int) -> np.ndarray | None:
    """One thumbnail, cropped to the zone and reduced to a fixed square."""
    img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if img is None or img.size == 0:
        return None
    height, width = img.shape[:2]
    x0, y0, x1, y1 = box.pixels(width, height)
    crop = img[y0:y1, x0:x1]
    if crop.size == 0:
        return None
    crop = cv2.resize(crop, (patch, patch), interpolation=cv2.INTER_AREA)
    # A light blur so JPEG blocking and sensor noise do not read as change.
    return cv2.GaussianBlur(crop, (3, 3), 0)


def _load_patches(paths: Sequence[str], box: Box, patch: int,
                  workers: int) -> list[np.ndarray | None]:
    if not paths:
        return []
    workers = max(1, min(workers, 16))
    if workers == 1:
        return [_patch_of(p, box, patch) for p in paths]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        # cv2.imread drops the GIL while decoding, so threads really do help.
        return list(pool.map(lambda p: _patch_of(p, box, patch), paths))


def time_weighted_indices(times: Sequence[float],
                          samples: int = BASELINE_SAMPLES) -> np.ndarray:
    """Sample the recording evenly in time, not evenly in stored frames.

    Indexing keeps frames where something moved, so the stored frames of a
    quiet night are crowded around its handful of incidents. Counting them
    equally would make a busy minute outweigh eleven still hours and give a
    door that is almost always shut an "average" of half-open. Since nothing
    was kept between two frames precisely because nothing changed, each frame
    stands for the stretch of time until the next one - so we sample that
    stretch instead.
    """
    stamps = np.asarray(list(times), dtype=float)
    if stamps.size <= 2:
        return np.arange(stamps.size)
    targets = np.linspace(stamps[0], stamps[-1], samples)
    return np.clip(np.searchsorted(stamps, targets, side="right") - 1,
                   0, stamps.size - 1)


def baseline_of(patches: Sequence[np.ndarray], times: Sequence[float] | None = None,
                samples: int = BASELINE_SAMPLES) -> np.ndarray:
    """How this corner of the picture usually looks.

    The per-pixel median across the recording: a door that is shut for eleven
    of twelve hours has a shut door as its median, and every open moment stands
    out against it.
    """
    if times is not None:
        picked = time_weighted_indices(times, samples)
        stack = np.stack([patches[i] for i in picked])
    elif len(patches) <= samples:
        stack = np.stack(list(patches))
    else:
        stack = np.stack([patches[i] for i in
                          np.linspace(0, len(patches) - 1, samples).astype(int)])
    return np.median(stack, axis=0).astype(np.uint8)


def _changed_fraction(patch: np.ndarray, reference: np.ndarray,
                      tolerance: int) -> float:
    diff = cv2.absdiff(patch, reference)
    return float(np.count_nonzero(diff > tolerance)) / diff.size


def scan(index: Index, video_id: int, box: Box | Sequence[float] | str,
         mode: str = "change", sensitivity: float = DEFAULT_SENSITIVITY,
         start: float = 0.0, end: float | None = None,
         label: str = "zone", tolerance: int = PIXEL_TOLERANCE,
         patch: int = PATCH, workers: int = 8) -> ZoneScan:
    """Every moment the zone did not look the way it usually looks."""
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}")
    zone = box if isinstance(box, Box) else Box.parse(box)

    video = index.get_video(video_id)
    if video is None:
        raise SystemExit(f"no video {video_id} in the index")
    rows = [r for r in index.frames_for(video_id, start, end) if r["thumb"]]
    if not rows:
        raise SystemExit(
            f"{video['path']}: no stored frames to compare - index this video "
            f"with thumbnails on (they are on by default)")

    t0 = time.time()
    paths = [str(index.abs(r["thumb"])) for r in rows]
    patches = _load_patches(paths, zone, patch, workers)
    usable = [(row, p) for row, p in zip(rows, patches) if p is not None]
    missing = len(rows) - len(usable)
    if not usable:
        raise SystemExit("the stored thumbnails for this video are unreadable")

    reference = baseline_of([p for _, p in usable],
                            [float(row["t"]) for row, _ in usable])
    hits: list[Hit] = []
    previous: np.ndarray | None = None
    for row, current in usable:
        if mode == "change":
            score = _changed_fraction(current, reference, tolerance)
        else:
            score = 0.0 if previous is None else \
                _changed_fraction(current, previous, tolerance)
        previous = current
        if score >= sensitivity:
            hits.append(Hit(video_id=video_id, video_path=video["path"],
                            t=float(row["t"]), score=round(min(1.0, score), 4),
                            thumb=row["thumb"],
                            meta={"zone": label, "mode": mode,
                                  "box": list(zone.as_tuple()),
                                  "changed": round(score, 3)}))

    scan_result = ZoneScan(hits=hits, frames_examined=len(usable),
                           frames_missing=missing, seconds=time.time() - t0,
                           mode=mode, sensitivity=sensitivity)
    LOG.info("zone %r: %d of %d frames differ by >= %.0f%% (%s mode, %.0f frames/s)",
             label, len(hits), len(usable), sensitivity * 100, mode,
             scan_result.rate)
    return scan_result


def preview(index: Index, video_id: int, box: Box | Sequence[float] | str,
            patch: int = PATCH) -> dict:
    """What the zone usually looks like, and how much it varies.

    Shown before saving a zone, so an operator can tell that they framed a
    door and not a stretch of wall that never changes.
    """
    zone = box if isinstance(box, Box) else Box.parse(box)
    rows = [r for r in index.frames_for(video_id) if r["thumb"]]
    if not rows:
        return {"frames": 0}
    picked = sorted(set(int(i) for i in
                        time_weighted_indices([float(r["t"]) for r in rows])))
    sampled = [rows[i] for i in picked]
    loaded = _load_patches([str(index.abs(r["thumb"])) for r in sampled],
                           zone, patch, 8)
    keep = [(float(r["t"]), p) for r, p in zip(sampled, loaded) if p is not None]
    if not keep:
        return {"frames": 0}
    patches = [p for _, p in keep]
    reference = baseline_of(patches, [t for t, _ in keep])
    scores = [_changed_fraction(p, reference, PIXEL_TOLERANCE) for p in patches]
    return {
        "frames": len(rows),
        "sampled": len(patches),
        "median_change": round(float(np.median(scores)), 4),
        "max_change": round(float(np.max(scores)), 4),
        # Clear of this zone's everyday noise, so the first scan returns
        # neither every frame nor none of them. The 60th percentile is still
        # inside the usual state whatever happened in the footage, which a
        # mean or a maximum would not be.
        "suggested_sensitivity": round(
            float(min(0.35, max(0.08, np.percentile(scores, 60) * 3))), 3),
    }


@dataclass
class ZonePlan:
    """One zone question, resolved: which rectangle, which videos, how strict.

    It travels intact from the request that asked it to the background job
    that answers it, so a scan queued now runs exactly as it was described.
    """
    box: Box
    mode: str = "change"
    sensitivity: float = DEFAULT_SENSITIVITY
    label: str = "zone"
    video_ids: list[int] = field(default_factory=list)
    start: float = 0.0
    end: float | None = None
    gap: float = 5.0
    min_hits: int = 1
    arrivals: bool = False
    absence: float = 300.0

    @classmethod
    def from_dict(cls, data: dict) -> "ZonePlan":
        data = dict(data)
        box = data.pop("box")
        known = {f for f in cls.__dataclass_fields__ if f != "box"}
        return cls(box=Box.parse(box),
                   **{k: v for k, v in data.items() if k in known})

    def to_dict(self) -> dict:
        return {"box": list(self.box.as_tuple()), "mode": self.mode,
                "sensitivity": self.sensitivity, "label": self.label,
                "video_ids": list(self.video_ids), "start": self.start,
                "end": self.end, "gap": self.gap, "min_hits": self.min_hits,
                "arrivals": self.arrivals, "absence": self.absence}


def run(index: Index, plan: ZonePlan,
        on_progress: Callable[[float, str], None] | None = None,
        should_cancel: Callable[[], bool] | None = None
        ) -> tuple[list[Event], int]:
    """Scan every video the plan covers and hand back finished events."""
    from .search import started_at_map

    hits: list[Hit] = []
    examined = 0
    total = max(1, len(plan.video_ids))
    for i, video_id in enumerate(plan.video_ids):
        if should_cancel is not None and should_cancel():
            break
        if on_progress is not None:
            on_progress(i / total, f"{plan.label}: video {i + 1} of {total}")
        try:
            result = scan(index, int(video_id), plan.box, plan.mode,
                          plan.sensitivity, plan.start, plan.end, plan.label)
        except SystemExit as exc:
            # One video indexed without thumbnails should not sink the others.
            LOG.warning("%s", exc)
            continue
        hits.extend(result.hits)
        examined += result.frames_examined
    if on_progress is not None:
        on_progress(0.98, f"{len(hits)} of {examined} stored frames matched")

    events = group_hits(hits, plan.label, plan.gap, plan.min_hits,
                        started_at_map(index))
    if plan.arrivals:
        events = first_arrivals(events, plan.absence)
    return events, examined
