"""Search: enrol people, find them by face or by appearance, cluster faces."""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Iterable, Sequence

import cv2
import numpy as np

from .appearance import (DEFAULT_APPEARANCE_THRESHOLD, AppearanceEngine,
                         crop_person)
from .db import Index, blob_to_emb
from .events import Hit
from .faces import DEFAULT_MATCH_THRESHOLD, FaceEngine, l2norm
from .util import LOG, fmt_timecode, parse_datetime
from .vectors import VectorSet


# ---------------------------------------------------------------- enrolment
def enroll_images(index: Index, engine: FaceEngine, name: str,
                  paths: Sequence[str | Path]) -> int:
    """Add reference faces for `name` from still images (one face each)."""
    person_id = index.get_or_create_person(name)
    added = 0
    for p in paths:
        img = cv2.imread(str(p))
        if img is None:
            LOG.warning("cannot read image %s", p)
            continue
        face = engine.best_face_of_image(img)
        if face is None or face.emb is None:
            LOG.warning("no usable face found in %s", p)
            continue
        crop_rel = _save_reference_crop(index, person_id, img, face)
        index.add_person_embedding(person_id, face.emb, f"image:{p}", crop_rel)
        added += 1
        LOG.info("enrolled face from %s (detector score %.2f)", Path(p).name, face.score)
    return added


def enroll_from_video(index: Index, engine: FaceEngine, name: str, video: str | Path,
                      times: Sequence[float], max_width: int = 0) -> int:
    """Add reference faces by pointing at moments in a video ('he is on screen at 3:12')."""
    from .video import grab_frame

    person_id = index.get_or_create_person(name)
    added = 0
    for t in times:
        frame = grab_frame(video, t, max_width)
        if frame is None:
            LOG.warning("could not decode %s at %s", video, fmt_timecode(t))
            continue
        face = engine.best_face_of_image(frame)
        if face is None or face.emb is None:
            LOG.warning("no usable face at %s", fmt_timecode(t))
            continue
        crop_rel = _save_reference_crop(index, person_id, frame, face)
        index.add_person_embedding(person_id, face.emb,
                                   f"video:{video}@{fmt_timecode(t, ms=True)}", crop_rel)
        added += 1
        LOG.info("enrolled face from %s at %s", Path(video).name, fmt_timecode(t))
    return added


def enroll_from_faces(index: Index, name: str, face_ids: Iterable[int]) -> int:
    """Promote already-indexed faces (e.g. a whole cluster) into a named person."""
    person_id = index.get_or_create_person(name)
    added = 0
    for fid in face_ids:
        row = index.conn.execute("SELECT * FROM faces WHERE id = ?", (fid,)).fetchone()
        if row is None or row["emb"] is None:
            continue
        emb = blob_to_emb(row["emb"])
        index.add_person_embedding(person_id, emb, f"face:{fid}", row["crop"])
        index.label_face(fid, person_id, 1.0, "manual")
        added += 1
    index.commit()
    return added


def _save_reference_crop(index: Index, person_id: int, img, face) -> str | None:
    from .faces import crop_face

    out_dir = index.crops / f"person{person_id}"
    out_dir.mkdir(parents=True, exist_ok=True)
    crop = crop_face(img, face.box)
    if crop.size == 0:
        return None
    n = len(list(out_dir.glob("*.jpg")))
    path = out_dir / f"ref{n:03d}.jpg"
    cv2.imwrite(str(path), crop, [cv2.IMWRITE_JPEG_QUALITY, 90])
    return index.rel(path)


# ------------------------------------------------------------------ search
def gallery_matrix(index: Index, person_id: int) -> np.ndarray:
    """Backwards-compatible alias for the face gallery."""
    return gallery_for(index, person_id, "face")


def gallery_for(index: Index, person_id: int, kind: str = "face") -> np.ndarray:
    rows = index.person_embeddings(person_id, kind)
    if not rows:
        return np.empty((0, 0), dtype=np.float32)
    return np.stack([l2norm(blob_to_emb(r["emb"])) for r in rows])


