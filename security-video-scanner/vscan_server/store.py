"""Application database: users, sessions, jobs, audit trail, settings.

Separate from the vscan index on purpose - the index holds biometric data and
can be purged wholesale without losing accounts or the audit trail.
"""
from __future__ import annotations

import datetime as dt
import json
import sqlite3
import threading
from pathlib import Path
from typing import Any, Iterable

ROLES = ("viewer", "analyst", "admin")
ROLE_RANK = {role: i for i, role in enumerate(ROLES)}

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY,
    username      TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL DEFAULT 'viewer',
    active        INTEGER NOT NULL DEFAULT 1,
    created_at    TEXT NOT NULL,
    last_login    TEXT
);

CREATE TABLE IF NOT EXISTS sessions (
    token      TEXT PRIMARY KEY,
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    ip         TEXT,
    user_agent TEXT
);
CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);

CREATE TABLE IF NOT EXISTS jobs (
    id          INTEGER PRIMARY KEY,
    kind        TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'queued',
    title       TEXT,
    params      TEXT,
    progress    REAL DEFAULT 0,
    message     TEXT,
    result      TEXT,
    error       TEXT,
    cancel      INTEGER DEFAULT 0,
    created_by  INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at  TEXT NOT NULL,
    started_at  TEXT,
    finished_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status, id);

CREATE TABLE IF NOT EXISTS audit (
    id       INTEGER PRIMARY KEY,
    ts       TEXT NOT NULL,
    user_id  INTEGER,
    username TEXT,
    action   TEXT NOT NULL,
    detail   TEXT,
    ip       TEXT
);
CREATE INDEX IF NOT EXISTS idx_audit_ts ON audit(ts);

