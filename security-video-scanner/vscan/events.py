"""Turn per-frame hits into human-readable time ranges ("appearances")."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Iterable

from .util import fmt_timecode


@dataclass
class Hit:
    video_id: int
    video_path: str
    t: float
    score: float
    thumb: str | None = None
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class Event:
    label: str
    video_id: int
    video_path: str
    start: float
    end: float
    hits: int
    best_t: float
    best_score: float
    best_thumb: str | None = None
    started_at: dt.datetime | None = None       # wall clock of video t=0
    meta: dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> float:
        return max(0.0, self.end - self.start)

    def wall(self, t: float | None = None) -> dt.datetime | None:
        if self.started_at is None:
            return None
        return self.started_at + dt.timedelta(seconds=t if t is not None else self.start)

    def describe(self) -> str:
        w = self.wall()
        stamp = f"  [{w:%Y-%m-%d %H:%M:%S}]" if w else ""
        return (f"{Path(self.video_path).name}  "
                f"{fmt_timecode(self.start)} - {fmt_timecode(self.end)}"
                f"  ({self.duration:.1f}s, {self.hits} hits, best "
                f"{fmt_timecode(self.best_t)} @ {self.best_score:.3f}){stamp}")

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["started_at"] = self.started_at.isoformat() if self.started_at else None
        d["duration"] = round(self.duration, 3)
        d["start_tc"] = fmt_timecode(self.start)
        d["end_tc"] = fmt_timecode(self.end)
        w = self.wall()
        d["wall_start"] = w.isoformat(timespec="seconds") if w else None
        return d


def group_hits(hits: Iterable[Hit], label: str, gap: float = 5.0,
               min_hits: int = 1, started_at: dict[int, dt.datetime | None] | None = None,
               ) -> list[Event]:
    """Merge hits that are less than `gap` seconds apart into one event.

    `gap` is what turns "the same person seen in 43 consecutive frames" into a
    single line saying they were there from 00:12:03 to 00:12:24.
    """
    by_video: dict[int, list[Hit]] = {}
    for h in hits:
        by_video.setdefault(h.video_id, []).append(h)

    events: list[Event] = []
    for video_id, group in by_video.items():
        group.sort(key=lambda h: h.t)
        run: list[Hit] = []
        for h in group:
            if run and h.t - run[-1].t > gap:
                events.append(_make_event(run, label, started_at))
                run = []
            run.append(h)
        if run:
            events.append(_make_event(run, label, started_at))
    events = [e for e in events if e.hits >= min_hits]
    events.sort(key=lambda e: (e.video_path, e.start))
    return events


def _make_event(run: list[Hit], label: str,
                started_at: dict[int, dt.datetime | None] | None) -> Event:
    best = max(run, key=lambda h: h.score)
    return Event(
        label=label,
        video_id=run[0].video_id,
        video_path=run[0].video_path,
        start=run[0].t,
        end=run[-1].t,
        hits=len(run),
        best_t=best.t,
        best_score=best.score,
        best_thumb=best.thumb,
        started_at=(started_at or {}).get(run[0].video_id),
        meta=best.meta,
    )


def arrivals(events: list[Event], absence: float = 300.0) -> list[Event]:
    """Keep only the first event after `absence` seconds of not being seen.

    Answers "when did X arrive" instead of "every second X was on camera".
    """
    out: list[Event] = []
    last_end: dict[int, float] = {}
    for e in sorted(events, key=lambda e: (e.video_path, e.start)):
        prev = last_end.get(e.video_id)
        if prev is None or e.start - prev >= absence:
            out.append(e)
        last_end[e.video_id] = max(prev or 0.0, e.end)
    return out
