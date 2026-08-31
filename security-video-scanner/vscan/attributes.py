"""Colour and movement, measured once at indexing time.

"The white car" and "a man in a white shirt" are the two most common things an
operator asks for, and neither is answerable by an object detector, whose whole
vocabulary is `car` and `person`. Sending those questions to a language model
works, but it charges for every search - which is the wrong shape for a product
someone uses fifty times while investigating one incident.

So the attributes are measured when the footage is indexed, at a cost of about
a millisecond per detection, and stored beside the box. A search for "the white
car" then costs exactly what a search for "car" costs: nothing.
"""
from __future__ import annotations

import cv2
import numpy as np

# Hue ranges in OpenCV's 0-179 scale, with saturation and value deciding first
# whether a pixel has any colour at all.
_HUES: tuple[tuple[str, int, int], ...] = (
    ("red", 0, 8), ("orange", 9, 20), ("yellow", 21, 33), ("green", 34, 85),
    ("cyan", 86, 96), ("blue", 97, 128), ("purple", 129, 148), ("pink", 149, 165),
    ("red", 166, 179),
)

COLOURS = ("white", "black", "gray", "red", "orange", "yellow", "green",
           "cyan", "blue", "purple", "pink", "brown")

# What each label is worth describing by colour. A traffic light has a colour;
# saying so helps nobody.
COLOURED_LABELS = frozenset({
    "person", "car", "truck", "bus", "motorcycle", "bicycle", "backpack",
    "handbag", "suitcase", "umbrella", "dog", "cat", "boat", "train",
})


def dominant_colour(crop: np.ndarray, sample: int = 48) -> str | None:
    """The colour a person would name if asked what colour this thing is."""
    if crop is None or crop.size == 0 or min(crop.shape[:2]) < 4:
        return None
    small = cv2.resize(crop, (sample, sample), interpolation=cv2.INTER_AREA)
    hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
    hue, sat, val = hsv[..., 0].ravel(), hsv[..., 1].ravel(), hsv[..., 2].ravel()

    # Greys first: a low-saturation pixel has no meaningful hue.
    grey = sat < 60
    counts: dict[str, int] = {}
    counts["white"] = int(np.count_nonzero(grey & (val >= 185)))
    counts["black"] = int(np.count_nonzero(grey & (val < 65)))
    counts["gray"] = int(np.count_nonzero(grey & (val >= 65) & (val < 185)))

    coloured = ~grey
    for name, low, high in _HUES:
        mask = coloured & (hue >= low) & (hue <= high)
        counts[name] = counts.get(name, 0) + int(np.count_nonzero(mask))

    # Dark, unsaturated orange reads as brown, not orange.
    brown = coloured & (hue >= 9) & (hue <= 25) & (val < 140)
    brown_n = int(np.count_nonzero(brown))
    if brown_n:
        counts["orange"] = max(0, counts.get("orange", 0) - brown_n)
        counts["brown"] = brown_n

    best = max(counts, key=lambda k: counts[k])
    return best if counts[best] >= hue.size * 0.18 else None


def torso_colour(crop: np.ndarray) -> str | None:
    """What someone is wearing on top - the band between shoulders and waist."""
    if crop is None or crop.size == 0:
        return None
    height = crop.shape[0]
    if height < 20:
        return dominant_colour(crop)
    return dominant_colour(crop[int(height * 0.18):int(height * 0.55)])


def colour_of(label: str, crop: np.ndarray) -> str | None:
    """Colour worth storing for this detection, or None when there is none."""
    if label not in COLOURED_LABELS:
        return None
    return torso_colour(crop) if label == "person" else dominant_colour(crop)


def displacement(previous: tuple[float, float, float, float],
                 current: tuple[float, float, float, float]) -> float:
    """How far a box moved, relative to its own size.

    Relative, because a car crossing ten pixels at the far end of a car park
    has moved as much as one crossing a hundred in the foreground.
    """
    px, py, pw, ph = previous
    cx, cy, cw, ch = current
    before = (px + pw / 2, py + ph / 2)
    after = (cx + cw / 2, cy + ch / 2)
    distance = float(np.hypot(after[0] - before[0], after[1] - before[1]))
    scale = max(8.0, (pw + ph + cw + ch) / 4)
    return distance / scale