def _hits_from_matches(index: Index, table: str, matches: list[tuple[int, float]],
                       start: float, end: float | None, min_sharpness: float,
                       video_ids: Sequence[int] | None) -> list[Hit]:
    """Turn (row id, score) pairs from a vector search into events-ready hits."""
    if not matches:
        return []
    rows = index.rows_by_id(table, [m[0] for m in matches])
    wanted = set(int(v) for v in video_ids) if video_ids else None
    hits: list[Hit] = []
    for row_id, score in matches:
        row = rows.get(row_id)
        if row is None:
            continue
        if wanted is not None and int(row["video_id"]) not in wanted:
            continue
        t = float(row["t"])
        if t < start or (end is not None and t > end):
            continue
        if min_sharpness and (row["sharpness"] or 0) < min_sharpness:
            continue
        meta = {"row_id": row_id, "table": table,
                "box": [row["x"], row["y"], row["w"], row["h"]]}
        if table == "appearances":
            meta["track"] = row["track"]
        hits.append(Hit(video_id=int(row["video_id"]), video_path=row["video_path"],
                        t=t, score=score, thumb=row["crop"], meta=meta))
    hits.sort(key=lambda h: (h.video_path, h.t))
    return hits


def search_vectors(index: Index, table: str, queries: np.ndarray, threshold: float,
                   video_ids: Sequence[int] | None = None, min_sharpness: float = 0.0,
                   start: float = 0.0, end: float | None = None,
                   limit: int = 0) -> list[Hit]:
    """One matrix product against every stored vector of `table`."""
    if queries is None or queries.size == 0:
        return []
    matches = VectorSet(index, table).search(queries, threshold, limit)
    return _hits_from_matches(index, table, matches, start, end, min_sharpness,
                              video_ids)


def find_person(index: Index, name: str, threshold: float = DEFAULT_MATCH_THRESHOLD,
                video_ids: Sequence[int] | None = None, min_sharpness: float = 0.0,
                start: float = 0.0, end: float | None = None) -> list[Hit]:
    """When does this enrolled person's face appear?"""
    person = index.person_by_name(name)
    if person is None:
        raise SystemExit(f"unknown person {name!r} - enrol them first (vscan enroll)")
    gallery = gallery_for(index, int(person["id"]), "face")
    if gallery.size == 0:
        raise SystemExit(f"{name!r} has no reference faces yet")
    hits = search_vectors(index, "faces", gallery, threshold, video_ids,
                          min_sharpness, start, end)
    LOG.info("%d face detections matched %s at cosine >= %.3f", len(hits), name,
             threshold)
    return hits


def find_person_appearance(index: Index, name: str,
                           threshold: float = DEFAULT_APPEARANCE_THRESHOLD,
                           video_ids: Sequence[int] | None = None,
                           start: float = 0.0, end: float | None = None
                           ) -> list[Hit]:
    """When does someone who looks like this person appear - face or no face?"""
    person = index.person_by_name(name)
    if person is None:
        raise SystemExit(f"unknown person {name!r}")
    gallery = gallery_for(index, int(person["id"]), "appearance")
    if gallery.size == 0:
        raise SystemExit(
            f"{name!r} has no appearance references - add one with "
            f"'vscan similar --enroll \"{name}\"'")
    hits = search_vectors(index, "appearances", gallery, threshold, video_ids,
                          0.0, start, end)
    LOG.info("%d appearance detections matched %s at cosine >= %.3f", len(hits),
             name, threshold)
    return hits


def appearance_at(index: Index, video_id: int, t: float,
                  box: Sequence[float] | None = None, engine=None,
                  allow_download: bool = True) -> tuple[np.ndarray, list[float]] | None:
    """Take an appearance vector from a moment in an indexed video.

    With a box, the crop is used as given ("this person, right here"). Without
    one, the largest person already indexed near that moment is used, and
    failing that the frame's own detection.
    """
    from .video import grab_frame

    video = index.get_video(video_id)
    if video is None:
        raise SystemExit(f"no video {video_id} in the index")
    if box is None:
        row = index.conn.execute(
            "SELECT x, y, w, h FROM appearances WHERE video_id = ?"
            " ORDER BY ABS(t - ?) LIMIT 1", (video_id, t)).fetchone()
        if row is not None:
            box = [row["x"], row["y"], row["w"], row["h"]]

    frame = grab_frame(video["path"], t)          # full resolution
    if frame is None:
        LOG.warning("could not decode %s at %s", video["path"], fmt_timecode(t))
        return None

    engine = engine or AppearanceEngine(allow_download=allow_download)
    if box is None:
        from .objects import ObjectEngine
        detector = ObjectEngine(labels=("person",), allow_download=allow_download)
        people = [d for d in detector.detect(frame) if engine.usable(d.box)]
        if not people:
            LOG.warning("no person found at %s - pass an explicit box",
                        fmt_timecode(t))
            return None
        box = list(max(people, key=lambda d: d.box[2] * d.box[3]).box)

    scale = _frame_scale(index, video_id, frame)
    scaled = [float(v) * scale for v in box]
    emb = engine.embed(crop_person(frame, scaled))
    if emb is None:
        return None
    return emb, list(box)


