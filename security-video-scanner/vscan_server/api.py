"""REST API. Everything the browser UI does goes through these endpoints."""
from __future__ import annotations

import datetime as dt
import os
import re
import shutil
import sqlite3
from pathlib import Path
from typing import Any, Literal

import cv2
import numpy as np
from fastapi import (APIRouter, Depends, File, Form, HTTPException, Query,
                     Request, Response, UploadFile, status)
from pydantic import BaseModel, Field

from vscan.appearance import DEFAULT_APPEARANCE_THRESHOLD
from vscan.events import arrivals, group_hits
from vscan.faces import DEFAULT_MATCH_THRESHOLD
from vscan.search import (appearance_at, enroll_appearance, enroll_from_faces,
                          enroll_from_video, find_objects, find_person,
                          find_person_appearance, load_clusters, search_vectors,
                          started_at_map)
from vscan.util import fmt_timecode
from vscan.video import grab_frame, probe

from .config import Settings, get_settings
from .engines import face_engine
from .jobs import JobRunner
from .media import (ensure_preview, image_response, open_index,
                    safe_index_file, stream_file)
from .security import (check_password_policy, clear_session_cookie, client_ip,
                       current_user, get_store, hash_password, login_throttle,
                       new_session_token, require_admin, require_analyst,
                       require_viewer, set_session_cookie, verify_password)
from .store import ROLES, Store

router = APIRouter(prefix="/api")
VIDEO_SUFFIXES = {".mp4", ".mkv", ".avi", ".mov", ".m4v", ".mpg", ".mpeg",
                  ".ts", ".webm", ".wmv", ".flv", ".dav", ".asf"}


def settings_dep(request: Request) -> Settings:
    return request.app.state.settings


def runner_dep(request: Request) -> JobRunner:
    return request.app.state.runner


def _user_dict(row: sqlite3.Row) -> dict:
    return {"id": row["id"], "username": row["username"], "role": row["role"],
            "active": bool(row["active"]), "created_at": row["created_at"],
            "last_login": row["last_login"]}


# ================================================================= auth
class LoginBody(BaseModel):
    username: str
    password: str


@router.post("/auth/login")
def login(body: LoginBody, request: Request, response: Response,
          store: Store = Depends(get_store),
          settings: Settings = Depends(settings_dep)) -> dict:
    ip = client_ip(request)
    wait = login_throttle.retry_after(body.username, ip)
    if wait:
        store.audit("auth.throttled", detail={"username": body.username,
                                              "retry_after": wait}, ip=ip)
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS,
                            f"too many failed attempts - try again in {wait}s",
                            headers={"Retry-After": str(wait)})
    user = store.user_by_name(body.username.strip())
    ok = user is not None and user["active"] and verify_password(
        body.password, user["password_hash"])
    if not ok:
        login_throttle.record_failure(body.username, ip)
        store.audit("auth.failed", detail={"username": body.username}, ip=ip)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "wrong username or password")
    login_throttle.clear(body.username, ip)
    token = new_session_token()
    store.create_session(token, int(user["id"]), settings.session_hours, ip,
                         request.headers.get("user-agent"))
    store.update_user(int(user["id"]),
                      last_login=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"))
    store.audit("auth.login", user=user, ip=ip)
    set_session_cookie(response, token, settings)
    return {"user": _user_dict(user)}


@router.post("/auth/logout")
def logout(request: Request, response: Response,
           store: Store = Depends(get_store)) -> dict:
    token = request.cookies.get("vscan_session")
    if token:
        user = store.session_user(token)
        store.delete_session(token)
        if user:
            store.audit("auth.logout", user=user, ip=client_ip(request))
    clear_session_cookie(response)
    return {"ok": True}


@router.get("/auth/me")
def me(user: sqlite3.Row = Depends(current_user),
       settings: Settings = Depends(settings_dep),
       store: Store = Depends(get_store)) -> dict:
    return {
        "user": _user_dict(user),
        "capabilities": {
            "ask": bool(store.get_setting("ask_enabled", settings.ask_enabled)),
            "footage_dirs": [str(p) for p in settings.footage_dirs],
            "uploads_dir": str(settings.uploads_dir.resolve()),
            "max_video_upload_mb": settings.max_video_upload_mb,
            "ask_key_set": bool(store.get_setting("anthropic_api_key")
                                or os.environ.get("ANTHROPIC_API_KEY")),
            "is_admin": user["role"] == "admin",
        },
    }


class PasswordBody(BaseModel):
    current_password: str
    new_password: str


@router.post("/auth/password")
def change_password(body: PasswordBody, request: Request,
                    user: sqlite3.Row = Depends(current_user),
                    store: Store = Depends(get_store)) -> dict:
    if not verify_password(body.current_password, user["password_hash"]):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "current password is wrong")
    check_password_policy(body.new_password)
    store.update_user(int(user["id"]), password_hash=hash_password(body.new_password))
    store.delete_user_sessions(int(user["id"]))
    store.audit("user.password_changed", user=user, ip=client_ip(request))
    return {"ok": True, "reauth_required": True}


