"""API tests: auth, roles, jobs, search, media and the audit trail."""
from __future__ import annotations

import os
import shutil
import time
from pathlib import Path

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("cv2")

from fastapi.testclient import TestClient          # noqa: E402

from vscan_server.app import create_app                  # noqa: E402
from vscan_server.config import Settings, set_settings   # noqa: E402

ADMIN_PASSWORD = "test-admin-password"
FACES = [Path(p) for p in os.environ.get("VSCAN_TEST_FACES", "").split(":") if p]
HAS_FACES = len(FACES) >= 2 and all(f.exists() for f in FACES)
HAS_FFMPEG = bool(shutil.which("ffmpeg"))


@pytest.fixture(scope="module")
def footage(tmp_path_factory) -> Path:
    """A footage root with one short clip in it (empty file if we have no faces)."""
    root = tmp_path_factory.mktemp("footage")
    if HAS_FACES and HAS_FFMPEG:
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from make_sample_video import build
        build(FACES[:2], root / "cam1.mp4", seconds=14, fps=10)
    return root


@pytest.fixture(scope="module")
def client(tmp_path_factory, footage, monkeypatch_module) -> TestClient:
    data_dir = tmp_path_factory.mktemp("data")
    monkeypatch_module.setenv("VSCAN_DATA_DIR", str(data_dir))
    monkeypatch_module.setenv("VSCAN_FOOTAGE_DIRS", str(footage))
    monkeypatch_module.setenv("VSCAN_ADMIN_PASSWORD", ADMIN_PASSWORD)
    monkeypatch_module.setenv("VSCAN_WORKERS", "1")
    settings = set_settings(Settings())
    with TestClient(create_app(settings)) as test_client:
        yield test_client


@pytest.fixture(scope="module")
def monkeypatch_module():
    from _pytest.monkeypatch import MonkeyPatch
    mp = MonkeyPatch()
    yield mp
    mp.undo()


def login(client: TestClient, username: str = "admin",
          password: str = ADMIN_PASSWORD) -> None:
    response = client.post("/api/auth/login",
                           json={"username": username, "password": password})
    assert response.status_code == 200, response.text


def wait_for_job(client: TestClient, job_id: int, timeout: float = 180.0) -> dict:
    deadline = time.time() + timeout
    while time.time() < deadline:
        job = client.get(f"/api/jobs/{job_id}").json()["job"]
        if job["status"] in ("done", "failed", "cancelled"):
            return job
        time.sleep(0.25)
    raise AssertionError(f"job {job_id} did not finish within {timeout}s")


# ------------------------------------------------------------------- auth
def test_health_needs_no_session(client):
    assert client.get("/api/health").json() == {"ok": True}


def test_api_is_closed_without_a_session(client):
    client.cookies.clear()
    assert client.get("/api/videos").status_code == 401
    assert client.get("/api/users").status_code == 401


def test_login_rejects_a_wrong_password(client):
    from vscan_server.security import login_throttle
    login_throttle.reset()
    client.cookies.clear()
    assert client.post("/api/auth/login",
                       json={"username": "admin", "password": "nope"}).status_code == 401


def test_repeated_wrong_passwords_are_throttled(client):
    from vscan_server.security import login_throttle
    login_throttle.reset()
    client.cookies.clear()
    for _ in range(5):
        assert client.post("/api/auth/login",
                           json={"username": "admin", "password": "nope"}).status_code == 401
    blocked = client.post("/api/auth/login",
                          json={"username": "admin", "password": ADMIN_PASSWORD})
    assert blocked.status_code == 429
    assert int(blocked.headers["retry-after"]) > 0
    login_throttle.reset()                       # release the brake for later tests


def test_login_and_me(client):
    login(client)
    body = client.get("/api/auth/me").json()
    assert body["user"]["username"] == "admin"
    assert body["user"]["role"] == "admin"


def test_bootstrap_created_exactly_one_admin(client):
    login(client)
    users = client.get("/api/users").json()["users"]
    assert [u["username"] for u in users] == ["admin"]


# ------------------------------------------------------------------ users
def test_admin_creates_users_and_roles_are_enforced(client):
    login(client)
    assert client.post("/api/users", json={"username": "vera", "password": "short",
                                           "role": "viewer"}).status_code == 400
    for name, role in (("vera", "viewer"), ("anna", "analyst")):
        response = client.post("/api/users", json={"username": name,
                                                   "password": "a-good-password",
                                                   "role": role})
        assert response.status_code == 201, response.text
    assert client.post("/api/users", json={"username": "vera",
                                           "password": "a-good-password"}).status_code == 409

    login(client, "vera", "a-good-password")
    assert client.get("/api/videos").status_code == 200          # viewer can read
    assert client.get("/api/users").status_code == 403           # ... but not admin
    assert client.post("/api/cluster", json={}).status_code == 403

    login(client, "anna", "a-good-password")
    assert client.post("/api/cluster", json={}).status_code == 202   # analyst can
    assert client.get("/api/audit").status_code == 403
    login(client)


def test_last_admin_cannot_be_removed(client):
    login(client)
    admin_id = next(u["id"] for u in client.get("/api/users").json()["users"]
                    if u["username"] == "admin")
    assert client.delete(f"/api/users/{admin_id}").status_code == 400
    assert client.patch(f"/api/users/{admin_id}",
                        json={"role": "viewer"}).status_code == 400


