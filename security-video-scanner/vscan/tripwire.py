"""Counting lines: who crossed, when, and which way.

"When did someone enter the room" and "when did someone leave through the gate"
are the two questions every operator asks, and neither is answerable by any
amount of object detection. A detector says a person is at these pixels; it has
no idea that those pixels are a doorway, and no idea that the person passing
them at 04:12 was going in rather than out.

Direction is what makes the question answerable, and direction needs a line an
operator drew - so they draw it once. Every crossing is then read off the
tracks already stored during indexing: no decoding, no model, no cost, and the
whole of a twelve-hour recording answered in milliseconds.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Iterable, Sequence

from .db import Index
from .events import Event
from .util import LOG

DIRECTIONS = ("in", "out", "both")
Point = tuple[float, float]


@dataclass
class Line:
    """Two points in fractions of the frame, so any resolution fits.

    `flipped` swaps which side counts as "in" - the operator sees an arrow and
    presses a button, rather than being asked to think about vectors.
    """
    x1: float
    y1: float
    x2: float
    y2: float
    flipped: bool = False

    @classmethod
    def parse(cls, value: Sequence[float] | str, flipped: bool = False) -> "Line":
        if isinstance(value, str):
            parts = [p for p in value.replace(" ", "").split(",") if p]
            if len(parts) != 4:
                raise ValueError("a line is x1,y1,x2,y2 as fractions of the frame")
            value = [float(p) for p in parts]
        x1, y1, x2, y2 = (max(0.0, min(1.0, float(v))) for v in value)
        if abs(x2 - x1) < 0.01 and abs(y2 - y1) < 0.01:
            raise ValueError("that line is too short to cross")
        return cls(x1, y1, x2, y2, flipped)

    def as_tuple(self) -> tuple[float, float, float, float]:
        return (self.x1, self.y1, self.x2, self.y2)

    def side(self, point: Point) -> float:
        """Which side of the line a point is on; the sign is all that matters."""
        return ((self.x2 - self.x1) * (point[1] - self.y1)
                - (self.y2 - self.y1) * (point[0] - self.x1))

    def direction_of(self, before: Point, after: Point) -> str:
        """'in' when the crossing follows the arrow the operator was shown."""
        forward = self.side(before) < 0 <= self.side(after)
        if self.flipped:
            forward = not forward
        return "in" if forward else "out"


def _crosses(line: Line, before: Point, after: Point) -> bool:
    """Does the step from `before` to `after` actually cut the drawn segment?

    Being on opposite sides of the infinite line is not enough - someone
    walking past the far end of a doorway has not gone through it.
    """
    d1, d2 = line.side(before), line.side(after)
    if (d1 > 0) == (d2 > 0):
        return False
    # ... and the line's own endpoints must straddle the path taken.
    def side_of_path(p: Point) -> float:
        return ((after[0] - before[0]) * (p[1] - before[1])
                - (after[1] - before[1]) * (p[0] - before[0]))
    a, b = side_of_path((line.x1, line.y1)), side_of_path((line.x2, line.y2))
    return (a > 0) != (b > 0)


def analysis_size(index: Index, video_id: int) -> tuple[float, float]:
    """The pixel grid detections were measured in, to put boxes back on 0..1.

    Indexing works on a downscaled frame, so a stored box is in neither source
    pixels nor fractions. Without this a line drawn on the picture would sit
    somewhere else entirely.
    """
    video = index.get_video(video_id)
    if video is None:
        return (1.0, 1.0)
    width = float(video["width"] or 0)
    height = float(video["height"] or 0)
    analysed = 0
    try:
        analysed = int(json.loads(video["settings"] or "{}").get("max_width") or 0)
    except (json.JSONDecodeError, TypeError, ValueError):
        analysed = 0
    if not width or not height:
        return (1.0, 1.0)
    used = min(analysed, width) if analysed else width
    return (used, height * (used / width))


def foot_point(box: Sequence[float], size: tuple[float, float]) -> Point:
    """Where a thing touches the ground, in fractions of the frame.

    The bottom centre, not the middle: a doorway is crossed by feet, and a tall
    person's centre passes the line a stride before they do.
    """
    x, y, w, h = (float(v) for v in box)
    width, height = size
    return ((x + w / 2) / max(1.0, width), (y + h) / max(1.0, height))


@dataclass
class Crossing:
    video_id: int
    video_path: str
    t: float
    label: str
    direction: str
    track: int
    colour: str | None = None
    thumb: str | None = None
    box: list[float] = field(default_factory=list)


def crossings(index: Index, video_id: int, line: Line,
              labels: Sequence[str] | None = None, min_score: float = 0.4,
              start: float = 0.0, end: float | None = None) -> list[Crossing]:
    """Every time a tracked thing stepped over the line, and which way."""
    video = index.get_video(video_id)
    if video is None:
        raise SystemExit(f"no video {video_id} in the index")

    sql = ("SELECT o.*, f.thumb AS thumb FROM objects o"
           " JOIN frames f ON f.id = o.frame_id"
           " WHERE o.video_id = ? AND o.track IS NOT NULL AND o.score >= ?"
           " AND o.t >= ?")
    params: list = [video_id, min_score, start]
    if end is not None:
        sql += " AND o.t <= ?"
        params.append(end)
    if labels:
        sql += f" AND o.label IN ({','.join('?' * len(labels))})"
        params += list(labels)
    sql += " ORDER BY o.label, o.track, o.t"
    rows = list(index.conn.execute(sql, params))
    if not rows:
        return []

    size = analysis_size(index, video_id)
    out: list[Crossing] = []
    previous: dict[tuple[str, int], tuple[float, Point]] = {}
    for row in rows:
        key = (row["label"], int(row["track"]))
        point = foot_point((row["x"], row["y"], row["w"], row["h"]), size)
        seen = previous.get(key)
        previous[key] = (float(row["t"]), point)
        if seen is None:
            continue
        last_t, last_point = seen
        if not _crosses(line, last_point, point):
            continue
        out.append(Crossing(
            video_id=video_id, video_path=video["path"],
            # Halfway between the two frames: nobody stands on the threshold.
            t=round((last_t + float(row["t"])) / 2, 2),
            label=row["label"], direction=line.direction_of(last_point, point),
            track=int(row["track"]), colour=row["colour"], thumb=row["thumb"],
            box=[row["x"], row["y"], row["w"], row["h"]]))
    out.sort(key=lambda c: c.t)
    LOG.info("%d crossing(s) of the line in %s", len(out), video["path"])
    return out


def to_events(found: Iterable[Crossing], label: str,
              started_at: dict[int, object] | None = None,
              direction: str = "both") -> list[Event]:
    """One event per crossing: a person going through a door is not a range."""
    events: list[Event] = []
    for crossing in found:
        if direction != "both" and crossing.direction != direction:
            continue
        events.append(Event(
            label=label, video_id=crossing.video_id, video_path=crossing.video_path,
            start=crossing.t, end=crossing.t, hits=1, best_t=crossing.t,
            best_score=1.0, best_thumb=crossing.thumb,
            started_at=(started_at or {}).get(crossing.video_id),
            meta={"line": label, "direction": crossing.direction,
                  "label": crossing.label, "colour": crossing.colour,
                  "track": crossing.track, "box": crossing.box}))
    events.sort(key=lambda e: (e.video_path, e.start))
    return events
