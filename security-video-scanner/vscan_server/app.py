"""Application wiring: settings -> store -> job runner -> API -> static UI."""
from __future__ import annotations

import logging
import secrets
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from . import __version__
from .api import router
from .config import Settings, get_settings
from .handlers import register_all
from .jobs import JobRunner
from .security import hash_password
from .store import Store

LOG = logging.getLogger("vscan.server")
STATIC_DIR = Path(__file__).parent / "static"


def bootstrap_admin(store: Store, settings: Settings) -> None:
    """First run on a fresh install: make sure there is exactly one way in."""
    if store.users():
        return
    password = settings.bootstrap_password or secrets.token_urlsafe(15)
    store.create_user(settings.bootstrap_admin, hash_password(password), "admin")
    store.audit("user.created", detail={"username": settings.bootstrap_admin,
                                        "role": "admin", "source": "bootstrap"})
    if settings.bootstrap_password:
        LOG.warning("created the first admin %r from VSCAN_ADMIN_PASSWORD",
                    settings.bootstrap_admin)
        return
    creds = settings.data_dir / "initial-admin-password.txt"
    creds.write_text(f"{settings.bootstrap_admin}\n{password}\n", encoding="utf-8")
    creds.chmod(0o600)
    LOG.warning("=" * 68)
    LOG.warning("first run: admin account %r created", settings.bootstrap_admin)
    LOG.warning("temporary password: %s", password)
    LOG.warning("also written to %s - change it and delete that file", creds)
    LOG.warning("=" * 68)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        store = Store(settings.app_db)
        bootstrap_admin(store, settings)
        store.purge_expired_sessions()
        runner = JobRunner(store, settings.workers)
        register_all(runner, settings)
        runner.start()
        app.state.settings = settings
        app.state.store = store
        app.state.runner = runner
        LOG.info("vscan server %s ready - data in %s, footage roots: %s",
                 __version__, settings.data_dir,
                 ", ".join(str(p) for p in settings.footage_dirs) or "(none configured)")
        try:
            yield
        finally:
            runner.stop()
            store.close()

    app = FastAPI(title="vscan", version=__version__, lifespan=lifespan,
                  docs_url="/api/docs", openapi_url="/api/openapi.json")
    app.include_router(router)

    @app.exception_handler(PermissionError)
    async def _permission_denied(_: Request, exc: PermissionError) -> JSONResponse:
        return JSONResponse({"detail": str(exc)}, status_code=403)

    if STATIC_DIR.is_dir():
        app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

        @app.get("/", include_in_schema=False)
        def index() -> FileResponse:
            return FileResponse(STATIC_DIR / "index.html")

    return app


app = create_app  # uvicorn factory target: `uvicorn vscan_server.app:app --factory`


def main() -> int:
    """Console entry point: `vscan-server`."""
    import uvicorn

    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s")
    settings = get_settings()
    import os
    uvicorn.run("vscan_server.app:app", factory=True,
                host=os.environ.get("VSCAN_HOST", "0.0.0.0"),
                port=int(os.environ.get("VSCAN_PORT", "8080")),
                proxy_headers=True, forwarded_allow_ips="*",
                log_level=os.environ.get("VSCAN_LOG_LEVEL", "info"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
