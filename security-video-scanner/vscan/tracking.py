"""A minimal IoU tracker.

Person boxes in consecutive sampled frames almost always belong to the same
person, so linking them costs nothing and buys a lot: one appearance vector per
*track* instead of one per frame (10x less compute and storage), the best crop
of a track instead of a blurry one, and an event that already knows it is one
visit rather than forty detections.
"""
from __future__ import annotations

from dataclasses import dataclass, field


def iou(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> float:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    x0, y0 = max(ax, bx), max(ay, by)
    x1, y1 = min(ax + aw, bx + bw), min(ay + ah, by + bh)
    if x1 <= x0 or y1 <= y0:
        return 0.0
    overlap = (x1 - x0) * (y1 - y0)
    union = aw * ah + bw * bh - overlap
    return overlap / union if union > 0 else 0.0


@dataclass
class Track:
    id: int
    box: tuple[float, float, float, float]
    first_t: float
    last_t: float
    hits: int = 1
    embedded_at: float | None = None      # last time we computed an appearance vector
    best_quality: float = 0.0
    meta: dict = field(default_factory=dict)


class IoUTracker:
    """Greedy nearest-box association. Good enough at 2-4 sampled fps."""

    def __init__(self, min_iou: float = 0.25, max_gap: float = 2.5):
        self.min_iou = min_iou
        self.max_gap = max_gap
        self._tracks: dict[int, Track] = {}
        self._next_id = 1

    @property
    def tracks(self) -> dict[int, Track]:
        return self._tracks

    def update(self, t: float, boxes: list[tuple[float, float, float, float]]) -> list[Track]:
        """Assign `boxes` seen at time `t` to tracks; returns one Track per box."""
        for track_id, track in list(self._tracks.items()):
            if t - track.last_t > self.max_gap:
                del self._tracks[track_id]

        assigned: list[Track] = []
        taken: set[int] = set()
        for box in boxes:
            best_id, best_iou = None, self.min_iou
            for track_id, track in self._tracks.items():
                if track_id in taken or track.last_t >= t:
                    continue
                score = iou(box, track.box)
                if score >= best_iou:
                    best_id, best_iou = track_id, score
            if best_id is None:
                track = Track(self._next_id, box, t, t)
                self._tracks[track.id] = track
                self._next_id += 1
            else:
                track = self._tracks[best_id]
                track.box = box
                track.last_t = t
                track.hits += 1
            taken.add(track.id)
            assigned.append(track)
        return assigned