CREATE TABLE IF NOT EXISTS app_settings (key TEXT PRIMARY KEY, value TEXT);
"""


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


class Store:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def close(self) -> None:
        with self._lock:
            self.conn.commit()
            self.conn.close()

    def _write(self, sql: str, params: Iterable[Any] = ()) -> sqlite3.Cursor:
        with self._lock:
            cur = self.conn.execute(sql, tuple(params))
            self.conn.commit()
            return cur

    def _read(self, sql: str, params: Iterable[Any] = ()) -> list[sqlite3.Row]:
        with self._lock:
            return list(self.conn.execute(sql, tuple(params)))

    # -- users -------------------------------------------------------------
    def create_user(self, username: str, password_hash: str, role: str = "viewer") -> int:
        if role not in ROLES:
            raise ValueError(f"unknown role {role!r}")
        cur = self._write(
            "INSERT INTO users(username, password_hash, role, created_at) VALUES (?,?,?,?)",
            (username, password_hash, role, _now()))
        return int(cur.lastrowid)

    def user_by_name(self, username: str) -> sqlite3.Row | None:
        rows = self._read("SELECT * FROM users WHERE username = ?", (username,))
        return rows[0] if rows else None

    def user(self, user_id: int) -> sqlite3.Row | None:
        rows = self._read("SELECT * FROM users WHERE id = ?", (user_id,))
        return rows[0] if rows else None

    def users(self) -> list[sqlite3.Row]:
        return self._read("SELECT * FROM users ORDER BY username")

    def update_user(self, user_id: int, **fields: Any) -> None:
        allowed = {"password_hash", "role", "active", "last_login"}
        sets = {k: v for k, v in fields.items() if k in allowed and v is not None}
        if not sets:
            return
        assigns = ", ".join(f"{k} = ?" for k in sets)
        self._write(f"UPDATE users SET {assigns} WHERE id = ?",
                    (*sets.values(), user_id))

    def delete_user(self, user_id: int) -> None:
        self._write("DELETE FROM users WHERE id = ?", (user_id,))

    def count_admins(self) -> int:
        rows = self._read("SELECT COUNT(*) AS n FROM users WHERE role='admin' AND active=1")
        return int(rows[0]["n"])

    # -- sessions ----------------------------------------------------------
    def create_session(self, token: str, user_id: int, hours: int,
                       ip: str | None, user_agent: str | None) -> None:
        expires = dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=hours)
        self._write(
            "INSERT INTO sessions(token, user_id, created_at, expires_at, ip, user_agent)"
            " VALUES (?,?,?,?,?,?)",
            (token, user_id, _now(), expires.isoformat(timespec="seconds"),
             ip, (user_agent or "")[:300]))

    def session_user(self, token: str) -> sqlite3.Row | None:
        rows = self._read(
            "SELECT u.* FROM sessions s JOIN users u ON u.id = s.user_id"
            " WHERE s.token = ? AND s.expires_at > ? AND u.active = 1",
            (token, _now()))
        return rows[0] if rows else None

    def delete_session(self, token: str) -> None:
        self._write("DELETE FROM sessions WHERE token = ?", (token,))

    def delete_user_sessions(self, user_id: int) -> None:
        self._write("DELETE FROM sessions WHERE user_id = ?", (user_id,))

    def purge_expired_sessions(self) -> int:
        cur = self._write("DELETE FROM sessions WHERE expires_at <= ?", (_now(),))
        return cur.rowcount

    # -- jobs --------------------------------------------------------------
    def create_job(self, kind: str, title: str, params: dict, user_id: int | None) -> int:
        cur = self._write(
            "INSERT INTO jobs(kind, status, title, params, created_by, created_at)"
            " VALUES (?, 'queued', ?, ?, ?, ?)",
            (kind, title, json.dumps(params, ensure_ascii=False), user_id, _now()))
        return int(cur.lastrowid)

    def job(self, job_id: int) -> dict | None:
        rows = self._read("SELECT * FROM jobs WHERE id = ?", (job_id,))
        return self._job_dict(rows[0]) if rows else None

    def jobs(self, limit: int = 50, status: str | None = None,
             kind: str | None = None) -> list[dict]:
        sql = "SELECT * FROM jobs"
        params: list[Any] = []
        where = []
        if status:
            where.append("status = ?")
            params.append(status)
        if kind:
            where.append("kind = ?")
            params.append(kind)
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        return [self._job_dict(r) for r in self._read(sql, params)]

    @staticmethod
    def _job_dict(row: sqlite3.Row) -> dict:
        out = dict(row)
        for key in ("params", "result"):
            if out.get(key):
                try:
                    out[key] = json.loads(out[key])
                except json.JSONDecodeError:
                    out[key] = None
        out["cancel"] = bool(out.get("cancel"))
        return out

    def start_job(self, job_id: int) -> None:
        self._write("UPDATE jobs SET status='running', started_at=? WHERE id=?",
                    (_now(), job_id))

    def update_job(self, job_id: int, progress: float | None = None,
                   message: str | None = None) -> None:
        sets, params = [], []
        if progress is not None:
            sets.append("progress = ?")
            params.append(max(0.0, min(1.0, progress)))
        if message is not None:
            sets.append("message = ?")
            params.append(message)
        if not sets:
            return
        params.append(job_id)
        self._write(f"UPDATE jobs SET {', '.join(sets)} WHERE id = ?", params)

    def finish_job(self, job_id: int, status: str, result: Any = None,
                   error: str | None = None) -> None:
        self._write(
            "UPDATE jobs SET status=?, result=?, error=?, finished_at=?,"
            " progress=CASE WHEN ?='done' THEN 1.0 ELSE progress END WHERE id=?",
            (status, json.dumps(result, ensure_ascii=False) if result is not None else None,
             error, _now(), status, job_id))

    def request_cancel(self, job_id: int) -> None:
        self._write("UPDATE jobs SET cancel=1 WHERE id=? AND status IN ('queued','running')",
                    (job_id,))

    def cancel_requested(self, job_id: int) -> bool:
        rows = self._read("SELECT cancel FROM jobs WHERE id = ?", (job_id,))
        return bool(rows and rows[0]["cancel"])

    def requeue_stale_jobs(self) -> int:
        """After a restart no job is running any more - mark the leftovers failed."""
        cur = self._write(
            "UPDATE jobs SET status='failed', error='interrupted by a server restart',"
            " finished_at=? WHERE status IN ('queued','running')", (_now(),))
        return cur.rowcount

    # -- audit -------------------------------------------------------------
    def audit(self, action: str, user: sqlite3.Row | dict | None = None,
              detail: dict | None = None, ip: str | None = None) -> None:
        user_id = user["id"] if user is not None else None
        username = user["username"] if user is not None else None
        self._write(
            "INSERT INTO audit(ts, user_id, username, action, detail, ip)"
            " VALUES (?,?,?,?,?,?)",
            (_now(), user_id, username, action,
             json.dumps(detail, ensure_ascii=False) if detail else None, ip))

    def audit_entries(self, limit: int = 200, action: str | None = None,
                      username: str | None = None) -> list[dict]:
        sql = "SELECT * FROM audit"
        where, params = [], []
        if action:
            where.append("action LIKE ?")
            params.append(f"%{action}%")
        if username:
            where.append("username = ?")
            params.append(username)
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        out = []
        for row in self._read(sql, params):
            entry = dict(row)
            if entry.get("detail"):
                try:
                    entry["detail"] = json.loads(entry["detail"])
                except json.JSONDecodeError:
                    pass
            out.append(entry)
        return out

    # -- settings ----------------------------------------------------------
    def get_setting(self, key: str, default: Any = None) -> Any:
        rows = self._read("SELECT value FROM app_settings WHERE key = ?", (key,))
        if not rows:
            return default
        try:
            return json.loads(rows[0]["value"])
        except json.JSONDecodeError:
            return rows[0]["value"]

    def set_setting(self, key: str, value: Any) -> None:
        self._write("INSERT OR REPLACE INTO app_settings(key, value) VALUES (?,?)",
                    (key, json.dumps(value, ensure_ascii=False)))

    def all_settings(self) -> dict[str, Any]:
        return {r["key"]: self.get_setting(r["key"])
                for r in self._read("SELECT key FROM app_settings")}