# ================================================================= users
class UserBody(BaseModel):
    username: str
    password: str
    role: Literal["viewer", "analyst", "admin"] = "viewer"


class UserPatch(BaseModel):
    role: Literal["viewer", "analyst", "admin"] | None = None
    password: str | None = None
    active: bool | None = None


@router.get("/users")
def list_users(_: sqlite3.Row = Depends(require_admin),
               store: Store = Depends(get_store)) -> dict:
    return {"users": [_user_dict(u) for u in store.users()], "roles": list(ROLES)}


@router.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(body: UserBody, request: Request,
                admin: sqlite3.Row = Depends(require_admin),
                store: Store = Depends(get_store)) -> dict:
    username = body.username.strip()
    if not username:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "username is required")
    if store.user_by_name(username):
        raise HTTPException(status.HTTP_409_CONFLICT, "that username is taken")
    check_password_policy(body.password)
    user_id = store.create_user(username, hash_password(body.password), body.role)
    store.audit("user.created", user=admin,
                detail={"username": username, "role": body.role}, ip=client_ip(request))
    return {"user": _user_dict(store.user(user_id))}


@router.patch("/users/{user_id}")
def patch_user(user_id: int, body: UserPatch, request: Request,
               admin: sqlite3.Row = Depends(require_admin),
               store: Store = Depends(get_store)) -> dict:
    target = store.user(user_id)
    if target is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "no such user")
    demoting = (body.role and body.role != "admin") or body.active is False
    if target["role"] == "admin" and demoting and store.count_admins() <= 1:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            "this is the last active admin")
    fields: dict[str, Any] = {}
    if body.role:
        fields["role"] = body.role
    if body.active is not None:
        fields["active"] = int(body.active)
    if body.password:
        check_password_policy(body.password)
        fields["password_hash"] = hash_password(body.password)
    store.update_user(user_id, **fields)
    if body.password or body.active is False:
        store.delete_user_sessions(user_id)
    store.audit("user.updated", user=admin,
                detail={"username": target["username"], **{k: v for k, v in fields.items()
                                                           if k != "password_hash"}},
                ip=client_ip(request))
    return {"user": _user_dict(store.user(user_id))}


@router.delete("/users/{user_id}")
def delete_user(user_id: int, request: Request,
                admin: sqlite3.Row = Depends(require_admin),
                store: Store = Depends(get_store)) -> dict:
    target = store.user(user_id)
    if target is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "no such user")
    if target["role"] == "admin" and store.count_admins() <= 1:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "this is the last active admin")
    store.delete_user(user_id)
    store.audit("user.deleted", user=admin, detail={"username": target["username"]},
                ip=client_ip(request))
    return {"ok": True}


# ================================================================= footage
@router.get("/sources")
def sources(_: sqlite3.Row = Depends(require_viewer),
            settings: Settings = Depends(settings_dep)) -> dict:
    out = []
    for root in settings.footage_dirs:
        out.append({"path": str(root), "name": root.name or str(root),
                    "exists": root.is_dir(), "uploads": False})
    uploads = settings.uploads_dir.resolve()
    out.append({"path": str(uploads), "name": "uploads", "exists": uploads.is_dir(),
                "uploads": True})
    return {"sources": out}


@router.get("/sources/browse")
def browse(path: str = Query(""), _: sqlite3.Row = Depends(require_analyst),
           settings: Settings = Depends(settings_dep)) -> dict:
    target = (settings.resolve_footage(path) if path
              else settings.readable_roots[0])
    if not target.is_dir():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "not a directory")
    dirs, files = [], []
    for entry in sorted(target.iterdir(), key=lambda p: p.name.lower()):
        try:
            if entry.is_dir():
                dirs.append({"name": entry.name, "path": str(entry)})
            elif entry.suffix.lower() in VIDEO_SUFFIXES:
                files.append({"name": entry.name, "path": str(entry),
                              "bytes": entry.stat().st_size})
        except OSError:
            continue
    parent = None
    if any(root in target.parents for root in settings.readable_roots):
        parent = str(target.parent)
    return {"path": str(target), "parent": parent, "dirs": dirs, "files": files}


class IndexBody(BaseModel):
    paths: list[str]
    options: dict[str, Any] = Field(default_factory=dict)
    force: bool = False
    start_time: str | None = None


@router.post("/videos/index", status_code=status.HTTP_202_ACCEPTED)
def start_index(body: IndexBody, request: Request,
                user: sqlite3.Row = Depends(require_analyst),
                store: Store = Depends(get_store),
                runner: JobRunner = Depends(runner_dep),
                settings: Settings = Depends(settings_dep)) -> dict:
    if not body.paths:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "no files selected")
    resolved = []
    for raw in body.paths:
        path = settings.resolve_footage(raw)
        if path.is_dir():
            resolved += [str(f) for f in sorted(path.rglob("*"))
                         if f.is_file() and f.suffix.lower() in VIDEO_SUFFIXES]
        else:
            resolved.append(str(path))
    if not resolved:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "no video files in that selection")
    title = (f"Index {len(resolved)} file(s)" if len(resolved) > 1
             else f"Index {Path(resolved[0]).name}")
    job_id = runner.submit("index", title,
                           {"paths": resolved, "options": body.options,
                            "force": body.force, "start_time": body.start_time},
                           int(user["id"]))
    store.audit("footage.index_started", user=user,
                detail={"job_id": job_id, "files": len(resolved)}, ip=client_ip(request))
    return {"job_id": job_id, "files": len(resolved)}


