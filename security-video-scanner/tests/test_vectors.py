"""The vector matrix that makes search a single numpy product."""
from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("cv2")

from vscan.db import Index, emb_to_blob                    # noqa: E402
from vscan.faces import l2norm                             # noqa: E402
from vscan.vectors import VectorSet                        # noqa: E402


class _Info:
    path = __import__("pathlib").Path("/footage/cam.mp4")
    duration, fps, width, height = 60.0, 25.0, 1920, 1080
    codec, started_at = "h264", None


def _index_with_faces(tmp_path, vectors) -> Index:
    index = Index(tmp_path)
    video_id = index.upsert_video(_Info(), 2.0, "fp", {})
    index.conn.execute("INSERT INTO frames(id, video_id, t, activity)"
                       " VALUES (1, ?, 0, 1)", (video_id,))
    for i, vec in enumerate(vectors):
        index.conn.execute(
            "INSERT INTO faces(video_id, frame_id, t, x, y, w, h, score, sharpness, emb)"
            " VALUES (?,1,?,0,0,40,40,0.9,50,?)",
            (video_id, float(i), emb_to_blob(l2norm(np.asarray(vec, np.float32)))))
    index.commit()
    return index


def test_search_finds_the_matching_vector(tmp_path):
    rng = np.random.default_rng(3)
    vectors = [rng.standard_normal(128) for _ in range(50)]
    index = _index_with_faces(tmp_path, vectors)
    hits = VectorSet(index, "faces").search(vectors[7], threshold=0.99)
    assert [i for i, _ in hits] == [8]                     # row ids start at 1
    assert hits[0][1] == pytest.approx(1.0, abs=1e-5)
    index.close()


def test_cache_is_reused_and_rebuilt_when_rows_change(tmp_path):
    rng = np.random.default_rng(4)
    vectors = [rng.standard_normal(128) for _ in range(20)]
    index = _index_with_faces(tmp_path, vectors)
    store = VectorSet(index, "faces")
    ids, mat = store.load()
    assert mat.shape == (20, 128) and store.mat_file.exists()

    index.conn.execute(
        "INSERT INTO faces(video_id, frame_id, t, x, y, w, h, score, sharpness, emb)"
        " VALUES (1,1,99,0,0,40,40,0.9,50,?)",
        (emb_to_blob(l2norm(np.asarray(vectors[0], np.float32))),))
    index.commit()
    ids2, mat2 = store.load()
    assert mat2.shape == (21, 128), "adding a row must rebuild the matrix"
    index.close()


def test_search_takes_the_best_of_several_queries(tmp_path):
    rng = np.random.default_rng(5)
    vectors = [rng.standard_normal(128) for _ in range(30)]
    index = _index_with_faces(tmp_path, vectors)
    queries = np.stack([l2norm(np.asarray(vectors[2], np.float32)),
                        l2norm(np.asarray(vectors[9], np.float32))])
    hits = dict(VectorSet(index, "faces").search(queries, threshold=0.99))
    assert set(hits) == {3, 10}
    index.close()


def test_empty_index_returns_nothing(tmp_path):
    index = Index(tmp_path)
    assert VectorSet(index, "faces").search(np.ones(128, np.float32), 0.1) == []
    index.close()


def test_unknown_table_is_rejected(tmp_path):
    index = Index(tmp_path)
    with pytest.raises(ValueError):
        VectorSet(index, "videos")
    index.close()
