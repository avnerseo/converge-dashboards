"""Watched zones: "when did the door open" over a recording, locally.

The fixture builds a static camera watching a door that opens twice at known
times, indexes it, and then asks the questions an operator would ask.
"""
from __future__ import annotations

import shutil

import pytest

pytest.importorskip("cv2")
import numpy as np                                          # noqa: E402

from conftest import build_static_camera_clip               # noqa: E402
from vscan.db import Index                                  # noqa: E402
from vscan.events import group_hits                         # noqa: E402
from vscan.indexer import IndexOptions, Indexer             # noqa: E402
from vscan.zones import (Box, ZonePlan, preview, run, scan,  # noqa: E402
                         time_weighted_indices)

HAS_FFMPEG = bool(shutil.which("ffmpeg"))
W, H, FPS = 640, 480, 10
DOOR = (430, 90, 120, 240)                    # pixels: x, y, w, h
DOOR_BOX = [DOOR[0] / W, DOOR[1] / H, DOOR[2] / W, DOOR[3] / H]
OPEN = [(12.0, 20.0), (38.0, 44.0)]           # seconds the door stands open
SECONDS = 60


@pytest.fixture(scope="module")
def door(tmp_path_factory) -> tuple[Index, int]:
    if not HAS_FFMPEG:
        pytest.skip("ffmpeg is needed to build the sample recording")
    root = tmp_path_factory.mktemp("zones")
    video = root / "door.mp4"
    build_static_camera_clip(video, seconds=SECONDS, fps=FPS,
                             open_windows=OPEN, door=DOOR, size=(W, H))
    index = Index(root / "index")
    Indexer(index, IndexOptions(sample_fps=2.0, detect_faces=False,
                                detect_objects=False)).run(video, progress=False)
    return index, int(index.find_video(video)["id"])


def _times(hits) -> list[float]:
    return sorted(round(h.t, 1) for h in hits)


def test_heartbeat_frames_record_the_scene_even_when_nothing_moves(door):
    """Without a periodic frame there is nothing to compare a state against."""
    index, video_id = door
    times = [r["t"] for r in index.frames_for(video_id)]
    assert len(times) >= SECONDS / 10          # one every keyframe_every at least
    quiet = [t for t in times if not any(a - 1 <= t <= b + 1 for a, b in OPEN)]
    assert quiet, "the still stretches of the recording were not sampled at all"


def test_change_mode_finds_the_door_open_and_nothing_else(door):
    index, video_id = door
    result = scan(index, video_id, DOOR_BOX, mode="change", sensitivity=0.15)
    assert result.hits, "the open door was not noticed"
    for hit in result.hits:
        assert any(a - 1 <= hit.t <= b + 1 for a, b in OPEN), \
            f"flagged {hit.t}s, when the door was shut"
    # both openings, not just the first
    assert {a for a, _ in OPEN} <= {round(h.t) for h in result.hits} or \
        len(group_hits(result.hits, "door", gap=6.0)) == len(OPEN)


def test_motion_mode_reports_the_moments_of_change(door):
    """Every swing, opening and closing alike - four transitions, not two."""
    index, video_id = door
    result = scan(index, video_id, DOOR_BOX, mode="motion", sensitivity=0.15)
    assert len(result.hits) >= len(OPEN) * 2 - 1
    edges = {a for a, _ in OPEN} | {b for _, b in OPEN}
    for hit in result.hits:
        assert any(abs(hit.t - edge) <= 1.5 for edge in edges), \
            f"flagged {hit.t}s, which is not a moment the door moved"


def test_a_blank_stretch_of_wall_never_fires(door):
    index, video_id = door
    result = scan(index, video_id, [0.05, 0.62, 0.2, 0.2], sensitivity=0.15)
    assert result.hits == []


def test_the_scan_reads_only_what_indexing_already_wrote(door):
    """The point of the feature: no decoding, no model, no per-search cost."""
    index, video_id = door
    result = scan(index, video_id, DOOR_BOX)
    assert result.frames_examined == len(
        [r for r in index.frames_for(video_id) if r["thumb"]])
    assert result.rate > 50                    # frames per second, single video


def test_preview_suggests_a_sensitivity_and_reports_the_everyday_change(door):
    index, video_id = door
    stats = preview(index, video_id, DOOR_BOX)
    assert stats["frames"] > 0
    assert 0.01 <= stats["suggested_sensitivity"] <= 0.35
    assert stats["max_change"] > stats["median_change"]


def test_a_saved_zone_survives_a_round_trip(door):
    index, _ = door
    zone_id = index.add_zone("front door", DOOR_BOX, mode="change",
                             sensitivity=0.2)
    row = index.get_zone(zone_id)
    assert row["name"] == "front door" and row["mode"] == "change"
    assert [row["x"], row["y"], row["w"], row["h"]] == pytest.approx(DOOR_BOX)
    with pytest.raises(ValueError):
        index.add_zone("front door", DOOR_BOX)      # names are the search key
    assert index.delete_zone(zone_id)
    assert index.get_zone(zone_id) is None


def test_plan_runs_end_to_end_and_groups_into_events(door):
    index, video_id = door
    plan = ZonePlan.from_dict({"box": DOOR_BOX, "video_ids": [video_id],
                               "label": "door", "sensitivity": 0.15, "gap": 6.0})
    events, examined = run(index, plan)
    assert examined > 0
    assert len(events) == len(OPEN)
    for event, (a, b) in zip(events, OPEN):
        assert a - 1 <= event.start <= b + 1
        assert event.label == "door"
    assert ZonePlan.from_dict(plan.to_dict()).to_dict() == plan.to_dict()


def test_a_box_dragged_past_the_edge_is_clipped_not_refused():
    box = Box.parse([0.8, 0.8, 0.5, 0.5])
    assert box.w == pytest.approx(0.2) and box.h == pytest.approx(0.2)
    assert Box.parse("0.1,0.2,0.3,0.4").as_tuple() == (0.1, 0.2, 0.3, 0.4)
    with pytest.raises(ValueError):
        Box.parse([0.1, 0.1, 0, 0.5])
    with pytest.raises(ValueError):
        Box.parse("0.1,0.2")


def test_pixels_land_inside_the_picture_at_any_resolution():
    box = Box.parse([0.5, 0.25, 0.25, 0.5])
    assert box.pixels(640, 480) == (320, 120, 480, 360)
    assert box.pixels(1920, 1080) == (960, 270, 1440, 810)


def test_the_usual_state_is_measured_in_time_not_in_stored_frames():
    """Motion gating crowds stored frames around incidents. Counting them
    equally would let one busy minute define the 'usual' state of an hour."""
    times = [0.0, 100.0, 101.0, 102.0, 103.0]     # four of five inside one second
    picked = time_weighted_indices(times, samples=100)
    quiet_share = float(np.mean(picked == 0))
    assert quiet_share > 0.9