_SAFE_NAME = re.compile(r"[^\w.\- ()\[\]\u0590-\u05FF]+", re.UNICODE)


def _upload_target(settings: Settings, filename: str) -> Path:
    """A safe, non-colliding path under the uploads folder."""
    name = _SAFE_NAME.sub("_", Path(filename or "video").name).strip() or "video"
    if Path(name).suffix.lower() not in VIDEO_SUFFIXES:
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"{name}: not a video file we can read "
            f"({', '.join(sorted(VIDEO_SUFFIXES))})")
    target = settings.uploads_dir / name
    stem, suffix = Path(name).stem, Path(name).suffix
    counter = 2
    while target.exists():
        target = settings.uploads_dir / f"{stem} ({counter}){suffix}"
        counter += 1
    return target


@router.post("/videos/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_video(request: Request,
                       file: UploadFile = File(...),
                       objects: bool = Form(True),
                       appearance: bool = Form(True),
                       sample_fps: float = Form(2.0),
                       user: sqlite3.Row = Depends(require_analyst),
                       store: Store = Depends(get_store),
                       runner: JobRunner = Depends(runner_dep),
                       settings: Settings = Depends(settings_dep)) -> dict:
    """Take a video straight from the browser and start indexing it.

    For the operator who has a file, not a mounted camera share: drag it in,
    and it lands in the uploads folder like any other recording.
    """
    target = _upload_target(settings, file.filename or "")
    limit = settings.max_video_upload_mb * 1024 * 1024
    written = 0
    try:
        with target.open("wb") as out:                 # streamed, never in memory
            while chunk := await file.read(1 << 20):
                written += len(chunk)
                if written > limit:
                    raise HTTPException(
                        status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        f"the file is larger than the {settings.max_video_upload_mb} MB "
                        "limit for uploads - point the server at the folder it "
                        "lives in instead")
                out.write(chunk)
    except HTTPException:
        target.unlink(missing_ok=True)
        raise
    except Exception:
        target.unlink(missing_ok=True)
        raise
    if written == 0:
        target.unlink(missing_ok=True)
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "the uploaded file was empty")

    job_id = runner.submit("index", f"Index {target.name}", {
        "paths": [str(target)],
        "options": {"sample_fps": sample_fps, "objects": objects,
                    "appearance": appearance},
    }, int(user["id"]))
    store.audit("footage.uploaded", user=user,
                detail={"name": target.name, "bytes": written, "job_id": job_id},
                ip=client_ip(request))
    return {"job_id": job_id, "name": target.name, "bytes": written}


@router.get("/videos")
def list_videos(_: sqlite3.Row = Depends(require_viewer),
                settings: Settings = Depends(settings_dep)) -> dict:
    with open_index(settings) as index:
        out = []
        for row in index.videos():
            counts = index.conn.execute(
                "SELECT (SELECT COUNT(*) FROM faces WHERE video_id=?) AS faces,"
                " (SELECT COUNT(*) FROM objects WHERE video_id=?) AS objects,"
                " (SELECT COUNT(*) FROM appearances WHERE video_id=?) AS appearances",
                (row["id"], row["id"], row["id"])).fetchone()
            out.append({
                "id": int(row["id"]), "path": row["path"], "name": Path(row["path"]).name,
                "duration": row["duration"], "duration_tc": fmt_timecode(row["duration"] or 0),
                "width": row["width"], "height": row["height"], "codec": row["codec"],
                "started_at": row["started_at"], "sample_fps": row["sample_fps"],
                "frames": row["frames_kept"], "indexed_at": row["indexed_at"],
                "faces": counts["faces"], "objects": counts["objects"],
                "appearances": counts["appearances"],
                "available": Path(row["path"]).exists(),
            })
    return {"videos": out}


@router.delete("/videos/{video_id}")
def delete_video(video_id: int, request: Request,
                 user: sqlite3.Row = Depends(require_analyst),
                 store: Store = Depends(get_store),
                 settings: Settings = Depends(settings_dep)) -> dict:
    with open_index(settings) as index:
        row = index.get_video(video_id)
        if row is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "no such video in the index")
        index.clear_video_data(video_id)
        index.conn.execute("DELETE FROM videos WHERE id = ?", (video_id,))
        index.commit()
        name = Path(row["path"]).name
    for folder in (settings.index_dir / "thumbs" / f"v{video_id}",
                   settings.index_dir / "crops" / f"v{video_id}"):
        shutil.rmtree(folder, ignore_errors=True)
    store.audit("footage.removed", user=user, detail={"video": name}, ip=client_ip(request))
    return {"ok": True}


