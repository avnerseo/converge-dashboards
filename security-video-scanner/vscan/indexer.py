"""The indexing pass: decode -> motion gate -> detect faces/objects -> store."""
from __future__ import annotations

import time
from dataclasses import dataclass, field, asdict
from pathlib import Path

import cv2
import numpy as np

from .db import Index
from .faces import FaceEngine, crop_face
from .motion import MotionGate
from .objects import ObjectEngine
from .util import LOG, fingerprint, fmt_timecode
from .video import VideoInfo, iter_frames, probe


@dataclass
class IndexOptions:
    sample_fps: float = 2.0
    max_width: int = 1280
    motion_threshold: float = 0.004
    detect_faces: bool = True
    detect_objects: bool = False
    object_labels: tuple[str, ...] = ("person",)
    object_conf: float = 0.4
    face_score: float = 0.6
    min_face: int = 20
    thumbs: bool = True
    thumb_width: int = 480
    thumb_quality: int = 72
    save_crops: bool = True
    crop_width: int = 160
    start: float = 0.0
    end: float | None = None
    allow_download: bool = True

    def as_settings(self) -> dict:
        d = asdict(self)
        d["object_labels"] = list(self.object_labels)
        return d


@dataclass
class IndexStats:
    video: str = ""
    frames_read: int = 0
    frames_kept: int = 0
    faces: int = 0
    embedded: int = 0
    objects: int = 0
    seconds: float = 0.0
    video_seconds: float = 0.0

    @property
    def speed(self) -> float:
        return self.video_seconds / self.seconds if self.seconds > 0 else 0.0


class Indexer:
    """Reusable across videos so the ONNX models load only once."""

    def __init__(self, index: Index, opts: IndexOptions):
        self.index = index
        self.opts = opts
        self.face_engine: FaceEngine | None = None
        self.object_engine: ObjectEngine | None = None
        if opts.detect_faces:
            self.face_engine = FaceEngine(
                score_threshold=opts.face_score, min_face=opts.min_face,
                allow_download=opts.allow_download)
        if opts.detect_objects:
            self.object_engine = ObjectEngine(
                conf_threshold=opts.object_conf, labels=opts.object_labels or None,
                allow_download=opts.allow_download)

    def run(self, path: str | Path, force: bool = False,
            progress: bool = True) -> IndexStats:
        opts = self.opts
        info: VideoInfo = probe(path)
        fp = fingerprint(info.path)
        existing = self.index.find_video(info.path)
        if existing and not force and existing["fingerprint"] == fp \
                and existing["frames_kept"]:
            LOG.info("%s already indexed (%d frames) - use --force to redo",
                     info.name, existing["frames_kept"])
            return IndexStats(video=str(info.path),
                              frames_kept=int(existing["frames_kept"]))

        video_id = self.index.upsert_video(info, opts.sample_fps, fp, opts.as_settings())
        self.index.clear_video_data(video_id)

        thumb_dir = self.index.thumbs / f"v{video_id}"
        crop_dir = self.index.crops / f"v{video_id}"
        thumb_dir.mkdir(parents=True, exist_ok=True)
        crop_dir.mkdir(parents=True, exist_ok=True)

        gate = MotionGate(threshold=opts.motion_threshold)
        stats = IndexStats(video=str(info.path))
        t0 = time.time()
        last_report = t0
        LOG.info("indexing %s (%s, %dx%d, %.1f fps source, sampling %.2f fps)",
                 info.name, fmt_timecode(info.duration), info.width, info.height,
                 info.fps, opts.sample_fps)

        try:
            for t, frame in iter_frames(info, opts.sample_fps, opts.max_width,
                                        opts.start, opts.end):
                stats.frames_read += 1
                activity = gate.score(frame)
                active = gate.is_active(activity)

                faces = []
                objects = []
                if active and self.face_engine is not None:
                    faces = self.face_engine.analyze(frame)
                if active and self.object_engine is not None:
                    objects = self.object_engine.detect(frame)

                if not active and not faces and not objects:
                    continue

                thumb_rel = None
                if opts.thumbs:
                    thumb_rel = self._write_thumb(thumb_dir, t, frame)
                frame_id = self.index.add_frame(video_id, t, activity, thumb_rel)
                stats.frames_kept += 1

                for f in faces:
                    crop_rel = None
                    if opts.save_crops:
                        crop_rel = self._write_crop(crop_dir, t, frame, f)
                    self.index.add_face(video_id, frame_id, t, f.box, f.score,
                                        f.sharpness, crop_rel, f.emb)
                    stats.faces += 1
                    stats.embedded += int(f.emb is not None)
                for o in objects:
                    self.index.add_object(video_id, frame_id, t, o.label, o.score, o.box)
                    stats.objects += 1

                if stats.frames_kept % 200 == 0:
                    self.index.commit()
                now = time.time()
                if progress and now - last_report > 5.0:
                    done = t - opts.start
                    total = (opts.end or info.duration) - opts.start
                    LOG.info("  %s / %s  (%.0f%%, %.1fx realtime, %d faces, %d objects)",
                             fmt_timecode(t), fmt_timecode(opts.end or info.duration),
                             100 * done / total if total else 0,
                             done / (now - t0) if now > t0 else 0,
                             stats.faces, stats.objects)
                    last_report = now
                stats.video_seconds = t - opts.start
        except KeyboardInterrupt:
            LOG.warning("interrupted - keeping what was indexed so far")
        finally:
            self.index.set_frames_kept(video_id, stats.frames_kept)
            self.index.commit()

        stats.seconds = time.time() - t0
        LOG.info("%s: %d frames read, %d kept, %d faces (%d embeddable), %d objects "
                 "in %.1fs (%.1fx realtime)", info.name, stats.frames_read,
                 stats.frames_kept, stats.faces, stats.embedded, stats.objects,
                 stats.seconds, stats.speed)
        return stats

    # -- helpers -----------------------------------------------------------
    def _write_thumb(self, out_dir: Path, t: float, frame: np.ndarray) -> str:
        img = frame
        if self.opts.thumb_width and frame.shape[1] > self.opts.thumb_width:
            scale = self.opts.thumb_width / frame.shape[1]
            img = cv2.resize(frame, (self.opts.thumb_width,
                                     max(1, int(frame.shape[0] * scale))),
                             interpolation=cv2.INTER_AREA)
        path = out_dir / f"{int(round(t * 1000)):09d}.jpg"
        cv2.imwrite(str(path), img,
                    [cv2.IMWRITE_JPEG_QUALITY, self.opts.thumb_quality])
        return self.index.rel(path)

    def _write_crop(self, out_dir: Path, t: float, frame: np.ndarray, face) -> str | None:
        crop = crop_face(frame, face.box)
        if crop.size == 0:
            return None
        if crop.shape[1] > self.opts.crop_width:
            scale = self.opts.crop_width / crop.shape[1]
            crop = cv2.resize(crop, (self.opts.crop_width,
                                     max(1, int(crop.shape[0] * scale))),
                              interpolation=cv2.INTER_AREA)
        path = out_dir / f"{int(round(t * 1000)):09d}_{int(face.box[0]):05d}.jpg"
        cv2.imwrite(str(path), crop, [cv2.IMWRITE_JPEG_QUALITY, 85])
        return self.index.rel(path)
