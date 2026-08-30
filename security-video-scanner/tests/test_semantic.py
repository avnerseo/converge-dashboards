"""The Claude-powered 'ask' path, exercised against a stubbed API client."""
from __future__ import annotations

import json
from types import SimpleNamespace

import numpy as np
import pytest

from vscan import semantic
from vscan.semantic import AskOptions, FrameRef, ask, build_grid


def _blocks(payload: dict):
    return SimpleNamespace(
        stop_reason="end_turn", stop_details=None,
        content=[SimpleNamespace(type="text", text=json.dumps(payload))])


class FakeMessages:
    def __init__(self, replies, log):
        self._replies, self._log = replies, log

    def create(self, **kwargs):
        self._log.append(kwargs)
        payload = self._replies(kwargs)
        return _blocks(payload)


class FakeClient:
    def __init__(self, replies):
        self.calls: list[dict] = []
        self.messages = FakeMessages(replies, self.calls)
        # force the plain (non-beta) path so the stub stays small
        self.beta = SimpleNamespace(messages=SimpleNamespace(
            create=lambda **kw: (_ for _ in ()).throw(TypeError("no beta here"))))


@pytest.fixture(autouse=True)
def _reset_fallback_flag():
    semantic._use_fallbacks = True
    yield
    semantic._use_fallbacks = True


def _refs(n: int) -> list[FrameRef]:
    return [FrameRef(1, "/f/cam.mp4", float(i)) for i in range(n)]


def _fake_frame_loader(monkeypatch, colour=200):
    monkeypatch.setattr(semantic, "_load",
                        lambda ref, max_width=0: np.full((90, 160, 3), colour, np.uint8))


def test_build_grid_tiles_and_labels():
    imgs = [np.full((90, 160, 3), 10 * i, np.uint8) for i in range(1, 6)]
    sheet = build_grid(imgs, ["00:00:01"] * 5, list(range(5)), cell_width=160)
    assert sheet.shape[1] == 3 * 160          # 5 frames -> 3 columns
    assert sheet.shape[0] == 2 * 90           # ... 2 rows


def test_ask_triages_then_confirms(monkeypatch):
    _fake_frame_loader(monkeypatch)
    import vscan.video
    monkeypatch.setattr(vscan.video, "grab_frame",
                        lambda path, t, width=0: np.full((90, 160, 3), 200, np.uint8))

    def replies(kwargs):
        schema = kwargs["output_config"]["format"]["schema"]
        if "matches" in schema["properties"]:                 # triage grid
            return {"matches": [{"frame": 0, "confidence": 0.9, "note": "a box"},
                                {"frame": 1, "confidence": 0.2, "note": "unsure"}]}
        return {"match": True, "confidence": 0.85, "note": "confirmed box"}

    client = FakeClient(replies)
    monkeypatch.setattr(semantic, "_client", lambda: client)

    result = ask("someone carrying a box", _refs(4),
                 AskOptions(grid=4, concurrency=1))

    assert [h.t for h in result.hits] == [0.0]                # 0.2 dropped by threshold
    assert result.hits[0].meta["stage"] == "confirmed"
    assert result.hits[0].score == pytest.approx(0.85)
    assert result.requests == 2                               # 1 grid + 1 confirmation

    first = client.calls[0]
    assert first["model"] == semantic.DEFAULT_MODEL
    assert first["thinking"] == {"type": "adaptive"}
    assert first["output_config"]["format"]["type"] == "json_schema"
    assert first["messages"][0]["content"][0]["source"]["media_type"] == "image/jpeg"


def test_ask_without_confirm_keeps_triage_scores(monkeypatch):
    _fake_frame_loader(monkeypatch)
    client = FakeClient(lambda kw: {"matches": [{"frame": 2, "confidence": 0.7,
                                                 "note": "van"}]})
    monkeypatch.setattr(semantic, "_client", lambda: client)
    result = ask("a van", _refs(3), AskOptions(grid=3, confirm=False,
                                                     concurrency=1))
    assert [h.t for h in result.hits] == [2.0]
    assert result.hits[0].meta["stage"] == "triage"


def test_ask_handles_refusal(monkeypatch):
    _fake_frame_loader(monkeypatch)

    class Refusing(FakeClient):
        def __init__(self):
            super().__init__(lambda kw: {})
            self.messages.create = lambda **kw: SimpleNamespace(
                stop_reason="refusal",
                stop_details=SimpleNamespace(category="privacy"), content=[])

    monkeypatch.setattr(semantic, "_client", Refusing)
    result = ask("anything", _refs(2), AskOptions(grid=2, concurrency=1))
    assert result.hits == [] and result.refusals == 1


def test_ask_dry_run_makes_no_calls(monkeypatch):
    called = []
    monkeypatch.setattr(semantic, "_client", lambda: called.append(1))
    result = ask("q", _refs(5), AskOptions(dry_run=True))
    assert not called and result.requests == 0