# ================================================================= jobs
@router.get("/jobs")
def list_jobs(limit: int = Query(40, le=200), status_filter: str | None = Query(None, alias="status"),
              kind: str | None = None, _: sqlite3.Row = Depends(require_viewer),
              store: Store = Depends(get_store)) -> dict:
    return {"jobs": store.jobs(limit=limit, status=status_filter, kind=kind)}


@router.get("/jobs/{job_id}")
def get_job(job_id: int, _: sqlite3.Row = Depends(require_viewer),
            store: Store = Depends(get_store)) -> dict:
    job = store.job(job_id)
    if job is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "no such job")
    return {"job": job}


@router.post("/jobs/{job_id}/cancel")
def cancel_job(job_id: int, request: Request,
               user: sqlite3.Row = Depends(require_analyst),
               store: Store = Depends(get_store)) -> dict:
    job = store.job(job_id)
    if job is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "no such job")
    store.request_cancel(job_id)
    store.audit("job.cancelled", user=user, detail={"job_id": job_id}, ip=client_ip(request))
    return {"ok": True}


# ================================================================= persons
@router.get("/persons")
def list_persons(_: sqlite3.Row = Depends(require_viewer),
                 settings: Settings = Depends(settings_dep)) -> dict:
    with open_index(settings) as index:
        out = []
        for row in index.persons():
            refs = index.person_embeddings(int(row["id"]))
            crops = [r["crop"] for r in refs if r["crop"]]
            appearance = sum(1 for r in refs if r["kind"] == "appearance")
            out.append({"id": int(row["id"]), "name": row["name"],
                        "references": int(row["n_emb"]),
                        "face_references": int(row["n_emb"]) - appearance,
                        "appearance_references": appearance,
                        "created_at": row["created_at"],
                        "thumb": crops[0] if crops else None})
    return {"persons": out}


class PersonBody(BaseModel):
    name: str


@router.post("/persons", status_code=status.HTTP_201_CREATED)
def create_person(body: PersonBody, request: Request,
                  user: sqlite3.Row = Depends(require_analyst),
                  store: Store = Depends(get_store),
                  settings: Settings = Depends(settings_dep)) -> dict:
    name = body.name.strip()
    if not name:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "a name is required")
    with open_index(settings) as index:
        person_id = index.get_or_create_person(name)
    store.audit("person.created", user=user, detail={"name": name}, ip=client_ip(request))
    return {"person": {"id": person_id, "name": name, "references": 0}}


@router.delete("/persons/{person_id}")
def delete_person(person_id: int, request: Request,
                  user: sqlite3.Row = Depends(require_analyst),
                  store: Store = Depends(get_store),
                  settings: Settings = Depends(settings_dep)) -> dict:
    with open_index(settings) as index:
        row = index.conn.execute("SELECT * FROM persons WHERE id = ?",
                                 (person_id,)).fetchone()
        if row is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "no such person")
        index.delete_person(row["name"])
        name = row["name"]
    store.audit("person.deleted", user=user, detail={"name": name}, ip=client_ip(request))
    return {"ok": True}


@router.post("/persons/{person_id}/faces/upload")
async def enroll_upload(person_id: int, request: Request,
                        files: list[UploadFile] = File(...),
                        user: sqlite3.Row = Depends(require_analyst),
                        store: Store = Depends(get_store),
                        settings: Settings = Depends(settings_dep)) -> dict:
    limit = settings.max_upload_mb * 1024 * 1024
    added, skipped = 0, []
    with open_index(settings) as index:
        person = index.conn.execute("SELECT * FROM persons WHERE id = ?",
                                    (person_id,)).fetchone()
        if person is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "no such person")
        from vscan.search import _save_reference_crop

        for upload in files:
            raw = await upload.read(limit + 1)
            if len(raw) > limit:
                skipped.append(f"{upload.filename}: larger than {settings.max_upload_mb} MB")
                continue
            image = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
            if image is None:
                skipped.append(f"{upload.filename}: not a readable image")
                continue
            with face_engine() as engine:
                face = engine.best_face_of_image(image)
            if face is None or face.emb is None:
                skipped.append(f"{upload.filename}: no usable face found")
                continue
            crop = _save_reference_crop(index, person_id, image, face)
            index.add_person_embedding(person_id, face.emb,
                                       f"upload:{upload.filename}", crop)
            added += 1
        total = len(index.person_embeddings(person_id))
        name = person["name"]
    store.audit("person.enrolled", user=user,
                detail={"name": name, "added": added, "source": "upload"},
                ip=client_ip(request))
    return {"added": added, "skipped": skipped, "references": total}


class FromVideoBody(BaseModel):
    video_id: int
    times: list[float]


