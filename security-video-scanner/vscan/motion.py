"""Motion gate: cheap way to skip the 95% of CCTV footage where nothing moves."""
from __future__ import annotations

import cv2
import numpy as np


class MotionGate:
    """Fraction of pixels that changed since the previous sampled frame.

    Frames are compared at a tiny resolution, so this costs microseconds and
    lets the expensive detectors run only where something actually happened.
    """

    def __init__(self, threshold: float = 0.004, pixel_delta: int = 18,
                 work_width: int = 160, warmup_hits: int = 1):
        self.threshold = threshold
        self.pixel_delta = pixel_delta
        self.work_width = work_width
        self.warmup_hits = warmup_hits
        self._prev: np.ndarray | None = None
        self._seen = 0

    def _small(self, frame: np.ndarray) -> np.ndarray:
        h, w = frame.shape[:2]
        scale = self.work_width / max(1, w)
        small = cv2.resize(frame, (self.work_width, max(1, int(h * scale))),
                           interpolation=cv2.INTER_AREA)
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        return cv2.GaussianBlur(gray, (5, 5), 0)

    def score(self, frame: np.ndarray) -> float:
        cur = self._small(frame)
        prev, self._prev = self._prev, cur
        self._seen += 1
        if prev is None:
            return 1.0                      # always keep the first frame
        diff = cv2.absdiff(cur, prev)
        moved = float(np.count_nonzero(diff > self.pixel_delta))
        return moved / float(diff.size)

    def is_active(self, score: float) -> bool:
        return self._seen <= self.warmup_hits or score >= self.threshold
