"""Lazily-loaded, lock-guarded detector instances shared by request handlers.

OpenCV DNN nets are not thread-safe and SFace takes ~40 MB and a moment to
load, so the request path borrows one shared engine under a lock instead of
building a new one per call. Job threads build their own.
"""
from __future__ import annotations

import threading
from contextlib import contextmanager
from typing import Iterator

from vscan.faces import FaceEngine

_lock = threading.Lock()
_engine: FaceEngine | None = None


@contextmanager
def face_engine(min_embed_face: int = 16) -> Iterator[FaceEngine]:
    global _engine
    with _lock:
        if _engine is None:
            _engine = FaceEngine(min_embed_face=min_embed_face)
        yield _engine


def reset() -> None:
    """Test helper - drops the cached engine."""
    global _engine
    with _lock:
        _engine = None