@router.post("/persons/{person_id}/faces/from-video")
def enroll_from_video_endpoint(person_id: int, body: FromVideoBody, request: Request,
                               user: sqlite3.Row = Depends(require_analyst),
                               store: Store = Depends(get_store),
                               settings: Settings = Depends(settings_dep)) -> dict:
    with open_index(settings) as index:
        person = index.conn.execute("SELECT * FROM persons WHERE id = ?",
                                    (person_id,)).fetchone()
        video = index.get_video(body.video_id)
        if person is None or video is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "no such person or video")
        with face_engine() as engine:
            added = enroll_from_video(index, engine, person["name"], video["path"],
                                      body.times)
        index.commit()
        total = len(index.person_embeddings(person_id))
        name = person["name"]
    store.audit("person.enrolled", user=user,
                detail={"name": name, "added": added, "source": "video",
                        "times": body.times}, ip=client_ip(request))
    return {"added": added, "references": total}


class FromClusterBody(BaseModel):
    cluster_id: int


@router.post("/persons/{person_id}/faces/from-cluster")
def enroll_from_cluster(person_id: int, body: FromClusterBody, request: Request,
                        user: sqlite3.Row = Depends(require_analyst),
                        store: Store = Depends(get_store),
                        settings: Settings = Depends(settings_dep)) -> dict:
    with open_index(settings) as index:
        person = index.conn.execute("SELECT * FROM persons WHERE id = ?",
                                    (person_id,)).fetchone()
        if person is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "no such person")
        try:
            clusters = load_clusters(index)
        except SystemExit as exc:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
        match = next((c for c in clusters if c["id"] == body.cluster_id), None)
        if match is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "no such cluster")
        added = enroll_from_faces(index, person["name"], match["face_ids"])
        total = len(index.person_embeddings(person_id))
        name = person["name"]
    store.audit("person.enrolled", user=user,
                detail={"name": name, "added": added, "source": "cluster",
                        "cluster": body.cluster_id}, ip=client_ip(request))
    return {"added": added, "references": total}


class AppearanceRefBody(BaseModel):
    video_id: int
    t: float
    box: list[float] | None = None


@router.post("/persons/{person_id}/appearance")
def enroll_appearance_endpoint(person_id: int, body: AppearanceRefBody, request: Request,
                               user: sqlite3.Row = Depends(require_analyst),
                               store: Store = Depends(get_store),
                               settings: Settings = Depends(settings_dep)) -> dict:
    """Save 'this is what they look like' from a moment in an indexed video."""
    with open_index(settings) as index:
        person = index.conn.execute("SELECT * FROM persons WHERE id = ?",
                                    (person_id,)).fetchone()
        if person is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "no such person")
        taken = appearance_at(index, body.video_id, body.t, body.box)
        if taken is None:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                                "no person could be read from that moment")
        emb, box = taken
        video = index.get_video(body.video_id)
        enroll_appearance(index, person["name"], emb,
                          f"video:{video['path']}@{fmt_timecode(body.t, ms=True)}")
        name = person["name"]
        total = len(index.person_embeddings(person_id, "appearance"))
    store.audit("person.enrolled", user=user,
                detail={"name": name, "source": "appearance", "t": body.t},
                ip=client_ip(request))
    return {"added": 1, "appearance_references": total, "box": box}


@router.get("/persons/{person_id}/faces")
def person_faces(person_id: int, _: sqlite3.Row = Depends(require_viewer),
                 settings: Settings = Depends(settings_dep)) -> dict:
    with open_index(settings) as index:
        rows = index.person_embeddings(person_id)
    return {"faces": [{"id": int(r["id"]), "source": r["source"], "crop": r["crop"]}
                      for r in rows]}


# ================================================================= search
class PersonSearch(BaseModel):
    person_id: int
    threshold: float = DEFAULT_MATCH_THRESHOLD
    min_sharpness: float = 0.0
    video_ids: list[int] | None = None
    start: float = 0.0
    end: float | None = None
    gap: float = 5.0
    min_hits: int = 1
    arrivals: bool = False
    absence: float = 300.0


class ObjectSearch(BaseModel):
    labels: list[str] = Field(default_factory=lambda: ["person"])
    min_score: float = 0.4
    video_ids: list[int] | None = None
    start: float = 0.0
    end: float | None = None
    gap: float = 5.0
    min_hits: int = 1
    arrivals: bool = False
    absence: float = 300.0


def _events_payload(events) -> dict:
    return {"events": [e.to_dict() for e in events], "count": len(events)}


@router.post("/search/person")
def search_person(body: PersonSearch, request: Request,
                  user: sqlite3.Row = Depends(require_viewer),
                  store: Store = Depends(get_store),
                  settings: Settings = Depends(settings_dep)) -> dict:
    with open_index(settings) as index:
        person = index.conn.execute("SELECT * FROM persons WHERE id = ?",
                                    (body.person_id,)).fetchone()
        if person is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "no such person")
        try:
            hits = find_person(index, person["name"], body.threshold, body.video_ids,
                               body.min_sharpness, body.start, body.end)
        except SystemExit as exc:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
        events = group_hits(hits, person["name"], body.gap, body.min_hits,
                            started_at_map(index))
        name = person["name"]
    if body.arrivals:
        events = arrivals(events, body.absence)
    store.audit("search.person", user=user,
                detail={"person": name, "threshold": body.threshold,
                        "results": len(events)}, ip=client_ip(request))
    return _events_payload(events)


