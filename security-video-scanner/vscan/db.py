"""SQLite index: one directory holds the DB plus the frame/face thumbnails."""
from __future__ import annotations

import datetime as dt
import json
import sqlite3
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np

from .util import ensure_dir

SCHEMA_VERSION = 1

SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);

CREATE TABLE IF NOT EXISTS videos (
    id           INTEGER PRIMARY KEY,
    path         TEXT UNIQUE NOT NULL,
    fingerprint  TEXT,
    duration     REAL,
    fps          REAL,
    width        INTEGER,
    height       INTEGER,
    codec        TEXT,
    started_at   TEXT,           -- wall clock of t=0, ISO, may be NULL
    sample_fps   REAL,
    indexed_at   TEXT,
    frames_kept  INTEGER DEFAULT 0,
    settings     TEXT
);

CREATE TABLE IF NOT EXISTS frames (
    id        INTEGER PRIMARY KEY,
    video_id  INTEGER NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    t         REAL NOT NULL,
    activity  REAL DEFAULT 0,
    thumb     TEXT,
    UNIQUE (video_id, t)
);
CREATE INDEX IF NOT EXISTS idx_frames_vt ON frames(video_id, t);

CREATE TABLE IF NOT EXISTS faces (
    id        INTEGER PRIMARY KEY,
    video_id  INTEGER NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    frame_id  INTEGER NOT NULL REFERENCES frames(id) ON DELETE CASCADE,
    t         REAL NOT NULL,
    x REAL, y REAL, w REAL, h REAL,
    score     REAL,
    sharpness REAL,
    crop      TEXT,
    emb       BLOB
);
CREATE INDEX IF NOT EXISTS idx_faces_vt ON faces(video_id, t);

CREATE TABLE IF NOT EXISTS objects (
    id        INTEGER PRIMARY KEY,
    video_id  INTEGER NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    frame_id  INTEGER NOT NULL REFERENCES frames(id) ON DELETE CASCADE,
    t         REAL NOT NULL,
    label     TEXT NOT NULL,
    score     REAL,
    x REAL, y REAL, w REAL, h REAL
);
CREATE INDEX IF NOT EXISTS idx_objects_vtl ON objects(video_id, t, label);

