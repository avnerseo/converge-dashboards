"""Unit tests that need neither models, network, nor ffmpeg."""
from __future__ import annotations

import datetime as dt
import json

import numpy as np
import pytest

from vscan.events import Hit, arrivals, group_hits
from vscan.motion import MotionGate
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