@router.post("/search/objects")
def search_objects(body: ObjectSearch, request: Request,
                   user: sqlite3.Row = Depends(require_viewer),
                   store: Store = Depends(get_store),
                   settings: Settings = Depends(settings_dep)) -> dict:
    with open_index(settings) as index:
        hits = find_objects(index, body.labels, body.min_score, body.video_ids)
        hits = [h for h in hits
                if h.t >= body.start and (body.end is None or h.t <= body.end)]
        events = group_hits(hits, ", ".join(body.labels), body.gap, body.min_hits,
                            started_at_map(index))
    if body.arrivals:
        events = arrivals(events, body.absence)
    store.audit("search.objects", user=user,
                detail={"labels": body.labels, "results": len(events)},
                ip=client_ip(request))
    return _events_payload(events)


class AppearanceSearch(BaseModel):
    person_id: int
    threshold: float = DEFAULT_APPEARANCE_THRESHOLD
    video_ids: list[int] | None = None
    start: float = 0.0
    end: float | None = None
    gap: float = 5.0
    min_hits: int = 1
    arrivals: bool = False
    absence: float = 300.0


@router.post("/search/appearance")
def search_appearance(body: AppearanceSearch, request: Request,
                      user: sqlite3.Row = Depends(require_viewer),
                      store: Store = Depends(get_store),
                      settings: Settings = Depends(settings_dep)) -> dict:
    """Find someone by how they look, for the frames where no face is visible."""
    with open_index(settings) as index:
        person = index.conn.execute("SELECT * FROM persons WHERE id = ?",
                                    (body.person_id,)).fetchone()
        if person is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "no such person")
        try:
            hits = find_person_appearance(index, person["name"], body.threshold,
                                          body.video_ids, body.start, body.end)
        except SystemExit as exc:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
        events = group_hits(hits, person["name"], body.gap, body.min_hits,
                            started_at_map(index))
        name = person["name"]
    if body.arrivals:
        events = arrivals(events, body.absence)
    store.audit("search.appearance", user=user,
                detail={"person": name, "threshold": body.threshold,
                        "results": len(events)}, ip=client_ip(request))
    return _events_payload(events)


class SimilarSearch(BaseModel):
    video_id: int
    t: float
    box: list[float] | None = None
    threshold: float = DEFAULT_APPEARANCE_THRESHOLD
    video_ids: list[int] | None = None
    start: float = 0.0
    end: float | None = None
    gap: float = 5.0
    min_hits: int = 1
    arrivals: bool = False
    absence: float = 300.0


@router.post("/search/similar")
def search_similar(body: SimilarSearch, request: Request,
                   user: sqlite3.Row = Depends(require_viewer),
                   store: Store = Depends(get_store),
                   settings: Settings = Depends(settings_dep)) -> dict:
    """"Who else looks like this?" - starting from any moment in the footage."""
    with open_index(settings) as index:
        taken = appearance_at(index, body.video_id, body.t, body.box)
        if taken is None:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                                "no person could be read from that moment - "
                                "index this video with appearance vectors first")
        emb, box = taken
        hits = search_vectors(index, "appearances", emb, body.threshold,
                              body.video_ids, 0.0, body.start, body.end)
        label = f"looks like {fmt_timecode(body.t)}"
        events = group_hits(hits, label, body.gap, body.min_hits,
                            started_at_map(index))
    if body.arrivals:
        events = arrivals(events, body.absence)
    store.audit("search.similar", user=user,
                detail={"video_id": body.video_id, "t": body.t,
                        "results": len(events)}, ip=client_ip(request))
    payload = _events_payload(events)
    payload["box"] = box
    return payload


class AskBody(BaseModel):
    query: str
    video_ids: list[int] | None = None
    start: float = 0.0
    end: float | None = None
    max_frames: int = 400
    grid: int = 9
    min_confidence: float = 0.5
    confirm: bool = True
    min_activity: float = 0.0
    gap: float = 5.0
    min_hits: int = 1
    arrivals: bool = False
    absence: float = 300.0
    effort: Literal["low", "medium", "high", "xhigh", "max"] = "low"
    model: str | None = None


@router.post("/search/ask", status_code=status.HTTP_202_ACCEPTED)
def search_ask(body: AskBody, request: Request,
               user: sqlite3.Row = Depends(require_analyst),
               store: Store = Depends(get_store),
               runner: JobRunner = Depends(runner_dep),
               settings: Settings = Depends(settings_dep)) -> dict:
    if not store.get_setting("ask_enabled", settings.ask_enabled):
        raise HTTPException(status.HTTP_403_FORBIDDEN,
                            "natural-language search is switched off on this deployment")
    if not body.query.strip():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "a description is required")
    if not (store.get_setting("anthropic_api_key") or os.environ.get("ANTHROPIC_API_KEY")):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "no Claude API key is configured - an admin can add one under Settings")
    job_id = runner.submit("ask", f"Ask: {body.query[:60]}", body.model_dump(),
                           int(user["id"]))
    store.audit("search.ask", user=user,
                detail={"query": body.query, "job_id": job_id,
                        "max_frames": body.max_frames}, ip=client_ip(request))
    return {"job_id": job_id}


