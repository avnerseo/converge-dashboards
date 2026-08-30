"""One matrix per embedding table, so a search is a matrix product.

Reading every row out of SQLite and decoding one BLOB at a time costs about
7-14 microseconds per vector - 1.5 seconds for 200k faces, and that grows with
the index. The same comparison as a single numpy product takes 26 ms. This
module keeps the vectors in one float32 matrix, cached on disk next to the
index and rebuilt only when rows were added or removed.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from .db import Index
from .util import LOG

TABLES = ("faces", "appearances")


class VectorSet:
    """The embeddings of one table as (ids, matrix), memory-mapped when cached."""

    def __init__(self, index: Index, table: str):
        if table not in TABLES:
            raise ValueError(f"unknown vector table {table!r}")
        self.index = index
        self.table = table
        self.mat_file = index.root / f"vectors-{table}.npy"
        self.ids_file = index.root / f"vectors-{table}.ids.npy"
        self.meta_file = index.root / f"vectors-{table}.json"

    def _fingerprint(self) -> tuple[int, int]:
        row = self.index.conn.execute(
            f"SELECT COUNT(*) AS n, COALESCE(MAX(id), 0) AS top"
            f" FROM {self.table} WHERE emb IS NOT NULL").fetchone()
        return int(row["n"]), int(row["top"])

    def load(self, rebuild: bool = False) -> tuple[np.ndarray, np.ndarray]:
        count, top = self._fingerprint()
        if not rebuild and self.meta_file.exists():
            try:
                meta = json.loads(self.meta_file.read_text(encoding="utf-8"))
                if meta.get("count") == count and meta.get("top") == top:
                    # memory-mapped: the pages stay in the OS cache between
                    # searches instead of being re-read and decompressed
                    return (np.load(self.ids_file, mmap_mode="r"),
                            np.load(self.mat_file, mmap_mode="r"))
            except (OSError, ValueError, KeyError, json.JSONDecodeError):
                LOG.debug("vector cache for %s unreadable - rebuilding", self.table)
        return self.build(count, top)

    def build(self, count: int | None = None, top: int | None = None
              ) -> tuple[np.ndarray, np.ndarray]:
        if count is None or top is None:
            count, top = self._fingerprint()
        rows = self.index.conn.execute(
            f"SELECT id, emb FROM {self.table} WHERE emb IS NOT NULL ORDER BY id")
        ids: list[int] = []
        vectors: list[np.ndarray] = []
        for row in rows:
            vec = np.frombuffer(row["emb"], dtype=np.float32)
            if vec.size == 0:
                continue
            ids.append(int(row["id"]))
            vectors.append(vec)
        if not vectors:
            empty = np.zeros((0, 1), dtype=np.float32)
            return np.zeros(0, dtype=np.int64), empty

        width = max(v.size for v in vectors)
        mat = np.zeros((len(vectors), width), dtype=np.float32)
        for i, vec in enumerate(vectors):
            mat[i, :vec.size] = vec           # tolerate a mixed-dimension index
        norms = np.linalg.norm(mat, axis=1, keepdims=True)
        np.divide(mat, np.where(norms == 0, 1.0, norms), out=mat)
        id_arr = np.asarray(ids, dtype=np.int64)
        try:
            np.save(self.mat_file, mat)
            np.save(self.ids_file, id_arr)
            self.meta_file.write_text(
                json.dumps({"count": count, "top": top, "dim": int(mat.shape[1])}),
                encoding="utf-8")
        except OSError as exc:                # read-only index directory
            LOG.debug("could not write the %s vector cache: %s", self.table, exc)
        LOG.debug("built %s vector matrix: %d x %d", self.table, *mat.shape)
        return id_arr, mat

    def search(self, queries: np.ndarray, threshold: float,
               limit: int = 0, max_hits: int = 20_000) -> list[tuple[int, float]]:
        """Rows scoring >= threshold against the best of `queries`, best first."""
        ids, mat = self.load()
        if mat.size == 0 or ids.size == 0:
            return []
        q = np.atleast_2d(np.asarray(queries, dtype=np.float32))
        if q.shape[1] != mat.shape[1]:
            width = mat.shape[1]
            padded = np.zeros((q.shape[0], width), dtype=np.float32)
            usable = min(width, q.shape[1])
            padded[:, :usable] = q[:, :usable]
            q = padded
        norms = np.linalg.norm(q, axis=1, keepdims=True)
        q = q / np.where(norms == 0, 1.0, norms)

        scores = (mat @ q.T).max(axis=1)
        hit = np.flatnonzero(scores >= threshold)
        if hit.size == 0:
            return []
        if hit.size > max_hits and not limit:
            LOG.warning("%d matches over the threshold - keeping the best %d. "
                        "Raise the threshold to narrow the search.", hit.size, max_hits)
            limit = max_hits
        order = hit[np.argsort(-scores[hit])]
        if limit:
            order = order[:limit]
        return [(int(ids[i]), float(scores[i])) for i in order]

    def invalidate(self) -> None:
        for path in (self.mat_file, self.ids_file, self.meta_file):
            path.unlink(missing_ok=True)


def clear_caches(root: str | Path) -> None:
    for table in TABLES:
        for suffix in (".npy", ".ids.npy", ".json", ".npz"):
            Path(root, f"vectors-{table}{suffix}").unlink(missing_ok=True)