CREATE TABLE IF NOT EXISTS persons (
    id         INTEGER PRIMARY KEY,
    name       TEXT UNIQUE NOT NULL,
    notes      TEXT,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS person_embeddings (
    id        INTEGER PRIMARY KEY,
    person_id INTEGER NOT NULL REFERENCES persons(id) ON DELETE CASCADE,
    emb       BLOB NOT NULL,
    source    TEXT,
    crop      TEXT
);
CREATE INDEX IF NOT EXISTS idx_pemb_person ON person_embeddings(person_id);

CREATE TABLE IF NOT EXISTS face_labels (
    face_id   INTEGER PRIMARY KEY REFERENCES faces(id) ON DELETE CASCADE,
    person_id INTEGER NOT NULL REFERENCES persons(id) ON DELETE CASCADE,
    score     REAL,
    source    TEXT
);
"""


def emb_to_blob(vec: np.ndarray) -> bytes:
    return np.asarray(vec, dtype=np.float32).ravel().tobytes()


def blob_to_emb(blob: bytes | None) -> np.ndarray | None:
    if not blob:
        return None
    return np.frombuffer(blob, dtype=np.float32)


class Index:
    """Thin wrapper over the SQLite index directory."""

    def __init__(self, root: str | Path):
        self.root = ensure_dir(root)
        self.thumbs = ensure_dir(self.root / "thumbs")
        self.crops = ensure_dir(self.root / "crops")
        self.conn = sqlite3.connect(self.root / "index.db")
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.conn.executescript(SCHEMA)
        self.conn.execute(
            "INSERT OR IGNORE INTO meta(key, value) VALUES ('schema_version', ?)",
            (str(SCHEMA_VERSION),),
        )
        self.conn.commit()

    # -- lifecycle ---------------------------------------------------------
    def close(self) -> None:
        self.conn.commit()
        self.conn.close()

    def __enter__(self) -> "Index":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    def rel(self, path: Path) -> str:
        try:
            return str(Path(path).relative_to(self.root))
        except ValueError:
            return str(path)

    def abs(self, rel_path: str | None) -> Path | None:
        if not rel_path:
            return None
        p = Path(rel_path)
        return p if p.is_absolute() else self.root / p

    # -- videos ------------------------------------------------------------
    def upsert_video(self, info, sample_fps: float, fingerprint: str,
                     settings: dict) -> int:
        cur = self.conn.execute("SELECT id FROM videos WHERE path = ?", (str(info.path),))
        row = cur.fetchone()
        started = info.started_at.isoformat() if info.started_at else None
        values = (str(info.path), fingerprint, info.duration, info.fps, info.width,
                  info.height, info.codec, started, sample_fps,
                  dt.datetime.now().isoformat(timespec="seconds"),
                  json.dumps(settings, ensure_ascii=False))
        if row:
            self.conn.execute(
                "UPDATE videos SET fingerprint=?, duration=?, fps=?, width=?, height=?,"
                " codec=?, started_at=?, sample_fps=?, indexed_at=?, settings=?"
                " WHERE id=?", values[1:] + (row["id"],))
            self.conn.commit()
            return int(row["id"])
        cur = self.conn.execute(
            "INSERT INTO videos(path, fingerprint, duration, fps, width, height, codec,"
            " started_at, sample_fps, indexed_at, settings)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?)", values)
        self.conn.commit()
        return int(cur.lastrowid)

    def clear_video_data(self, video_id: int) -> None:
        for tbl in ("objects", "faces", "frames"):
            self.conn.execute(f"DELETE FROM {tbl} WHERE video_id = ?", (video_id,))
        self.conn.commit()

    def get_video(self, video_id: int) -> sqlite3.Row | None:
        return self.conn.execute("SELECT * FROM videos WHERE id = ?", (video_id,)).fetchone()

    def find_video(self, path: str | Path) -> sqlite3.Row | None:
        return self.conn.execute(
            "SELECT * FROM videos WHERE path = ?",
            (str(Path(path).expanduser().resolve()),)).fetchone()

    def videos(self) -> list[sqlite3.Row]:
        return list(self.conn.execute("SELECT * FROM videos ORDER BY id"))

    def resolve_videos(self, selectors: Sequence[str] | None) -> list[sqlite3.Row]:
        """Selectors are video ids, exact paths, or filename substrings."""
        rows = self.videos()
        if not selectors:
            return rows
        out: list[sqlite3.Row] = []
        for sel in selectors:
            hits = [r for r in rows
                    if str(r["id"]) == sel or r["path"] == sel or sel in Path(r["path"]).name]
            if not hits:
                raise SystemExit(f"no indexed video matches {sel!r}")
            out.extend(h for h in hits if h not in out)
        return out

    # -- frames / detections ----------------------------------------------
    def add_frame(self, video_id: int, t: float, activity: float, thumb: str | None) -> int:
        cur = self.conn.execute(
            "INSERT OR REPLACE INTO frames(video_id, t, activity, thumb) VALUES (?,?,?,?)",
            (video_id, round(t, 3), activity, thumb))
        return int(cur.lastrowid)

    def add_face(self, video_id: int, frame_id: int, t: float, box: Sequence[float],
                 score: float, sharpness: float, crop: str | None,
                 emb: np.ndarray | None) -> int:
        cur = self.conn.execute(
            "INSERT INTO faces(video_id, frame_id, t, x, y, w, h, score, sharpness, crop, emb)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (video_id, frame_id, round(t, 3), *[float(v) for v in box],
             float(score), float(sharpness), crop,
             emb_to_blob(emb) if emb is not None else None))
        return int(cur.lastrowid)

    def add_object(self, video_id: int, frame_id: int, t: float, label: str,
                   score: float, box: Sequence[float]) -> int:
        cur = self.conn.execute(
            "INSERT INTO objects(video_id, frame_id, t, label, score, x, y, w, h)"
            " VALUES (?,?,?,?,?,?,?,?,?)",
            (video_id, frame_id, round(t, 3), label, float(score),
             *[float(v) for v in box]))
        return int(cur.lastrowid)

    def set_frames_kept(self, video_id: int, n: int) -> None:
        self.conn.execute("UPDATE videos SET frames_kept = ? WHERE id = ?", (n, video_id))
        self.conn.commit()

    def faces_with_emb(self, video_ids: Iterable[int] | None = None) -> list[sqlite3.Row]:
        sql = ("SELECT f.*, v.path AS video_path, v.started_at AS video_started_at"
               " FROM faces f JOIN videos v ON v.id = f.video_id WHERE f.emb IS NOT NULL")
        params: list[Any] = []
        ids = list(video_ids) if video_ids is not None else None
        if ids:
            sql += f" AND f.video_id IN ({','.join('?' * len(ids))})"
            params += ids
        sql += " ORDER BY f.video_id, f.t"
        return list(self.conn.execute(sql, params))

    def frames_for(self, video_id: int, start: float = 0.0, end: float | None = None,
                   min_activity: float = -1.0) -> list[sqlite3.Row]:
        sql = "SELECT * FROM frames WHERE video_id = ? AND t >= ? AND activity >= ?"
        params: list[Any] = [video_id, start, min_activity]
        if end is not None:
            sql += " AND t <= ?"
            params.append(end)
        sql += " ORDER BY t"
        return list(self.conn.execute(sql, params))

    def objects_for(self, video_id: int, labels: Sequence[str] | None = None,
                    min_score: float = 0.0) -> list[sqlite3.Row]:
        sql = "SELECT * FROM objects WHERE video_id = ? AND score >= ?"
        params: list[Any] = [video_id, min_score]
        if labels:
            sql += f" AND label IN ({','.join('?' * len(labels))})"
            params += list(labels)
        sql += " ORDER BY t"
        return list(self.conn.execute(sql, params))

    # -- persons -----------------------------------------------------------
    def get_or_create_person(self, name: str, notes: str | None = None) -> int:
        row = self.conn.execute("SELECT id FROM persons WHERE name = ?", (name,)).fetchone()
        if row:
            return int(row["id"])
        cur = self.conn.execute(
            "INSERT INTO persons(name, notes, created_at) VALUES (?,?,?)",
            (name, notes, dt.datetime.now().isoformat(timespec="seconds")))
        self.conn.commit()
        return int(cur.lastrowid)

    def person_by_name(self, name: str) -> sqlite3.Row | None:
        return self.conn.execute("SELECT * FROM persons WHERE name = ?", (name,)).fetchone()

    def persons(self) -> list[sqlite3.Row]:
        return list(self.conn.execute(
            "SELECT p.*, (SELECT COUNT(*) FROM person_embeddings e WHERE e.person_id = p.id)"
            " AS n_emb FROM persons p ORDER BY p.name"))

    def add_person_embedding(self, person_id: int, emb: np.ndarray, source: str,
                             crop: str | None = None) -> int:
        cur = self.conn.execute(
            "INSERT INTO person_embeddings(person_id, emb, source, crop) VALUES (?,?,?,?)",
            (person_id, emb_to_blob(emb), source, crop))
        self.conn.commit()
        return int(cur.lastrowid)

    def person_embeddings(self, person_id: int) -> list[sqlite3.Row]:
        return list(self.conn.execute(
            "SELECT * FROM person_embeddings WHERE person_id = ?", (person_id,)))

    def delete_person(self, name: str) -> bool:
        row = self.person_by_name(name)
        if not row:
            return False
        self.conn.execute("DELETE FROM persons WHERE id = ?", (row["id"],))
        self.conn.commit()
        return True

    def label_face(self, face_id: int, person_id: int, score: float, source: str) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO face_labels(face_id, person_id, score, source)"
            " VALUES (?,?,?,?)", (face_id, person_id, score, source))

    def commit(self) -> None:
        self.conn.commit()

    def stats(self) -> dict[str, int]:
        q = lambda sql: int(self.conn.execute(sql).fetchone()[0])  # noqa: E731
        return {
            "videos": q("SELECT COUNT(*) FROM videos"),
            "frames": q("SELECT COUNT(*) FROM frames"),
            "faces": q("SELECT COUNT(*) FROM faces"),
            "objects": q("SELECT COUNT(*) FROM objects"),
            "persons": q("SELECT COUNT(*) FROM persons"),
        }