class ClusterBody(BaseModel):
    threshold: float = 0.45
    min_size: int = 3
    min_sharpness: float = 8.0
    video_ids: list[int] | None = None


@router.post("/cluster", status_code=status.HTTP_202_ACCEPTED)
def start_cluster(body: ClusterBody, request: Request,
                  user: sqlite3.Row = Depends(require_analyst),
                  store: Store = Depends(get_store),
                  runner: JobRunner = Depends(runner_dep)) -> dict:
    job_id = runner.submit("cluster", "Group unknown faces", body.model_dump(),
                           int(user["id"]))
    store.audit("cluster.started", user=user, detail={"job_id": job_id},
                ip=client_ip(request))
    return {"job_id": job_id}


@router.get("/clusters")
def get_clusters(limit: int = Query(200, le=1000),
                 _: sqlite3.Row = Depends(require_viewer),
                 settings: Settings = Depends(settings_dep)) -> dict:
    with open_index(settings) as index:
        try:
            clusters = load_clusters(index)
        except SystemExit:
            return {"clusters": [], "hint": "run face grouping first"}
        videos = {v["path"]: int(v["id"]) for v in index.videos()}
    out = []
    for c in clusters[:limit]:
        times = c.get("times") or []
        out.append({"id": c["id"], "size": c["size"], "crop": c.get("best_crop"),
                    "first_seen": times[0] if times else None,
                    "last_seen": times[-1] if times else None,
                    "videos": [{"name": Path(v).name, "id": videos.get(v)}
                               for v in c.get("videos", [])]})
    return {"clusters": out}


# ================================================================= export
class ExportBody(BaseModel):
    events: list[dict]
    pad: float = 3.0


@router.post("/export/clips", status_code=status.HTTP_202_ACCEPTED)
def export_clips(body: ExportBody, request: Request,
                 user: sqlite3.Row = Depends(require_analyst),
                 store: Store = Depends(get_store),
                 runner: JobRunner = Depends(runner_dep)) -> dict:
    if not body.events:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "nothing to export")
    job_id = runner.submit("export", f"Export {len(body.events)} clip(s)",
                           body.model_dump(), int(user["id"]))
    store.audit("export.clips", user=user,
                detail={"job_id": job_id, "clips": len(body.events)},
                ip=client_ip(request))
    return {"job_id": job_id}


@router.get("/export/file")
def export_file(path: str = Query(...), request: Request = None,
                user: sqlite3.Row = Depends(require_analyst),
                store: Store = Depends(get_store),
                settings: Settings = Depends(settings_dep)) -> Response:
    root = settings.exports_dir.resolve()
    target = (root / path).resolve()
    if root not in target.parents or not target.is_file():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "no such export")
    store.audit("export.downloaded", user=user, detail={"file": path},
                ip=client_ip(request) if request else None)
    response = stream_file(target, request)
    response.headers["Content-Disposition"] = f'attachment; filename="{target.name}"'
    return response


# ================================================================= media
@router.get("/media/thumb")
def media_thumb(path: str = Query(...), _: sqlite3.Row = Depends(require_viewer),
                settings: Settings = Depends(settings_dep)) -> Response:
    return image_response(safe_index_file(settings, path))


@router.get("/media/frame/{video_id}")
def media_frame(video_id: int, t: float = Query(0.0), width: int = Query(960, le=3840),
                _: sqlite3.Row = Depends(require_viewer),
                settings: Settings = Depends(settings_dep)) -> Response:
    with open_index(settings) as index:
        row = index.get_video(video_id)
        if row is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "no such video")
        path = row["path"]
    frame = grab_frame(path, t, width)
    if frame is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "could not decode that moment")
    ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
    if not ok:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "encoding failed")
    return Response(buf.tobytes(), media_type="image/jpeg",
                    headers={"Cache-Control": "private, max-age=600"})


@router.get("/media/preview/{video_id}")
def media_preview(video_id: int, request: Request, start: float = Query(0.0),
                  duration: float = Query(20.0, gt=0), width: int = Query(1280, le=1920),
                  _: sqlite3.Row = Depends(require_viewer),
                  settings: Settings = Depends(settings_dep)) -> Response:
    """A short, browser-playable transcode around a moment of interest."""
    with open_index(settings) as index:
        row = index.get_video(video_id)
        if row is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "no such video")
        source = Path(row["path"])
    settings.resolve_footage(source)
    if not source.exists():
        raise HTTPException(status.HTTP_410_GONE, "the source recording is not reachable")
    path, media_type = ensure_preview(settings, source, start, duration, width)
    return stream_file(path, request, media_type=media_type)


