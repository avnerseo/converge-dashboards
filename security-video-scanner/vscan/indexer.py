"""The indexing pass: decode -> motion gate -> detect faces/objects -> store."""
from __future__ import annotations

import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Callable

import cv2
import numpy as np

from .appearance import AppearanceEngine, crop_person
from .attributes import colour_of, displacement
from .db import Index
from .faces import FaceEngine, crop_face, sharpness
from .motion import MotionGate
from .objects import ObjectEngine
from .tracking import IoUTracker, iou
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
    detect_appearance: bool = False       # person re-identification vectors
    appearance_every: float = 1.5         # seconds between vectors of one track
    min_person_height: int = 64
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
    coloured: int = 0
    appearances: int = 0
    tracks: int = 0
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
        self.appearance_engine: AppearanceEngine | None = None
        if opts.detect_appearance and not opts.detect_objects:
            # appearance vectors are cut out of person boxes, so the detector
            # they come from is not optional
            opts.detect_objects = True
            if opts.object_labels and "person" not in opts.object_labels:
                opts.object_labels = tuple(opts.object_labels) + ("person",)
        if opts.detect_faces:
            self.face_engine = FaceEngine(
                score_threshold=opts.face_score, min_face=opts.min_face,
                allow_download=opts.allow_download)
        if opts.detect_objects:
            self.object_engine = ObjectEngine(
                conf_threshold=opts.object_conf, labels=opts.object_labels or None,
                allow_download=opts.allow_download)
        if opts.detect_appearance:
            self.appearance_engine = AppearanceEngine(
                allow_download=opts.allow_download, min_height=opts.min_person_height)

    def run(self, path: str | Path, force: bool = False, progress: bool = True,
            on_progress: Callable[[float, str], None] | None = None,
            should_cancel: Callable[[], bool] | None = None) -> IndexStats:
        """Index one video.

        `on_progress(fraction, message)` is called every few seconds so a UI can
        follow along; `should_cancel()` is polled at the same rate and stops the
        pass cleanly, keeping whatever was indexed so far.
        """
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
        tracker = IoUTracker()
        # One tracker per label: a person walking past a parked car should not
        # be handed the car's track just because the boxes overlap.
        label_trackers: dict[str, IoUTracker] = {}
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
                    colour, track_id, motion = self._describe(
                        o, t, frame, label_trackers)
                    self.index.add_object(video_id, frame_id, t, o.label, o.score,
                                          o.box, colour, track_id, motion)
                    stats.objects += 1
                    stats.coloured += int(colour is not None)

                if self.appearance_engine is not None:
                    stats.appearances += self._appearances(
                        video_id, frame_id, t, frame, objects, tracker, crop_dir)
                    stats.tracks = max(stats.tracks, len(tracker.tracks))

                if stats.frames_kept % 200 == 0:
                    self.index.commit()
                now = time.time()
                if now - last_report > 2.0:
                    done = t - opts.start
                    total = (opts.end or info.duration) - opts.start
                    fraction = (done / total) if total else 0.0
                    speed = done / (now - t0) if now > t0 else 0
                    if progress:
                        LOG.info("  %s / %s  (%.0f%%, %.1fx realtime, %d faces, %d objects)",
                                 fmt_timecode(t), fmt_timecode(opts.end or info.duration),
                                 100 * fraction, speed, stats.faces, stats.objects)
                    if on_progress is not None:
                        on_progress(fraction, f"{info.name}: {fmt_timecode(t)} of "
                                              f"{fmt_timecode(opts.end or info.duration)}, "
                                              f"{stats.faces} faces")
                    if should_cancel is not None and should_cancel():
                        LOG.warning("cancelled - keeping what was indexed so far")
                        break
                    last_report = now
                stats.video_seconds = t - opts.start
        except KeyboardInterrupt:
            LOG.warning("interrupted - keeping what was indexed so far")
        finally:
            self.index.set_frames_kept(video_id, stats.frames_kept)
            self.index.commit()

        stats.seconds = time.time() - t0
        LOG.info("%s: %d frames read, %d kept, %d faces (%d embeddable), %d objects "
                 "(%d with a colour), %d appearance vectors in %.1fs (%.1fx realtime)",
                 info.name, stats.frames_read, stats.frames_kept, stats.faces,
                 stats.embedded, stats.objects, stats.coloured, stats.appearances,
                 stats.seconds, stats.speed)
        return stats

    def _describe(self, det, t: float, frame, trackers: dict[str, IoUTracker]):
        """Colour and movement for one detection, measured now so searching is free.

        Costs about a millisecond; saves an API call per search, for ever.
        """
        tracker = trackers.setdefault(det.label, IoUTracker())
        previous = None
        for existing in tracker.tracks.values():
            if iou(det.box, existing.box) >= tracker.min_iou:
                previous = existing.box
                break
        (track,) = tracker.update(t, [det.box])
        motion = displacement(previous, det.box) if previous is not None else None
        colour = colour_of(det.label, crop_person(frame, det.box, margin=0.0))
        return colour, track.id, motion

    def _appearances(self, video_id: int, frame_id: int, t: float, frame,
                     objects, tracker: IoUTracker, crop_dir: Path) -> int:
        """One appearance vector per track every `appearance_every` seconds.

        Embedding every person box in every frame would cost ~35 ms each and
        fill the index with near-duplicates; one vector per track per second
        and a half carries the same information.
        """
        engine = self.appearance_engine
        assert engine is not None
        people = [o for o in objects if o.label == "person" and engine.usable(o.box)]
        if not people:
            return 0

        written = 0
        for det, track in zip(people, tracker.update(t, [o.box for o in people])):
            if track.embedded_at is not None and \
                    t - track.embedded_at < self.opts.appearance_every:
                continue
            crop = crop_person(frame, det.box)
            emb = engine.embed(crop)
            if emb is None:
                continue
            track.embedded_at = t
            crop_rel = None
            if self.opts.save_crops:
                crop_rel = self._write_person_crop(crop_dir, t, track.id, crop)
            self.index.add_appearance(video_id, frame_id, t, track.id, det.box,
                                      det.score, sharpness(crop), crop_rel, emb)
            written += 1
        return written

    def _write_person_crop(self, out_dir: Path, t: float, track: int, crop) -> str | None:
        if crop.size == 0:
            return None
        target_w = max(64, self.opts.crop_width // 2)
        if crop.shape[1] > target_w:
            scale = target_w / crop.shape[1]
            crop = cv2.resize(crop, (target_w, max(1, int(crop.shape[0] * scale))),
                              interpolation=cv2.INTER_AREA)
        path = out_dir / f"p{track:05d}_{int(round(t * 1000)):09d}.jpg"
        cv2.imwrite(str(path), crop, [cv2.IMWRITE_JPEG_QUALITY, 85])
        return self.index.rel(path)

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
