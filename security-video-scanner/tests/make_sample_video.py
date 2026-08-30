#!/usr/bin/env python3
"""Build a small synthetic 'security camera' clip for trying vscan out.

It composites face photos you supply onto a noisy static scene, so the clip
contains real, detectable faces at known times - handy for verifying the whole
pipeline end to end without touching real footage.

    python tests/make_sample_video.py --faces alice.jpg bob.jpg --out demo.mp4

Prints the ground-truth schedule it used.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

SCENE = (640, 480)


def build(faces: list[Path], out: Path, seconds: int = 24, fps: int = 10,
          seed: int = 7) -> list[tuple[str, float, float]]:
    rng = np.random.default_rng(seed)
    backdrop = rng.integers(60, 90, size=(SCENE[1], SCENE[0], 3), dtype=np.uint8)
    backdrop = cv2.GaussianBlur(backdrop, (21, 21), 0)
    cv2.rectangle(backdrop, (40, 300), (600, 470), (70, 70, 78), -1)   # "floor"
    cv2.rectangle(backdrop, (430, 90), (600, 330), (95, 95, 105), -1)  # "doorway"

    crops = [_face_patch(f) for f in faces]

    # each face walks across the scene during its own window
    windows = [(f"face{i + 1}:{faces[i].name}", 3.0 + i * 8.0, 3.0 + i * 8.0 + 5.0)
               for i in range(len(crops))]

    writer = _open_writer(out, fps)
    for n in range(seconds * fps):
        t = n / fps
        frame = backdrop.copy()
        frame = cv2.add(frame, rng.integers(0, 8, frame.shape, dtype=np.uint8))
        for crop, (_, t0, t1) in zip(crops, windows):
            if not (t0 <= t <= t1):
                continue
            progress = (t - t0) / max(0.1, t1 - t0)
            x = int(60 + progress * 380)
            y = int(150 + 25 * np.sin(progress * 6))
            h, w = crop.shape[:2]
            frame[y:y + h, x:x + w] = crop
        cv2.putText(frame, f"CAM-01  T={t:06.2f}s", (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (220, 220, 220), 1, cv2.LINE_AA)
        writer.write(frame)
    writer.release()
    return windows


def _face_patch(path: Path, size: int = 150) -> np.ndarray:
    """Crop tightly around the face in `path` so it is big enough to detect."""
    img = cv2.imread(str(path))
    if img is None:
        raise SystemExit(f"cannot read {path}")
    try:
        from vscan.faces import FaceEngine, crop_face
        face = FaceEngine(score_threshold=0.5, min_embed_face=16).best_face_of_image(img)
        if face is not None:
            img = crop_face(img, face.box, margin=0.45)
    except Exception:                       # models not cached - use the whole image
        pass
    return cv2.resize(img, (size, size), interpolation=cv2.INTER_AREA)


def _open_writer(out: Path, fps: int):
    out.parent.mkdir(parents=True, exist_ok=True)
    for fourcc in ("mp4v", "MJPG"):
        writer = cv2.VideoWriter(str(out), cv2.VideoWriter_fourcc(*fourcc), fps, SCENE)
        if writer.isOpened():
            return writer
    raise SystemExit("OpenCV could not open a video writer")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--faces", nargs="+", required=True, type=Path)
    ap.add_argument("--out", type=Path, default=Path("demo.mp4"))
    ap.add_argument("--seconds", type=int, default=24)
    ap.add_argument("--fps", type=int, default=10)
    args = ap.parse_args()
    windows = build(args.faces, args.out, args.seconds, args.fps)
    print(f"wrote {args.out}")
    for name, t0, t1 in windows:
        print(f"  {name}: visible {t0:.1f}s - {t1:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