@router.get("/media/video/{video_id}")
def media_video(video_id: int, request: Request,
                _: sqlite3.Row = Depends(require_viewer),
                settings: Settings = Depends(settings_dep)) -> Response:
    with open_index(settings) as index:
        row = index.get_video(video_id)
        if row is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "no such video")
        path = Path(row["path"])
    settings.resolve_footage(path)          # never stream outside the mounted roots
    return stream_file(path, request)


# ================================================================= admin
@router.get("/audit")
def audit_log(limit: int = Query(200, le=1000), action: str | None = None,
              username: str | None = None, _: sqlite3.Row = Depends(require_admin),
              store: Store = Depends(get_store)) -> dict:
    return {"entries": store.audit_entries(limit, action, username)}


class SettingsPatch(BaseModel):
    ask_enabled: bool | None = None
    retention_days: int | None = None
    site_name: str | None = None
    default_index_options: dict[str, Any] | None = None
    anthropic_api_key: str | None = None


@router.get("/settings")
def read_settings(_: sqlite3.Row = Depends(require_viewer),
                  store: Store = Depends(get_store),
                  settings: Settings = Depends(settings_dep)) -> dict:
    return {
        "settings": {
            "ask_enabled": bool(store.get_setting("ask_enabled", settings.ask_enabled)),
            "retention_days": int(store.get_setting("retention_days",
                                                    settings.retention_days)),
            "site_name": store.get_setting("site_name", "vscan"),
            "default_index_options": store.get_setting("default_index_options", {}),
            # the key itself is never sent back - only whether one is stored
            "ask_key_set": bool(store.get_setting("anthropic_api_key")
                                or os.environ.get("ANTHROPIC_API_KEY")),
            "ask_key_source": ("settings" if store.get_setting("anthropic_api_key")
                               else "environment" if os.environ.get("ANTHROPIC_API_KEY")
                               else None),
        },
        "deployment": {
            "data_dir": str(settings.data_dir),
            "footage_dirs": [str(p) for p in settings.footage_dirs],
            "workers": settings.workers,
            "session_hours": settings.session_hours,
        },
    }


@router.patch("/settings")
def patch_settings(body: SettingsPatch, request: Request,
                   admin: sqlite3.Row = Depends(require_admin),
                   store: Store = Depends(get_store)) -> dict:
    changed = {}
    for key, value in body.model_dump(exclude_none=True).items():
        store.set_setting(key, value.strip() if key == "anthropic_api_key" else value)
        # never write a credential into the audit trail
        changed[key] = "(set)" if key == "anthropic_api_key" and value else value
    store.audit("settings.updated", user=admin, detail=changed, ip=client_ip(request))
    return {"ok": True, "changed": changed}


class PurgeBody(BaseModel):
    older_than_days: int | None = None
    everything: bool = False


@router.post("/maintenance/purge")
def purge(body: PurgeBody, request: Request,
          admin: sqlite3.Row = Depends(require_admin),
          store: Store = Depends(get_store),
          settings: Settings = Depends(settings_dep)) -> dict:
    """Delete indexed biometric data. Retention is a legal requirement, not a nicety."""
    removed = []
    with open_index(settings) as index:
        rows = index.videos()
        cutoff = None
        if not body.everything:
            days = body.older_than_days
            if days is None:
                days = int(store.get_setting("retention_days", settings.retention_days))
            if not days:
                raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                    "set a retention period or pass older_than_days")
            cutoff = dt.datetime.now() - dt.timedelta(days=days)
        for row in rows:
            if cutoff is not None:
                try:
                    indexed_at = dt.datetime.fromisoformat(row["indexed_at"])
                except (TypeError, ValueError):
                    continue
                if indexed_at >= cutoff:
                    continue
            video_id = int(row["id"])
            index.clear_video_data(video_id)
            index.conn.execute("DELETE FROM videos WHERE id = ?", (video_id,))
            removed.append(Path(row["path"]).name)
            for folder in (settings.index_dir / "thumbs" / f"v{video_id}",
                           settings.index_dir / "crops" / f"v{video_id}"):
                shutil.rmtree(folder, ignore_errors=True)
        if body.everything:
            index.conn.execute("DELETE FROM person_embeddings")
            index.conn.execute("DELETE FROM persons")
        index.commit()
    store.audit("maintenance.purge", user=admin,
                detail={"videos": removed, "everything": body.everything},
                ip=client_ip(request))
    return {"removed": removed, "count": len(removed)}


@router.get("/stats")
def stats(_: sqlite3.Row = Depends(require_viewer),
          store: Store = Depends(get_store),
          settings: Settings = Depends(settings_dep)) -> dict:
    with open_index(settings) as index:
        index_stats = index.stats()
        total_seconds = index.conn.execute(
            "SELECT COALESCE(SUM(duration), 0) AS d FROM videos").fetchone()["d"]
    running = store.jobs(limit=200, status="running")
    queued = store.jobs(limit=200, status="queued")
    return {"index": index_stats,
            "footage_hours": round((total_seconds or 0) / 3600, 2),
            "jobs": {"running": len(running), "queued": len(queued)}}


@router.get("/health")
def health() -> dict:
    return {"ok": True}
