"""Is this footage searchable at all? Answer before indexing a terabyte of it.

`vscan doctor` samples a video, measures what a search would actually have to
work with - how often anything moves, how many pixels a face gets, how tall
people are in frame - and turns that into settings and an honest verdict. It is
also the fastest way to qualify a prospect's cameras before promising anything.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field, asdict
from pathlib import Path

import numpy as np

from .appearance import AppearanceEngine
from .faces import FaceEngine
from .motion import MotionGate
from .objects import ObjectEngine
from .util import LOG, fmt_timecode, human_size
from .video import VideoInfo, iter_frames, probe, scaled_size

FACE_MIN_PX = 24          # below this SFace cannot embed at all
FACE_GOOD_PX = 40         # above this matching is reliable
PERSON_MIN_PX = 64        # below this the re-id crop is mush


@dataclass
class Verdict:
    ok: bool
    headline: str
    detail: str


@dataclass
class DoctorReport:
    path: str
    duration: float
    width: int
    height: int
    fps: float
    codec: str
    started_at: str | None
    analysed_width: int
    frames_sampled: int
    active_fraction: float
    mean_brightness: float
    dark_fraction: float
    frames_with_faces: int
    face_widths: list[float] = field(default_factory=list)
    frames_with_people: int = 0
    person_heights: list[float] = field(default_factory=list)
    seconds_per_sampled_frame: float = 0.0
    verdicts: list[Verdict] = field(default_factory=list)
    recommended: dict = field(default_factory=dict)
    estimates: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        data = asdict(self)
        data["verdicts"] = [asdict(v) for v in self.verdicts]
        return data


def _pct(values: list[float], q: float) -> float:
    return float(np.percentile(values, q)) if values else 0.0


def examine(path: str | Path, samples: int = 60, width: int = 1280,
            start: float = 0.0, end: float | None = None,
            allow_download: bool = True) -> DoctorReport:
    info: VideoInfo = probe(path)
    span_end = end if end is not None else info.duration
    span = max(0.001, span_end - start)
    sample_fps = max(0.02, min(2.0, samples / span))
    analysed_w, _ = scaled_size(info, width)

    faces = FaceEngine(score_threshold=0.6, allow_download=allow_download)
    objects = ObjectEngine(conf_threshold=0.35, labels=("person",),
                           allow_download=allow_download)
    appearance = AppearanceEngine(allow_download=allow_download)
    gate = MotionGate(threshold=0.004)

    report = DoctorReport(
        path=str(info.path), duration=info.duration, width=info.width,
        height=info.height, fps=info.fps, codec=info.codec,
        started_at=info.started_at.isoformat() if info.started_at else None,
        analysed_width=analysed_w, frames_sampled=0, active_fraction=0.0,
        mean_brightness=0.0, dark_fraction=0.0, frames_with_faces=0)

    brightness: list[float] = []
    active = 0
    t0 = time.time()
    for t, frame in iter_frames(info, sample_fps, width, start, span_end):
        report.frames_sampled += 1
        gray_mean = float(frame.mean())
        brightness.append(gray_mean)
        if gate.is_active(gate.score(frame)):
            active += 1

        found = faces.analyze(frame, embed=False)
        if found:
            report.frames_with_faces += 1
            report.face_widths.extend(f.box[2] for f in found)

        people = objects.detect(frame)
        if people:
            report.frames_with_people += 1
            report.person_heights.extend(p.box[3] for p in people)

    elapsed = time.time() - t0
    if report.frames_sampled == 0:
        raise RuntimeError(f"could not decode any frame of {info.path}")

    report.active_fraction = active / report.frames_sampled
    report.mean_brightness = float(np.mean(brightness))
    report.dark_fraction = float(np.mean([b < 45 for b in brightness]))
    report.seconds_per_sampled_frame = elapsed / report.frames_sampled

    _judge(report, appearance)
    _recommend(report)
    _estimate(report)
    return report


def _judge(r: DoctorReport, appearance: AppearanceEngine) -> None:
    face_p50 = _pct(r.face_widths, 50)
    face_p90 = _pct(r.face_widths, 90)
    person_p50 = _pct(r.person_heights, 50)

    if not r.face_widths:
        r.verdicts.append(Verdict(
            False, "face search will not work on this camera",
            "no face was detected in the sample at all - the camera is probably "
            "too high or too far. Search by appearance and by object instead."))
    elif face_p90 < FACE_MIN_PX:
        r.verdicts.append(Verdict(
            False, "faces are too small to identify",
            f"faces top out around {face_p90:.0f} px wide; {FACE_MIN_PX} px is the "
            f"floor and {FACE_GOOD_PX} px is where matching gets reliable."))
    elif face_p50 < FACE_GOOD_PX:
        r.verdicts.append(Verdict(
            True, "face search will work, but only sometimes",
            f"half the faces are under {FACE_GOOD_PX} px ({face_p50:.0f} px median). "
            "Expect misses; lower --threshold to about 0.30 and enrol several "
            "reference photos."))
    else:
        r.verdicts.append(Verdict(
            True, "face search will work well",
            f"median face width {face_p50:.0f} px, comfortably above {FACE_GOOD_PX} px."))

    if not r.person_heights:
        r.verdicts.append(Verdict(
            False, "no people in the sample",
            "either nobody walks through this view, or the camera angle hides "
            "them. Check the sampled window before indexing the whole file."))
    elif person_p50 < PERSON_MIN_PX:
        r.verdicts.append(Verdict(
            False, "people are too small for appearance search",
            f"median person height {person_p50:.0f} px, under the {PERSON_MIN_PX} px "
            "the re-id model needs. Index at a larger --width if the source allows."))
    else:
        r.verdicts.append(Verdict(
            True, "appearance search will work",
            f"median person height {person_p50:.0f} px - enough for a re-id vector "
            "even when the face is not visible."))

    if r.active_fraction > 0.7:
        r.verdicts.append(Verdict(
            True, "the scene is busy",
            f"{r.active_fraction:.0%} of frames show movement, so the motion gate "
            "saves little. Expect indexing to cost close to the full rate."))
    elif r.active_fraction < 0.05:
        r.verdicts.append(Verdict(
            True, "the scene is almost always still",
            f"only {r.active_fraction:.0%} of frames move - indexing will be fast "
            "and the index small."))

    if r.dark_fraction > 0.3:
        r.verdicts.append(Verdict(
            False, "a lot of this footage is dark",
            f"{r.dark_fraction:.0%} of sampled frames are very dark. Night footage "
            "yields far fewer faces; lean on appearance and object search there."))


def _recommend(r: DoctorReport) -> None:
    face_p50 = _pct(r.face_widths, 50)
    person_p50 = _pct(r.person_heights, 50)
    faces_worth_it = bool(r.face_widths) and _pct(r.face_widths, 90) >= FACE_MIN_PX
    small_faces = faces_worth_it and face_p50 < FACE_GOOD_PX

    width = r.analysed_width
    if small_faces and r.width > r.analysed_width:
        width = min(r.width, 1920)                 # give the detector more pixels

    r.recommended = {
        "sample_fps": 2.0 if r.active_fraction > 0.2 else 1.0,
        "width": width,
        "faces": faces_worth_it,
        "objects": True,
        "appearance": bool(r.person_heights) and person_p50 >= PERSON_MIN_PX,
        "motion": 0.004 if r.active_fraction < 0.7 else 0.0,
        "face_threshold": 0.30 if small_faces else 0.363,
    }


def _estimate(r: DoctorReport) -> None:
    """Extrapolate index time and disk from what the sample actually cost."""
    per_frame = r.seconds_per_sampled_frame
    fps = r.recommended.get("sample_fps", 2.0)
    frames_per_hour = 3600 * fps
    keep_ratio = max(r.active_fraction, 0.02)
    seconds_per_hour = frames_per_hour * per_frame * (0.35 + 0.65 * keep_ratio)
    thumbs_per_hour = frames_per_hour * keep_ratio * 45_000     # ~45 KB per thumb

    r.estimates = {
        "index_seconds_per_hour": round(seconds_per_hour, 1),
        "realtime_factor": round(3600 / seconds_per_hour, 1) if seconds_per_hour else 0,
        "index_seconds_for_this_file": round(seconds_per_hour * r.duration / 3600, 1),
        "disk_bytes_per_hour": int(thumbs_per_hour),
        "disk_per_hour_human": human_size(thumbs_per_hour),
        "disk_for_this_file": human_size(thumbs_per_hour * r.duration / 3600),
    }


def render(r: DoctorReport) -> str:
    """A report an operator can read without knowing what a vector is."""
    lines = [
        f"{Path(r.path).name}",
        f"  {fmt_timecode(r.duration)}  {r.width}x{r.height}  {r.fps:.1f} fps  {r.codec}"
        + (f"  starts {r.started_at}" if r.started_at else ""),
        f"  sampled {r.frames_sampled} frames, analysed at {r.analysed_width} px wide",
        "",
        "what is in the picture",
        f"  movement           {r.active_fraction:6.0%} of sampled frames",
        f"  brightness         mean {r.mean_brightness:.0f}/255"
        + (f", {r.dark_fraction:.0%} of frames very dark" if r.dark_fraction else ""),
        f"  frames with faces  {r.frames_with_faces:4d} / {r.frames_sampled}"
        + (f"   width p50 {_pct(r.face_widths, 50):.0f} px, p90 {_pct(r.face_widths, 90):.0f} px"
           if r.face_widths else "   (none)"),
        f"  frames with people {r.frames_with_people:4d} / {r.frames_sampled}"
        + (f"   height p50 {_pct(r.person_heights, 50):.0f} px, p90 {_pct(r.person_heights, 90):.0f} px"
           if r.person_heights else "   (none)"),
        "",
        "verdict",
    ]
    for v in r.verdicts:
        lines.append(f"  [{'ok ' if v.ok else 'no '}] {v.headline}")
        lines.append(f"         {v.detail}")

    rec = r.recommended
    est = r.estimates
    lines += [
        "",
        "suggested command",
        f"  vscan index \"{r.path}\" --fps {rec['sample_fps']:g} --width {rec['width']}"
        + ("" if rec["faces"] else " --no-faces")
        + (" --objects" if rec["objects"] else "")
        + (" --appearance" if rec["appearance"] else "")
        + (f" --motion {rec['motion']:g}" if rec["motion"] != 0.004 else ""),
        f"  then search faces with --threshold {rec['face_threshold']:g}"
        if rec["faces"] else "  face search is not worth enabling on this camera",
        "",
        "what it will cost",
        f"  indexing   ~{est['index_seconds_per_hour']:.0f} s per hour of footage "
        f"({est['realtime_factor']:.1f}x realtime), "
        f"~{est['index_seconds_for_this_file']:.0f} s for this file",
        f"  disk       ~{est['disk_per_hour_human']} per hour of footage, "
        f"~{est['disk_for_this_file']} for this file",
    ]
    return "\n".join(lines)