def _frame_scale(index: Index, video_id: int, frame) -> float:
    """Indexed boxes are in analysis pixels; a fresh full-res frame is bigger."""
    video = index.get_video(video_id)
    settings = video["settings"] if video else None
    analysed_width = None
    if settings:
        try:
            analysed_width = int(json.loads(settings).get("max_width") or 0)
        except (json.JSONDecodeError, TypeError, ValueError):
            analysed_width = None
    source_width = int(video["width"] or 0) if video else 0
    if not analysed_width or not source_width:
        return 1.0
    used = min(analysed_width, source_width) or source_width
    return frame.shape[1] / used if used else 1.0


def enroll_appearance(index: Index, name: str, emb: np.ndarray, source: str,
                      crop_rel: str | None = None) -> int:
    person_id = index.get_or_create_person(name)
    index.add_person_embedding(person_id, emb, source, crop_rel, kind="appearance")
    return person_id


def find_objects(index: Index, labels: Sequence[str], min_score: float = 0.4,
                 video_ids: Sequence[int] | None = None) -> list[Hit]:
    hits: list[Hit] = []
    videos = {int(v["id"]): v for v in index.videos()}
    ids = list(video_ids) if video_ids else list(videos)
    for vid in ids:
        for row in index.objects_for(vid, labels, min_score):
            frame = index.conn.execute("SELECT thumb FROM frames WHERE id = ?",
                                       (row["frame_id"],)).fetchone()
            hits.append(Hit(video_id=vid, video_path=videos[vid]["path"],
                            t=float(row["t"]), score=float(row["score"]),
                            thumb=frame["thumb"] if frame else None,
                            meta={"label": row["label"]}))
    return hits


def started_at_map(index: Index) -> dict[int, dt.datetime | None]:
    out: dict[int, dt.datetime | None] = {}
    for v in index.videos():
        try:
            out[int(v["id"])] = parse_datetime(v["started_at"]) if v["started_at"] else None
        except ValueError:
            out[int(v["id"])] = None
    return out


# ----------------------------------------------------------- clustering
def cluster_faces(index: Index, video_ids: Sequence[int] | None = None,
                  threshold: float = 0.45, min_sharpness: float = 8.0,
                  min_size: int = 3) -> list[dict]:
    """Greedy agglomerative clustering of every embedded face in the index.

    Answers "who shows up in this footage at all" without enrolling anyone
    first: each cluster is one apparent person, ready to be named.
    """
    rows = [r for r in index.faces_with_emb(video_ids)
            if (r["sharpness"] or 0) >= min_sharpness]
    if not rows:
        return []
    # Best-quality faces first so cluster centroids start from clean examples.
    rows.sort(key=lambda r: -( (r["score"] or 0) * min((r["sharpness"] or 0) / 100.0, 3.0)
                               + (r["w"] or 0) / 100.0 ))

    centroids: list[np.ndarray] = []
    members: list[list] = []
    for r in rows:
        emb = l2norm(blob_to_emb(r["emb"]))
        if centroids:
            sims = np.stack(centroids) @ emb
            best = int(np.argmax(sims))
            if float(sims[best]) >= threshold:
                members[best].append(r)
                n = len(members[best])
                centroids[best] = l2norm(centroids[best] * (n - 1) / n + emb / n)
                continue
        centroids.append(emb)
        members.append([r])

    clusters = []
    for i, group in enumerate(members):
        if len(group) < min_size:
            continue
        group_sorted = sorted(group, key=lambda r: -(r["sharpness"] or 0))
        clusters.append({
            "id": i,
            "size": len(group),
            "face_ids": [int(r["id"]) for r in group],
            "best_face_id": int(group_sorted[0]["id"]),
            "best_crop": group_sorted[0]["crop"],
            "first_seen": {"video_id": int(group[0]["video_id"]),
                           "video": group_sorted[0]["video_path"]},
            "times": sorted({round(float(r["t"]), 1) for r in group})[:2000],
            "videos": sorted({r["video_path"] for r in group}),
        })
    clusters.sort(key=lambda c: -c["size"])
    for rank, c in enumerate(clusters):
        c["id"] = rank
    return clusters


def save_clusters(index: Index, clusters: list[dict]) -> Path:
    path = index.root / "clusters.json"
    path.write_text(json.dumps(clusters, ensure_ascii=False, indent=1), encoding="utf-8")
    return path


def load_clusters(index: Index) -> list[dict]:
    path = index.root / "clusters.json"
    if not path.exists():
        raise SystemExit("no clusters yet - run 'vscan cluster' first")
    return json.loads(path.read_text(encoding="utf-8"))
