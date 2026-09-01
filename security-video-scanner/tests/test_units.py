"""Unit tests that need neither models, network, nor ffmpeg."""
from __future__ import annotations

import datetime as dt
import json

import numpy as np
import pytest

from vscan.events import Hit, arrivals, group_hits
from vscan.motion import MotionGate
from vscan.tracking import IoUTracker, iou
from vscan.util import (fmt_timecode, parse_datetime, parse_timecode,
                        start_time_from_name)


@pytest.mark.parametrize("text,expected", [
    ("42", 42.0), ("1:30", 90.0), ("00:01:30", 90.0),
    ("01:00:00", 3600.0), ("00:00:02.5", 2.5),
])
def test_parse_timecode(text, expected):
    assert parse_timecode(text) == pytest.approx(expected)


def test_parse_timecode_rejects_garbage():
    with pytest.raises(ValueError):
        parse_timecode("half past three")


def test_fmt_timecode():
    assert fmt_timecode(3725) == "01:02:05"
    assert fmt_timecode(3725.25, ms=True) == "01:02:05.250"
    assert fmt_timecode(-5) == "00:00:00"


@pytest.mark.parametrize("name,expected", [
    ("ch01_20260830140000.mp4", dt.datetime(2026, 8, 30, 14, 0, 0)),
    ("cam3-2026-08-30_14-05-09.mkv", dt.datetime(2026, 8, 30, 14, 5, 9)),
    ("holiday.mp4", None),
])
def test_start_time_from_name(name, expected):
    assert start_time_from_name(name) == expected


def test_parse_datetime():
    assert parse_datetime("2026-08-30 14:00:00") == dt.datetime(2026, 8, 30, 14, 0)


def _hits(times, video=1, score=0.9):
    return [Hit(video, "/f/cam.mp4", t, score) for t in times]


def test_group_hits_merges_runs_and_splits_on_gap():
    events = group_hits(_hits([1, 1.5, 2, 30, 30.5]), "X", gap=5.0)
    assert [(e.start, e.end, e.hits) for e in events] == [(1, 2, 3), (30, 30.5, 2)]


def test_group_hits_min_hits_filters_singletons():
    assert group_hits(_hits([1, 40]), "X", gap=5.0, min_hits=2) == []


def test_group_hits_keeps_videos_apart():
    hits = _hits([1, 2], video=1) + _hits([1, 2], video=2)
    assert len(group_hits(hits, "X", gap=5.0)) == 2


def test_event_best_hit_and_wall_clock():
    hits = [Hit(1, "/f/cam.mp4", 1.0, 0.4), Hit(1, "/f/cam.mp4", 2.0, 0.95)]
    started = {1: dt.datetime(2026, 8, 30, 14, 0, 0)}
    event = group_hits(hits, "X", gap=5.0, started_at=started)[0]
    assert event.best_t == 2.0 and event.best_score == pytest.approx(0.95)
    assert event.wall() == dt.datetime(2026, 8, 30, 14, 0, 1)
    assert json.loads(json.dumps(event.to_dict()))["start_tc"] == "00:00:01"


def test_arrivals_keeps_only_first_after_absence():
    events = group_hits(_hits([10, 20, 700, 710, 1400]), "X", gap=5.0)
    got = [e.start for e in arrivals(events, absence=300.0)]
    assert got == [10, 700, 1400]


def test_motion_gate_ignores_static_scene():
    gate = MotionGate(threshold=0.004)
    still = np.full((120, 160, 3), 90, dtype=np.uint8)
    assert gate.is_active(gate.score(still))          # first frame is always kept
    assert not gate.is_active(gate.score(still))
    moved = still.copy()
    moved[30:90, 40:120] = 255
    assert gate.is_active(gate.score(moved))


# ------------------------------------------------------------------ tracking
def test_iou_of_identical_and_disjoint_boxes():
    assert iou((0, 0, 10, 10), (0, 0, 10, 10)) == pytest.approx(1.0)
    assert iou((0, 0, 10, 10), (50, 50, 10, 10)) == 0.0
    assert iou((0, 0, 10, 10), (5, 0, 10, 10)) == pytest.approx(1 / 3)


def test_tracker_follows_one_person_across_frames():
    tracker = IoUTracker()
    ids = []
    for step in range(5):
        (track,) = tracker.update(step * 0.5, [(10 + step * 4, 20, 40, 90)])
        ids.append(track.id)
    assert len(set(ids)) == 1, "a person drifting slowly is one track"
    assert tracker.tracks[ids[0]].hits == 5


