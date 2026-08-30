"""Natural-language search over indexed frames, using Claude as the detector.

This is the "find anything by instruction" half of the tool: faces answer
"who", this answers "someone carrying a box", "a van parked at the gate",
"the door was left open". Frames are triaged in grids (cheap), then each
candidate is re-checked on its own full-resolution frame (accurate).

Only frames that reach this module are sent to the Claude API - the local
face/object pipeline never leaves the machine.
"""
from __future__ import annotations

import base64
import json
import os
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

import cv2
import numpy as np

from .db import Index
from .events import Hit
from .util import LOG, fmt_timecode

DEFAULT_MODEL = "claude-opus-5"
_FALLBACK_BETA = "server-side-fallback-2026-07-01"

SYSTEM_PROMPT = (
    "You are a video-surveillance analyst reviewing still frames sampled from "
    "security-camera footage. You are given a numbered grid of frames and a "
    "description of what the operator is looking for.\n"
    "Judge each numbered frame independently and strictly on what is visible. "
    "Report a frame only when the described thing is actually shown in it. "
    "If you are unsure, give it a low confidence rather than leaving it out - "
    "the operator reviews the hits, so a hedged hit is more useful than a "
    "silent miss, but an invented one is worse than both.\n"
    "Frames are low resolution and often motion-blurred; say what you can see, "
    "never guess identities of people, and never infer anything that is not in "
    "the image."
)

GRID_SCHEMA = {
    "type": "object",
    "properties": {
        "matches": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "frame": {"type": "integer",
                              "description": "the number printed on the frame"},
                    "confidence": {"type": "number",
                                   "description": "0.0-1.0 that the frame matches"},
                    "note": {"type": "string",
                             "description": "short reason, quoting what is visible"},
                },
                "required": ["frame", "confidence", "note"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["matches"],
    "additionalProperties": False,
}

SINGLE_SCHEMA = {
    "type": "object",
    "properties": {
        "match": {"type": "boolean"},
        "confidence": {"type": "number"},
        "note": {"type": "string"},
    },
    "required": ["match", "confidence", "note"],
    "additionalProperties": False,
}


@dataclass
class AskOptions:
    model: str = DEFAULT_MODEL
    grid: int = 9                 # frames per request in the triage pass
    cell_width: int = 512
    max_frames: int = 400
    min_confidence: float = 0.5
    confirm: bool = True          # second pass on full-resolution frames
    concurrency: int = 4
    effort: str = "low"           # triage is a simple visual call; confirm uses "high"
    confirm_effort: str = "high"
    max_tokens: int = 4000
    dry_run: bool = False


@dataclass
class FrameRef:
    video_id: int
    video_path: str
    t: float
    thumb: Path | None = None


@dataclass
class AskResult:
    hits: list[Hit] = field(default_factory=list)
    frames_examined: int = 0
    requests: int = 0
    refusals: int = 0


# ------------------------------------------------------------------ client
def _client():
    try:
        import anthropic
    except ImportError as exc:                    # pragma: no cover - env dependent
        raise SystemExit(
            "the 'ask' command needs the Anthropic SDK: pip install anthropic"
        ) from exc
    if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")):
        LOG.info("ANTHROPIC_API_KEY not set - falling back to an 'ant auth login' profile")
    return anthropic.Anthropic()


_use_fallbacks = True


def _create(client, **kwargs):
    """messages.create with server-side refusal fallbacks when available."""
    global _use_fallbacks
    if _use_fallbacks:
        try:
            return client.beta.messages.create(
                betas=[_FALLBACK_BETA], fallbacks="default", **kwargs)
        except Exception as exc:                  # older SDK / beta not enabled
            _use_fallbacks = False
            LOG.debug("server-side fallbacks unavailable (%s); using plain create", exc)
    return client.messages.create(**kwargs)


def _json_of(response) -> dict | None:
    if getattr(response, "stop_reason", None) == "refusal":
        details = getattr(response, "stop_details", None)
        LOG.warning("model declined this batch (%s)",
                    getattr(details, "category", "unspecified"))
        return None
    for block in response.content:
        if block.type == "text" and block.text.strip():
            try:
                return json.loads(block.text)
            except json.JSONDecodeError:
                LOG.debug("non-JSON response: %.200s", block.text)
    return None


# ------------------------------------------------------------------ images
def _encode(img: np.ndarray, quality: int = 80) -> str:
    ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, quality])
    if not ok:
        raise RuntimeError("JPEG encoding failed")
    return base64.standard_b64encode(buf.tobytes()).decode("ascii")