def test_password_change_invalidates_sessions(client):
    login(client, "vera", "a-good-password")
    response = client.post("/api/auth/password",
                           json={"current_password": "a-good-password",
                                 "new_password": "another-good-password"})
    assert response.status_code == 200
    assert client.get("/api/auth/me").status_code == 401         # old cookie is dead
    login(client, "vera", "another-good-password")
    login(client)


# ---------------------------------------------------------------- footage
def test_browse_stays_inside_the_configured_roots(client, footage):
    login(client)
    listing = client.get("/api/sources/browse").json()
    assert listing["path"] == str(footage)
    assert client.get("/api/sources/browse", params={"path": "/etc"}).status_code == 403


def test_index_refuses_paths_outside_the_roots(client):
    login(client)
    assert client.post("/api/videos/index",
                       json={"paths": ["/etc/passwd"]}).status_code == 403
    assert client.post("/api/videos/index", json={"paths": []}).status_code == 400


@pytest.mark.skipif(not (HAS_FACES and HAS_FFMPEG),
                    reason="set VSCAN_TEST_FACES=a.jpg:b.jpg and install ffmpeg")
def test_full_flow_index_cluster_enroll_search(client, footage):
    login(client)
    start = client.post("/api/videos/index", json={
        "paths": [str(footage / "cam1.mp4")],
        "options": {"sample_fps": 3, "objects": True}})
    assert start.status_code == 202, start.text
    job = wait_for_job(client, start.json()["job_id"])
    assert job["status"] == "done", job
    assert job["result"]["totals"]["faces"] > 0

    videos = client.get("/api/videos").json()["videos"]
    assert len(videos) == 1 and videos[0]["frames"] > 0
    video_id = videos[0]["id"]

    # a frame and a byte range of the video itself come back
    assert client.get(f"/api/media/frame/{video_id}",
                      params={"t": 4.0}).headers["content-type"] == "image/jpeg"
    ranged = client.get(f"/api/media/video/{video_id}", headers={"Range": "bytes=0-1023"})
    assert ranged.status_code == 206 and len(ranged.content) == 1024

    # group faces, then turn one group into a named person
    cluster_job = wait_for_job(client, client.post(
        "/api/cluster", json={"min_size": 2}).json()["job_id"])
    assert cluster_job["status"] == "done"
    clusters = client.get("/api/clusters").json()["clusters"]
    assert len(clusters) == 2, clusters

    person_id = client.post("/api/persons",
                            json={"name": "Person A"}).json()["person"]["id"]
    enrolled = client.post(f"/api/persons/{person_id}/faces/from-cluster",
                           json={"cluster_id": clusters[0]["id"]}).json()
    assert enrolled["added"] > 0

    found = client.post("/api/search/person", json={"person_id": person_id}).json()
    assert found["count"] == 1
    event = found["events"][0]
    assert event["video_id"] == video_id and event["duration"] > 0

    objects = client.post("/api/search/objects",
                          json={"labels": ["person"], "gap": 3}).json()
    assert objects["count"] >= 1

    # a browser-playable preview is transcoded on demand
    preview = client.get(f"/api/media/preview/{video_id}",
                         params={"start": 3.0, "duration": 4.0})
    assert preview.status_code in (200, 206), preview.text
    assert preview.headers["content-type"] in ("video/mp4", "video/webm")
    assert len(preview.content) > 1000

    # thumbnails referenced by results are actually served
    thumb = event.get("best_thumb")
    if thumb:
        assert client.get("/api/media/thumb", params={"path": thumb}).status_code == 200
    assert client.get("/api/media/thumb",
                      params={"path": "../../etc/passwd"}).status_code == 400


@pytest.mark.skipif(not (HAS_FACES and HAS_FFMPEG), reason="needs the indexed flow")
def test_enroll_from_uploaded_photo(client):
    login(client)
    person_id = client.post("/api/persons",
                            json={"name": "From Photo"}).json()["person"]["id"]
    with FACES[0].open("rb") as fh:
        response = client.post(f"/api/persons/{person_id}/faces/upload",
                               files={"files": (FACES[0].name, fh, "image/jpeg")})
    assert response.status_code == 200, response.text
    assert response.json()["added"] == 1
    assert client.post("/api/search/person",
                       json={"person_id": person_id}).json()["count"] == 1


# ------------------------------------------------------------------ admin
def test_ask_is_refused_when_switched_off(client):
    login(client)
    assert client.patch("/api/settings", json={"ask_enabled": False}).status_code == 200
    assert client.post("/api/search/ask", json={"query": "anything"}).status_code == 403
    client.patch("/api/settings", json={"ask_enabled": True})


def test_audit_trail_records_searches_and_logins(client):
    login(client)
    entries = client.get("/api/audit").json()["entries"]
    actions = {e["action"] for e in entries}
    assert "auth.login" in actions
    assert "auth.failed" in actions
    assert "user.created" in actions
    assert any(e["username"] == "admin" for e in entries)


def test_purge_needs_a_retention_window(client):
    login(client)
    assert client.post("/api/maintenance/purge", json={}).status_code == 400
    response = client.post("/api/maintenance/purge", json={"older_than_days": 3650})
    assert response.status_code == 200 and response.json()["count"] == 0