def test_tracker_separates_two_people_and_forgets_stale_ones():
    tracker = IoUTracker(max_gap=1.0)
    first = tracker.update(0.0, [(0, 0, 40, 90), (300, 0, 40, 90)])
    assert len({t.id for t in first}) == 2
    later = tracker.update(5.0, [(0, 0, 40, 90)])          # long after the gap
    assert later[0].id not in {t.id for t in first}, "a stale track is not reused"


def test_an_index_written_by_an_older_version_still_opens(tmp_path):
    """Upgrading must never strand a customer's index.

    Older releases wrote `objects` without the colour, track and motion
    columns. The migration adds them - but only if opening the database gets
    that far, which it does not if an index that names those columns is created
    first.
    """
    import sqlite3

    from vscan.db import Index

    root = tmp_path / "old-index"
    root.mkdir()
    old = sqlite3.connect(root / "index.db")
    old.executescript("""
        CREATE TABLE videos (id INTEGER PRIMARY KEY, path TEXT UNIQUE NOT NULL,
                             frames_kept INTEGER DEFAULT 0);
        CREATE TABLE frames (id INTEGER PRIMARY KEY, video_id INTEGER, t REAL);
        CREATE TABLE objects (id INTEGER PRIMARY KEY, video_id INTEGER,
                              frame_id INTEGER, t REAL, label TEXT, score REAL,
                              x REAL, y REAL, w REAL, h REAL);
        CREATE TABLE person_embeddings (id INTEGER PRIMARY KEY, person_id INTEGER,
                                        emb BLOB NOT NULL, source TEXT, crop TEXT);
        INSERT INTO objects(video_id, frame_id, t, label, score, x, y, w, h)
        VALUES (1, 1, 3.0, 'car', 0.9, 0, 0, 10, 10);
    """)
    old.commit()
    old.close()

    with Index(root) as index:
        columns = {r["name"] for r in index.conn.execute("PRAGMA table_info(objects)")}
        assert {"colour", "track", "motion"} <= columns
        assert {"kind"} <= {r["name"] for r in
                            index.conn.execute("PRAGMA table_info(person_embeddings)")}
        assert index.conn.execute("SELECT COUNT(*) FROM objects").fetchone()[0] == 1
        assert index.zones() == []              # new tables arrive with the upgrade


def test_selecting_a_video_by_id_does_not_also_match_filenames(tmp_path):
    """A CCTV export is called gate_20260830.mp4; selecting video 2 must not
    drag in every file whose name happens to contain a 2."""
    from vscan.db import Index

    class _Info:
        def __init__(self, path):
            self.path = path
            self.duration, self.fps = 10.0, 5.0
            self.width, self.height = 320, 240
            self.codec, self.started_at = "h264", None

    with Index(tmp_path / "index") as index:
        for name in ("gate_20260830.mp4", "door_20260831.mp4"):
            index.upsert_video(_Info(tmp_path / name), 2.0, name, {})
        assert [r["id"] for r in index.resolve_videos(["2"])] == [2]
        assert [r["id"] for r in index.resolve_videos(["gate"])] == [1]
        assert len(index.resolve_videos(["2026"])) == 2      # still a substring


def test_suggestions_leave_out_what_the_detector_is_guessing_at(tmp_path):
    """On cluttered indoor footage YOLOX reads a carrier bag as a dog at 0.51
    and a cabinet as an oven at 0.42. Searching still finds those if asked;
    offering them as things to look for would be a lie."""
    from vscan.db import Index

    class _Info:
        def __init__(self, path):
            self.path = path
            self.duration, self.fps = 60.0, 10.0
            self.width, self.height = 640, 480
            self.codec, self.started_at = "h264", None

    with Index(tmp_path / "index") as index:
        video_id = index.upsert_video(_Info(tmp_path / "shop.mp4"), 2.0, "fp", {})
        frame_id = index.add_frame(video_id, 1.0, 0.5, None)
        for score in (0.92, 0.74, 0.71, 0.58):                # a real person
            index.add_object(video_id, frame_id, 1.0, "person", score,
                             (0, 0, 40, 90), "gray", 1, 0.3)
        for score in (0.51, 0.41, 0.41):                      # a bag, allegedly
            index.add_object(video_id, frame_id, 1.0, "dog", score,
                             (0, 0, 30, 30), "gray", 1, 0.0)
        index.commit()

        offered = index.contents()
        assert [l["label"] for l in offered["labels"]] == ["person"]
        assert offered["labels"][0]["count"] == 4
        assert [c["colour"] for c in offered["combos"]] == ["gray"]
        # ... but the dog is still in the index for anyone who asks for it
        assert len(index.objects_for(video_id, ["dog"])) == 3