def _image_block(img: np.ndarray) -> dict:
    return {"type": "image",
            "source": {"type": "base64", "media_type": "image/jpeg", "data": _encode(img)}}


def _label(cell: np.ndarray, number: int, caption: str) -> np.ndarray:
    cell = cell.copy()
    cv2.rectangle(cell, (0, 0), (int(cell.shape[1] * 0.62), 30), (0, 0, 0), -1)
    cv2.putText(cell, f"#{number}  {caption}", (6, 21),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.rectangle(cell, (0, 0), (cell.shape[1] - 1, cell.shape[0] - 1), (255, 255, 255), 2)
    return cell


def build_grid(images: Sequence[np.ndarray], captions: Sequence[str],
               numbers: Sequence[int], cell_width: int = 512) -> np.ndarray:
    """Tile frames into one labelled contact sheet."""
    n = len(images)
    cols = 1 if n == 1 else (2 if n <= 4 else 3)
    rows = (n + cols - 1) // cols
    cells = []
    cell_h = 0
    for img, cap, num in zip(images, captions, numbers):
        scale = cell_width / max(1, img.shape[1])
        cell = cv2.resize(img, (cell_width, max(1, int(img.shape[0] * scale))),
                          interpolation=cv2.INTER_AREA)
        cell = _label(cell, num, cap)
        cell_h = max(cell_h, cell.shape[0])
        cells.append(cell)
    sheet = np.full((rows * cell_h, cols * cell_width, 3), 32, dtype=np.uint8)
    for i, cell in enumerate(cells):
        r, c = divmod(i, cols)
        sheet[r * cell_h:r * cell_h + cell.shape[0],
              c * cell_width:(c + 1) * cell_width] = cell
    return sheet


# -------------------------------------------------------------- frame picks
def select_frames(index: Index, video_ids: Sequence[int] | None = None,
                  start: float = 0.0, end: float | None = None,
                  min_activity: float = 0.0, max_frames: int = 400) -> list[FrameRef]:
    """Evenly spread `max_frames` picks across every frame the index kept."""
    videos = {int(v["id"]): v for v in index.videos()}
    ids = [int(i) for i in (video_ids or videos)]
    refs: list[FrameRef] = []
    for vid in ids:
        for row in index.frames_for(vid, start, end, min_activity):
            refs.append(FrameRef(vid, videos[vid]["path"], float(row["t"]),
                                 index.abs(row["thumb"])))
    refs.sort(key=lambda r: (r.video_path, r.t))
    if max_frames and len(refs) > max_frames:
        step = len(refs) / max_frames
        refs = [refs[int(i * step)] for i in range(max_frames)]
    return refs


def _load(ref: FrameRef, max_width: int = 0) -> np.ndarray | None:
    if ref.thumb and Path(ref.thumb).exists():
        img = cv2.imread(str(ref.thumb))
        if img is not None:
            return img
    from .video import grab_frame
    return grab_frame(ref.video_path, ref.t, max_width)


# ---------------------------------------------------------------- the ask
def ask(query: str, refs: Sequence[FrameRef],
        opts: AskOptions = AskOptions()) -> AskResult:
    result = AskResult(frames_examined=len(refs))
    if not refs:
        LOG.warning("no indexed frames match that filter - nothing to ask about")
        return result

    batches = [list(refs[i:i + opts.grid]) for i in range(0, len(refs), opts.grid)]
    LOG.info("asking %s about %d frames in %d grid request(s)%s",
             opts.model, len(refs), len(batches),
             " + per-hit confirmation" if opts.confirm else "")
    if opts.dry_run:
        LOG.info("dry run - no API calls made")
        return result

    client = _client()
    with ThreadPoolExecutor(max_workers=max(1, opts.concurrency)) as pool:
        batch_results = list(pool.map(
            lambda b: _ask_batch(client, query, b[1], b[0] * opts.grid, opts),
            list(enumerate(batches))))

    candidates: list[Hit] = []
    for hits, refused in batch_results:
        result.requests += 1
        result.refusals += int(refused)
        candidates.extend(hits)

    candidates = [h for h in candidates if h.score >= opts.min_confidence]
    LOG.info("triage kept %d candidate frame(s)", len(candidates))

    if opts.confirm and candidates:
        with ThreadPoolExecutor(max_workers=max(1, opts.concurrency)) as pool:
            confirmed = list(pool.map(lambda h: _confirm(client, query, h, opts),
                                      candidates))
        result.requests += len(candidates)
        candidates = [h for h in confirmed if h is not None]
        LOG.info("confirmation kept %d frame(s)", len(candidates))

    result.hits = sorted(candidates, key=lambda h: (h.video_path, h.t))
    return result


def _ask_batch(client, query: str, batch: list[FrameRef], offset: int,
               opts: AskOptions) -> tuple[list[Hit], bool]:
    images, captions, numbers, kept = [], [], [], []
    for i, ref in enumerate(batch):
        img = _load(ref)
        if img is None:
            continue
        images.append(img)
        captions.append(fmt_timecode(ref.t))
        numbers.append(offset + i)
        kept.append(ref)
    if not images:
        return [], False

    sheet = build_grid(images, captions, numbers, opts.cell_width)
    prompt = (
        f"Operator's search: {query}\n\n"
        f"The image is a grid of {len(images)} frames, each stamped with its number "
        f"(#{numbers[0]}-#{numbers[-1]}) and its timecode in the recording. "
        "List every frame that matches the search, with a confidence and a one-line "
        "reason. Return an empty list if none of them match."
    )
    try:
        resp = _create(
            client,
            model=opts.model,
            max_tokens=opts.max_tokens,
            system=SYSTEM_PROMPT,
            thinking={"type": "adaptive"},
            output_config={"effort": opts.effort,
                           "format": {"type": "json_schema", "schema": GRID_SCHEMA}},
            messages=[{"role": "user",
                       "content": [_image_block(sheet), {"type": "text", "text": prompt}]}],
        )
    except Exception as exc:
        LOG.error("grid request failed: %s", exc)
        return [], False

    data = _json_of(resp)
    if data is None:
        return [], True

    by_number = {n: ref for n, ref in zip(numbers, kept)}
    hits: list[Hit] = []
    for m in data.get("matches", []):
        ref = by_number.get(int(m.get("frame", -1)))
        if ref is None:
            continue
        hits.append(Hit(video_id=ref.video_id, video_path=ref.video_path, t=ref.t,
                        score=float(m.get("confidence", 0.0)),
                        thumb=str(ref.thumb) if ref.thumb else None,
                        meta={"note": str(m.get("note", "")), "stage": "triage"}))
    return hits, False


def _confirm(client, query: str, hit: Hit, opts: AskOptions) -> Hit | None:
    from .video import grab_frame

    img = grab_frame(hit.video_path, hit.t, 1280)
    if img is None and hit.thumb:
        img = cv2.imread(hit.thumb)
    if img is None:
        return hit
    prompt = (
        f"Operator's search: {query}\n\n"
        f"This is a single full-resolution frame at {fmt_timecode(hit.t)} of "
        f"{Path(hit.video_path).name}. Does it match the search? Answer strictly on "
        "what is visible in this frame."
    )
    try:
        resp = _create(
            client,
            model=opts.model,
            max_tokens=opts.max_tokens,
            system=SYSTEM_PROMPT,
            thinking={"type": "adaptive"},
            output_config={"effort": opts.confirm_effort,
                           "format": {"type": "json_schema", "schema": SINGLE_SCHEMA}},
            messages=[{"role": "user",
                       "content": [_image_block(img), {"type": "text", "text": prompt}]}],
        )
    except Exception as exc:
        LOG.error("confirmation request failed: %s", exc)
        return hit
    data = _json_of(resp)
    if data is None:
        return None
    if not data.get("match"):
        return None
    hit.score = float(data.get("confidence", hit.score))
    hit.meta = {**hit.meta, "note": str(data.get("note", "")), "stage": "confirmed"}
    return hit
