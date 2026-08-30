"""Face detection (YuNet) and 128-d face embeddings (SFace), both via OpenCV DNN.

Everything runs locally on CPU - no image ever leaves the machine in this path.
"""
from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from . import modelzoo
from .util import LOG

# OpenCV's published cosine threshold for SFace: >= 0.363 means "same person".
DEFAULT_MATCH_THRESHOLD = 0.363


@dataclass
class FaceDet:
    box: tuple[float, float, float, float]      # x, y, w, h in frame pixels
    score: float
    sharpness: float
    emb: np.ndarray | None
    row: np.ndarray                             # raw 15-value YuNet row


def l2norm(vec: np.ndarray) -> np.ndarray:
    vec = np.asarray(vec, dtype=np.float32).ravel()
    n = float(np.linalg.norm(vec))
    return vec / n if n > 0 else vec


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(l2norm(a), l2norm(b)))


class FaceEngine:
    """Detect faces in a frame and turn each one into a comparable vector."""

    def __init__(
        self,
        score_threshold: float = 0.6,
        nms_threshold: float = 0.3,
        top_k: int = 500,
        min_face: int = 20,
        min_embed_face: int = 24,
        allow_download: bool = True,
        embed: bool = True,
    ):
        det_path = modelzoo.get_model("face_detect", allow_download)
        self.detector = cv2.FaceDetectorYN.create(
            str(det_path), "", (320, 320), score_threshold, nms_threshold, top_k)
        self.recognizer = None
        if embed:
            emb_path = modelzoo.get_model("face_embed", allow_download)
            self.recognizer = cv2.FaceRecognizerSF.create(str(emb_path), "")
        self.min_face = min_face
        self.min_embed_face = min_embed_face
        self._size: tuple[int, int] | None = None

    def _set_size(self, frame: np.ndarray) -> None:
        h, w = frame.shape[:2]
        if self._size != (w, h):
            self.detector.setInputSize((w, h))
            self._size = (w, h)

    def detect(self, frame: np.ndarray) -> np.ndarray:
        """Return an (N, 15) array of YuNet rows (may be empty)."""
        self._set_size(frame)
        # YuNet needs a contiguous, writable buffer; ffmpeg pipe frames are read-only.
        _, faces = self.detector.detect(np.ascontiguousarray(frame))
        if faces is None:
            return np.empty((0, 15), dtype=np.float32)
        return np.asarray(faces, dtype=np.float32)

    def analyze(self, frame: np.ndarray, embed: bool = True) -> list[FaceDet]:
        out: list[FaceDet] = []
        frame = np.ascontiguousarray(frame)
        for row in self.detect(frame):
            x, y, w, h = (float(v) for v in row[:4])
            if w < self.min_face or h < self.min_face:
                continue
            crop = _safe_crop(frame, x, y, w, h)
            sharp = sharpness(crop)
            emb = None
            if embed and self.recognizer is not None and min(w, h) >= self.min_embed_face:
                emb = self.embed(frame, row)
            out.append(FaceDet((x, y, w, h), float(row[14]), sharp, emb, row))
        return out

    def embed(self, frame: np.ndarray, row: np.ndarray) -> np.ndarray | None:
        if self.recognizer is None:
            return None
        try:
            aligned = self.recognizer.alignCrop(np.ascontiguousarray(frame),
                                                np.asarray(row, dtype=np.float32))
            return l2norm(self.recognizer.feature(aligned))
        except cv2.error as exc:            # degenerate landmarks near frame edges
            LOG.debug("alignCrop failed: %s", exc)
            return None

    def best_face_of_image(self, image: np.ndarray) -> FaceDet | None:
        """Largest, sharpest face in a still - used when enrolling a person."""
        faces = [f for f in self.analyze(image) if f.emb is not None]
        if not faces:
            return None
        # Prefer a big *and* confident face: a large blurry background head
        # otherwise wins over the sharp portrait the user meant to enroll.
        return max(faces, key=lambda f: f.box[2] * f.box[3] * max(f.score, 0.01))


def _safe_crop(frame: np.ndarray, x: float, y: float, w: float, h: float,
               margin: float = 0.0) -> np.ndarray:
    fh, fw = frame.shape[:2]
    mx, my = w * margin, h * margin
    x0 = max(0, int(x - mx))
    y0 = max(0, int(y - my))
    x1 = min(fw, int(x + w + mx))
    y1 = min(fh, int(y + h + my))
    if x1 <= x0 or y1 <= y0:
        return frame[0:1, 0:1]
    return frame[y0:y1, x0:x1]


def crop_face(frame: np.ndarray, box, margin: float = 0.25) -> np.ndarray:
    return _safe_crop(frame, *box, margin=margin)


def sharpness(crop: np.ndarray) -> float:
    """Variance of the Laplacian - low means motion blur / out of focus."""
    if crop.size == 0:
        return 0.0
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY) if crop.ndim == 3 else crop
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def best_match(emb: np.ndarray, gallery: np.ndarray) -> tuple[int, float]:
    """gallery: (M, D) of L2-normalised vectors. Returns (index, cosine)."""
    if gallery.size == 0:
        return -1, -1.0
    sims = gallery @ l2norm(emb)
    idx = int(np.argmax(sims))
    return idx, float(sims[idx])
