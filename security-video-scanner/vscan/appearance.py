"""Appearance (person re-identification) vectors.

Faces answer "who is this" but need ~24 px of face; most security cameras are
mounted too high and too wide for that most of the time. An appearance vector
describes the whole person - build, clothing, colour - so a search still works
when the face is turned away, masked or too small. It is deliberately weaker
evidence than a face match: clothes change between days, and two people in the
same uniform look alike. Treat it as "find this person in today's footage",
not as identification.
"""
from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from . import modelzoo
from .faces import l2norm

# Youtu ReID cosine similarities run higher than SFace's. 0.60 separates the
# same person in the same clothes from other people in most footage, but it is
# scene-dependent - calibrate per site with `vscan doctor`.
DEFAULT_APPEARANCE_THRESHOLD = 0.60

_INPUT_W, _INPUT_H = 128, 256
_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)


@dataclass
class Appearance:
    box: tuple[float, float, float, float]
    score: float
    sharpness: float
    emb: np.ndarray | None
    track: int = 0


class AppearanceEngine:
    """768-d appearance embeddings from a person crop (CPU, ~35 ms per crop)."""

    def __init__(self, allow_download: bool = True, min_height: int = 64,
                 min_width: int = 24):
        path = modelzoo.get_model("appearance", allow_download)
        self.net = cv2.dnn.readNet(str(path))
        self.min_height = min_height
        self.min_width = min_width

    def usable(self, box: tuple[float, float, float, float]) -> bool:
        """A crop too small or too wide to be a standing person is noise."""
        _, _, w, h = box
        return h >= self.min_height and w >= self.min_width and h > w * 0.8

    def embed(self, crop: np.ndarray) -> np.ndarray | None:
        if crop.size == 0 or crop.shape[0] < 8 or crop.shape[1] < 4:
            return None
        resized = cv2.resize(crop, (_INPUT_W, _INPUT_H), interpolation=cv2.INTER_LINEAR)
        rgb = resized[:, :, ::-1].astype(np.float32) / 255.0
        blob = cv2.dnn.blobFromImage(((rgb - _MEAN) / _STD).astype(np.float32))
        self.net.setInput(blob)
        features = self.net.forward()
        return l2norm(np.asarray(features, dtype=np.float32).reshape(-1))

    def embed_box(self, frame: np.ndarray, box: tuple[float, float, float, float],
                  margin: float = 0.02) -> np.ndarray | None:
        return self.embed(crop_person(frame, box, margin))


def crop_person(frame: np.ndarray, box, margin: float = 0.02) -> np.ndarray:
    x, y, w, h = box
    fh, fw = frame.shape[:2]
    mx, my = w * margin, h * margin
    x0, y0 = max(0, int(x - mx)), max(0, int(y - my))
    x1, y1 = min(fw, int(x + w + mx)), min(fh, int(y + h + my))
    if x1 <= x0 or y1 <= y0:
        return frame[0:0, 0:0]
    return frame[y0:y1, x0:x1]
