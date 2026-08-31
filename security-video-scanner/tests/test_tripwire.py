"""Counting lines: who crossed, when, and which way.

Crossings are read off the tracks stored during indexing, so these tests build
the tracks directly. That keeps them about the question being answered - "did
this person go in or out" - rather than about whether a detector fired.
"""
from __future__ import annotations

import pytest

pytest.importorskip("cv2")

from vscan.db import Index                                   # noqa: E402
from vscan.tripwire import (Line, analysis_size, crossings,   # noqa: E402
                            foot_point, to_events)


class _Info:
    """The bits of a probed video that upsert_video actually reads."""
    def __init__(self, path):
        self.path = path
        self.duration, self.fps = 60.0, 10.0
        self.width, self.height = 640, 480
        self.codec, self.started_at = "h264", None


def _walk(index, video_id, track, label, points, t0=1.0, step=0.5):
    """Store one thing moving through a list of (x, y) foot positions."""
    for i, (x, y) in enumerate(points):
        t = t0 + i * step
        frame_id = index.add_frame(video_id, t, 0.5, None)
        # boxes are stored in analysis pixels, and the foot point is the
        # bottom centre - so a 40x80 box sits above the position given
        index.add_object(video_id, frame_id, t, label, 0.9,
                         (x - 20, y - 80, 40, 80), "red", track, 0.4)
    index.commit()


@pytest.fixture()
def walked(tmp_path):
    index = Index(tmp_path / "index")
    video_id = index.upsert_video(_Info(tmp_path / "gate.mp4"), 2.0, "fp",
                                  {"max_width": 640})
    # the frame is 640x480 and analysis width 640, so pixels are fractions x640
    _walk(index, video_id, 1, "person",                      # left -> right
          [(100, 400), (220, 400), (400, 400), (540, 400)])
    _walk(index, video_id, 2, "person",                      # right -> left
          [(540, 300), (400, 300), (220, 300), (100, 300)], t0=20.0)
    _walk(index, video_id, 3, "person",                      # never crosses
          [(100, 200), (140, 200), (180, 200), (200, 200)], t0=40.0)
    return index, video_id


MIDDLE = Line.parse([0.5, 0.0, 0.5, 1.0])                    # vertical, centred


def test_a_crossing_is_found_once_per_track(walked):
    index, video_id = walked
    found = crossings(index, video_id, MIDDLE)
    assert len(found) == 2, [(c.t, c.direction) for c in found]
    assert {c.track for c in found} == {1, 2}


def test_the_two_directions_are_told_apart(walked):
    index, video_id = walked
    by_track = {c.track: c for c in crossings(index, video_id, MIDDLE)}
    assert by_track[1].direction != by_track[2].direction
    # left-to-right is "out" with the arrow as drawn; flipping swaps both
    assert by_track[1].direction == "out" and by_track[2].direction == "in"
    flipped = Line.parse([0.5, 0.0, 0.5, 1.0], flipped=True)
    swapped = {c.track: c.direction for c in crossings(index, video_id, flipped)}
    assert swapped[1] == "in" and swapped[2] == "out"


def test_the_moment_reported_is_between_the_two_frames(walked):
    index, video_id = walked
    first = next(c for c in crossings(index, video_id, MIDDLE) if c.track == 1)
    # 220px -> 400px is the step that crosses 320px, at t=1.5 and t=2.0
    assert 1.5 <= first.t <= 2.0


def test_walking_parallel_to_the_line_is_not_a_crossing(walked):
    index, video_id = walked
    assert all(c.track != 3 for c in crossings(index, video_id, MIDDLE))


def test_a_line_that_stops_short_is_not_crossed(walked):
    """Someone passing the far end of a doorway has not gone through it."""
    index, video_id = walked
    short = Line.parse([0.5, 0.0, 0.5, 0.2])       # only the top of the frame
    assert crossings(index, video_id, short) == []


def test_the_direction_asked_for_is_the_one_returned(walked):
    index, video_id = walked
    found = crossings(index, video_id, MIDDLE)
    assert len(to_events(found, "gate", direction="in")) == 1
    assert len(to_events(found, "gate", direction="out")) == 1
    assert len(to_events(found, "gate", direction="both")) == 2
    event = to_events(found, "gate", direction="in")[0]
    assert event.meta["direction"] == "in" and event.meta["label"] == "person"
    assert event.start == event.end                # a crossing is a moment


def test_only_the_labels_asked_for_are_counted(walked):
    index, video_id = walked
    _walk(index, video_id, 9, "car", [(100, 450), (540, 450)], 50.0)
    assert len(crossings(index, video_id, MIDDLE, labels=["person"])) == 2
    assert len(crossings(index, video_id, MIDDLE, labels=["car"])) == 1
    assert len(crossings(index, video_id, MIDDLE)) == 3


def test_boxes_are_read_in_the_pixels_they_were_measured_in(walked):
    """Indexing downscales; a line drawn on the picture must still line up."""
    index, video_id = walked
    assert analysis_size(index, video_id) == (640, 480)
    index.conn.execute("UPDATE videos SET settings = ? WHERE id = ?",
                       ('{"max_width": 320}', video_id))
    index.commit()
    assert analysis_size(index, video_id) == (320, 240)
    # the foot point is the bottom centre, in fractions of the frame
    assert foot_point((100, 100, 40, 80), (320, 240)) == pytest.approx((0.375, 0.75))


def test_a_line_needs_two_distinct_points():
    with pytest.raises(ValueError):
        Line.parse([0.5, 0.5, 0.5, 0.505])
    with pytest.raises(ValueError):
        Line.parse("0.1,0.2,0.3")
