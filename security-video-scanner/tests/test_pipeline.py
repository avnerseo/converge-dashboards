"""End-to-end: build a clip with real faces in it, index it, then search it.

Skipped unless face photos are available, since a face pipeline cannot be
tested without faces. Point VSCAN_TEST_FACES at two portraits of two different
people (colon-separated) to enable it:

    VSCAN_TEST_FACES=alice.jpg:bob.jpg pytest tests/test_pipeline.py
"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

import pytest

pytest.importorskip("cv2")

from vscan.db import Index                          # noqa: E402
from vscan.events import group_hits                 # noqa: E402
from vscan.faces import FaceEngine                  # noqa: E402
from vscan.indexer import IndexOptions, Indexer     # noqa: E402
from vscan.search import (appearance_at, cluster_faces, enroll_from_faces,
                          enroll_images, find_person, search_vectors)  # noqa: E402

FACES = [Path(p) for p in os.environ.get("VSCAN_TEST_FACES", "").split(":") if p]

pytestmark = [
    pytest.mark.skipif(not shutil.which("ffmpeg"), reason="ffmpeg not installed"),
    pytest.mark.skipif(len(FACES) < 2 or not all(f.exists() for f in FACES),
                       reason="set VSCAN_TEST_FACES=a.jpg:b.jpg to run"),
]


@pytest.fixture(scope="module")
def demo(tmp_path_factory) -> tuple[Path, list]:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from make_sample_video import build

    out = tmp_path_factory.mktemp("footage") / "demo.mp4"
    windows = build(FACES[:2], out, seconds=24, fps=10)
    return out, windows


@pytest.fixture(scope="module")
def indexed(demo, tmp_path_factory) -> tuple[Index, Path, list]:
    video, windows = demo
    index = Index(tmp_path_factory.mktemp("index"))
    Indexer(index, IndexOptions(sample_fps=3.0, detect_objects=True,
                                detect_appearance=True)).run(video)
    return index, video, windows


def test_index_finds_faces(indexed):
    index, _, _ = indexed
    assert index.stats()["faces"] > 0
    assert index.stats()["frames"] > 0


def test_clusters_split_the_two_people(indexed):
    index, _, windows = indexed
    clusters = cluster_faces(index, min_size=2)
    assert len(clusters) == 2, "expected one cluster per person"
    spans = sorted((c["times"][0], c["times"][-1]) for c in clusters)
    for (start, end), (_, t0, t1) in zip(spans, windows):
        assert t0 - 1 <= start <= t1 and t0 <= end <= t1 + 1


def test_find_person_hits_only_their_window(indexed):
    index, _, windows = indexed
    clusters = cluster_faces(index, min_size=2)
    first = min(clusters, key=lambda c: c["times"][0])
    enroll_from_faces(index, "First Person", first["face_ids"])
    events = group_hits(find_person(index, "First Person"), "First Person", gap=5.0)
    assert len(events) == 1
    _, t0, t1 = windows[0]
    assert t0 - 1 <= events[0].start and events[0].end <= t1 + 1


def test_enroll_from_still_photo_matches_the_same_person(indexed):
    index, _, windows = indexed
    engine = FaceEngine(min_embed_face=16)
    assert enroll_images(index, engine, "From Photo", [FACES[0]]) == 1
    events = group_hits(find_person(index, "From Photo"), "From Photo", gap=5.0)
    assert len(events) == 1, "a still photo should match exactly one appearance"
    _, t0, t1 = windows[0]
    assert t0 - 1 <= events[0].start and events[0].end <= t1 + 1


def test_appearance_vectors_are_stored_once_per_track(indexed):
    index, _, _ = indexed
    stats = index.stats()
    assert stats["appearances"] > 0, "no appearance vectors were written"
    assert stats["appearances"] < stats["objects"], \
        "the tracker should embed far fewer crops than there are person boxes"
    tracks = {r["track"] for r in index.conn.execute(
        "SELECT DISTINCT track FROM appearances")}
    assert len(tracks) >= 2, "the two people should not share one track"


def test_similar_search_finds_the_right_window(indexed):
    index, _, windows = indexed
    video_id = int(index.videos()[0]["id"])
    _, first_start, first_end = windows[0]
    midpoint = (first_start + first_end) / 2

    taken = appearance_at(index, video_id, midpoint)
    assert taken is not None, "could not read an appearance at that moment"
    emb, _box = taken

    hits = search_vectors(index, "appearances", emb, threshold=0.6)
    assert hits, "the person should at least match themselves"
    for hit in hits:
        assert first_start - 2 <= hit.t <= first_end + 2, (
            "appearance search leaked into the other person's window")
