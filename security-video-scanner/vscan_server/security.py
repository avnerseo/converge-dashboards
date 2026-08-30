"""Passwords, session cookies and role checks."""
from __future__ import annotations

import hashlib
import hmac
import secrets
import sqlite3
import threading
import time

from fastapi import Depends, HTTPException, Request, status

from .config import Settings, get_settings
from .store import ROLE_RANK, Store

COOKIE_NAME = "vscan_session"
_PBKDF2_ROUNDS = 240_000
MIN_PASSWORD_LEN = 10


def hash_password(password: str, *, rounds: int = _PBKDF2_ROUNDS) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, rounds)
    return f"pbkdf2_sha256${rounds}${salt.hex()}${digest.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algo, rounds, salt_hex, digest_hex = encoded.split("$")
        if algo != "pbkdf2_sha256":
            return False
        expected = bytes.fromhex(digest_hex)
        got = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"),
                                  bytes.fromhex(salt_hex), int(rounds))
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(expected, got)


def check_password_policy(password: str) -> None:
    if len(password) < MIN_PASSWORD_LEN:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            f"password must be at least {MIN_PASSWORD_LEN} characters")


def new_session_token() -> str:
    return secrets.token_urlsafe(32)


def client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


# ---------------------------------------------------------------- dependencies
def get_store(request: Request) -> Store:
    return request.app.state.store


def current_user(request: Request, store: Store = Depends(get_store)) -> sqlite3.Row:
    token = request.cookies.get(COOKIE_NAME)
    user = store.session_user(token) if token else None
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "not signed in")
    return user


def require_role(minimum: str):
    """Dependency factory: viewer < analyst < admin."""
    needed = ROLE_RANK[minimum]

    def _dep(user: sqlite3.Row = Depends(current_user)) -> sqlite3.Row:
        if ROLE_RANK.get(user["role"], -1) < needed:
            raise HTTPException(status.HTTP_403_FORBIDDEN,
                                f"this action requires the {minimum} role")
        return user

    return _dep


require_viewer = require_role("viewer")
require_analyst = require_role("analyst")
require_admin = require_role("admin")


def set_session_cookie(response, token: str, settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    response.set_cookie(
        COOKIE_NAME, token, httponly=True, samesite="lax",
        secure=settings.secure_cookie, max_age=settings.session_hours * 3600, path="/")


def clear_session_cookie(response) -> None:
    response.delete_cookie(COOKIE_NAME, path="/")


class LoginThrottle:
    """Slow down password guessing without locking a real user out for long.

    Counts recent failures per (username, client address). Deliberately in
    memory: a restart clears it, which is the right trade for a single-box
    appliance - it is a brute-force brake, not an account-lockout policy.
    """

    def __init__(self, max_failures: int = 5, window_seconds: int = 900):
        self.max_failures = max_failures
        self.window = window_seconds
        self._failures: dict[tuple[str, str], list[float]] = {}
        self._lock = threading.Lock()

    def _recent(self, key: tuple[str, str], now: float) -> list[float]:
        return [ts for ts in self._failures.get(key, []) if now - ts < self.window]

    def retry_after(self, username: str, ip: str | None) -> int:
        """Seconds the caller must wait, or 0 when they may try now."""
        key = (username.strip().lower(), ip or "-")
        now = time.time()
        with self._lock:
            recent = self._recent(key, now)
            self._failures[key] = recent
            if len(recent) < self.max_failures:
                return 0
            return max(1, int(self.window - (now - recent[0])))

    def record_failure(self, username: str, ip: str | None) -> None:
        key = (username.strip().lower(), ip or "-")
        now = time.time()
        with self._lock:
            self._failures[key] = self._recent(key, now) + [now]

    def clear(self, username: str, ip: str | None) -> None:
        with self._lock:
            self._failures.pop((username.strip().lower(), ip or "-"), None)

    def reset(self) -> None:
        """Forget every recorded failure (used by tests and by admins)."""
        with self._lock:
            self._failures.clear()


login_throttle = LoginThrottle()
