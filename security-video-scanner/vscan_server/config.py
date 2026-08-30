"""Deployment settings. Everything is environment-driven so one image fits all sites."""
from __future__ import annotations

import os
import secrets
from dataclasses import dataclass, field
from pathlib import Path


def _env_paths(name: str) -> list[Path]:
    raw = os.environ.get(name, "")
    return [Path(p).expanduser().resolve() for p in raw.split(os.pathsep) if p.strip()]


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, "").strip() or default)
    except ValueError:
        return default


def _env_bool(name: str, default: bool) -> bool:
    val = os.environ.get(name)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


@dataclass
class Settings:
    """Runtime configuration.

    VSCAN_DATA_DIR      where the app database, index and exports live
    VSCAN_FOOTAGE_DIRS  os.pathsep-separated roots holding the recordings
                        (mounted read-only in the compose file)
    VSCAN_SECRET_KEY    signing/secret material; generated and persisted if unset
    """

    # Every default is a factory: the environment is read when a Settings object
    # is built, not when this module happens to be imported.
    data_dir: Path = field(default_factory=lambda: Path(
        os.environ.get("VSCAN_DATA_DIR", "./vscan-data")).expanduser().resolve())
    footage_dirs: list[Path] = field(default_factory=lambda: _env_paths("VSCAN_FOOTAGE_DIRS"))
    secret_key: str = ""
    session_hours: int = field(default_factory=lambda: _env_int("VSCAN_SESSION_HOURS", 12))
    workers: int = field(default_factory=lambda: _env_int("VSCAN_WORKERS", 2))
    ask_enabled: bool = field(default_factory=lambda: _env_bool("VSCAN_ASK_ENABLED", True))
    retention_days: int = field(default_factory=lambda: _env_int("VSCAN_RETENTION_DAYS", 0))
    bootstrap_admin: str = field(
        default_factory=lambda: os.environ.get("VSCAN_ADMIN_USER", "admin"))
    bootstrap_password: str = field(
        default_factory=lambda: os.environ.get("VSCAN_ADMIN_PASSWORD", ""))
    max_upload_mb: int = field(default_factory=lambda: _env_int("VSCAN_MAX_UPLOAD_MB", 25))
    secure_cookie: bool = field(
        default_factory=lambda: _env_bool("VSCAN_SECURE_COOKIE", False))

    def __post_init__(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.exports_dir.mkdir(parents=True, exist_ok=True)
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        self.previews_dir.mkdir(parents=True, exist_ok=True)
        self.secret_key = os.environ.get("VSCAN_SECRET_KEY") or self._persisted_secret()

    def _persisted_secret(self) -> str:
        key_file = self.data_dir / "secret.key"
        if key_file.exists():
            return key_file.read_text(encoding="utf-8").strip()
        secret = secrets.token_urlsafe(48)
        key_file.write_text(secret, encoding="utf-8")
        key_file.chmod(0o600)
        return secret

    # -- derived paths -----------------------------------------------------
    @property
    def app_db(self) -> Path:
        return self.data_dir / "app.db"

    @property
    def index_dir(self) -> Path:
        return self.data_dir / "index"

    @property
    def exports_dir(self) -> Path:
        return self.data_dir / "exports"

    @property
    def uploads_dir(self) -> Path:
        return self.data_dir / "uploads"

    @property
    def previews_dir(self) -> Path:
        """Browser-playable transcodes of the moments an operator opens."""
        return self.data_dir / "previews"

    def resolve_footage(self, path: str | Path) -> Path:
        """Resolve `path` and refuse anything outside the configured roots.

        Every filesystem path that arrives from a browser goes through here.
        """
        target = Path(path).expanduser()
        if not target.is_absolute():
            if not self.footage_dirs:
                raise PermissionError("no footage directories are configured")
            target = self.footage_dirs[0] / target
        target = target.resolve()
        for root in self.footage_dirs:
            if target == root or root in target.parents:
                return target
        raise PermissionError(f"path is outside the configured footage directories: {path}")


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def set_settings(settings: Settings) -> Settings:
    """Used by tests and by the CLI entry point to inject a configuration."""
    global _settings
    _settings = settings
    return settings
