"""Job handlers: the long-running work, wired to the vscan engine."""
from __future__ import annotations

import datetime as dt
from pathlib import Path

from vscan.events import arrivals, group_hits
from vscan.indexer import IndexOptions, Indexer
from vscan.search import cluster_faces, save_clusters, started_at_map
from vscan.util import fmt_timecode
from vscan.video import extract_clip

from .config import Settings
from .jobs import INDEX_WRITE_LOCK, JobContext
from .media import open_index


def index_options(settings: Settings, raw: dict) -> IndexOptions:
    labels = tuple(raw.get("labels") or ("person",))
    if "all" in labels:
        labels = ()
    return IndexOptions(
        sample_fps=float(raw.get("sample_fps", 2.0)),
        max_width=int(raw.get("width", 1280)),
        motion_threshold=float(raw.get("motion", 0.004)),
        detect_faces=bool(raw.get("faces", True)),
        detect_objects=bool(raw.get("objects", False)),
        object_labels=labels,
        object_conf=float(raw.get("object_conf", 0.4)),
        detect_appearance=bool(raw.get("appearance", False)),
        appearance_every=float(raw.get("appearance_every", 1.5)),
        thumbs=bool(raw.get("thumbs", True)),
        thumb_width=int(raw.get("thumb_width", 480)),
        start=float(raw.get("start", 0.0)),
        end=float(raw["end"]) if raw.get("end") else None,
    )


def make_index_handler(settings: Settings):
    def handle(ctx: JobContext, params: dict) -> dict:
        paths = [settings.resolve_footage(p) for p in params.get("paths", [])]
        opts = index_options(settings, params.get("options") or {})
        force = bool(params.get("force"))
        started_override = params.get("start_time")

        summary = []
        from vscan.vectors import clear_caches

        with INDEX_WRITE_LOCK, open_index(settings) as index:
            indexer = Indexer(index, opts)
            for i, path in enumerate(paths):
                ctx.progress(i / max(1, len(paths)), f"indexing {path.name}")
                base = i / max(1, len(paths))
                span = 1.0 / max(1, len(paths))
                stats = indexer.run(
                    path, force=force, progress=False,
                    on_progress=lambda f, m, b=base, s=span: ctx.progress(b + f * s, m),
                    should_cancel=lambda: ctx.cancelled)
                if started_override:
                    row = index.find_video(path)
                    if row:
                        index.conn.execute(
                            "UPDATE videos SET started_at = ? WHERE id = ?",
                            (started_override, row["id"]))
                        index.commit()
                row = index.find_video(path)
                entry = {
                    "video_id": int(row["id"]) if row else None,
                    "name": path.name,
                    "frames": stats.frames_kept,
                    "faces": stats.faces,
                    "objects": stats.objects,
                    "appearances": stats.appearances,
                    "seconds": round(stats.seconds, 1),
                }
                if stats.faces == 0 and stats.objects == 0 and not ctx.cancelled:
                    # A silent zero is the worst answer a search tool can give.
                    # Work out why before the operator has to ask.
                    entry["diagnosis"] = _diagnose(path, ctx)
                summary.append(entry)
                ctx.check_cancel()
            clear_caches(index.root)          # new vectors, stale search matrix
        return {"videos": summary,
                "totals": {k: sum(v[k] for v in summary)
                           for k in ("frames", "faces", "objects", "appearances")}}

    return handle


def _diagnose(path: Path, ctx: JobContext) -> list[dict]:
    """Explain an empty result: no people, faces too small, too dark, ..."""
    from vscan.doctor import examine

    ctx.progress(message=f"{path.name}: nothing found - checking why")
    try:
        report = examine(path, samples=24)
    except Exception as exc:                      # never fail the job over this
        return [{"ok": False, "headline": "could not analyse the footage",
                 "detail": str(exc)}]
    return [{"ok": v.ok, "headline": v.headline, "detail": v.detail}
            for v in report.verdicts]


def make_cluster_handler(settings: Settings):
    def handle(ctx: JobContext, params: dict) -> dict:
        ctx.progress(0.1, "loading face vectors")
        with open_index(settings) as index:
            clusters = cluster_faces(
                index,
                video_ids=params.get("video_ids") or None,
                threshold=float(params.get("threshold", 0.45)),
                min_sharpness=float(params.get("min_sharpness", 8.0)),
                min_size=int(params.get("min_size", 3)))
            ctx.progress(0.9, f"{len(clusters)} cluster(s) found")
            save_clusters(index, clusters)
        return {"clusters": len(clusters),
                "faces": sum(c["size"] for c in clusters)}

    return handle


def make_ask_handler(settings: Settings):
    def handle(ctx: JobContext, params: dict) -> dict:
        from vscan.semantic import AskOptions, ask, select_frames

        if not ctx.store.get_setting("ask_enabled", settings.ask_enabled):
            raise RuntimeError("natural-language search is switched off in Settings")
        api_key = ctx.store.get_setting("anthropic_api_key") or None

        opts = AskOptions(
            model=params.get("model") or AskOptions.model,
            grid=int(params.get("grid", 9)),
            max_frames=int(params.get("max_frames", 400)),
            min_confidence=float(params.get("min_confidence", 0.5)),
            confirm=bool(params.get("confirm", True)),
            concurrency=int(params.get("concurrency", 4)),
            effort=params.get("effort", "low"),
        )
        with open_index(settings) as index:
            refs = select_frames(
                index, params.get("video_ids") or None,
                float(params.get("start", 0.0)),
                float(params["end"]) if params.get("end") else None,
                float(params.get("min_activity", 0.0)), opts.max_frames)
            starts = started_at_map(index)

        ctx.progress(0.02, f"{len(refs)} frame(s) selected")
        result = ask(params["query"], refs, opts,
                     on_progress=lambda f, m: ctx.progress(0.02 + f * 0.95, m),
                     should_cancel=lambda: ctx.cancelled, api_key=api_key)
        events = group_hits(result.hits, params["query"],
                            float(params.get("gap", 5.0)),
                            int(params.get("min_hits", 1)), starts)
        if params.get("arrivals"):
            events = arrivals(events, float(params.get("absence", 300.0)))
        return {
            "events": [e.to_dict() for e in events],
            "frames_examined": result.frames_examined,
            "requests": result.requests,
            "refusals": result.refusals,
        }

    return handle


def make_export_handler(settings: Settings):
    def handle(ctx: JobContext, params: dict) -> dict:
        events = params.get("events") or []
        pad = float(params.get("pad", 3.0))
        stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        out_dir = settings.exports_dir / f"export-{stamp}-job{ctx.job_id}"
        out_dir.mkdir(parents=True, exist_ok=True)

        with open_index(settings) as index:
            videos = {int(v["id"]): v["path"] for v in index.videos()}

        files = []
        for i, event in enumerate(events, 1):
            ctx.progress(i / max(1, len(events)), f"cutting clip {i} of {len(events)}")
            source = videos.get(int(event["video_id"]))
            if not source:
                continue
            name = (f"{i:03d}_{Path(source).stem}_"
                    f"{fmt_timecode(float(event['start'])).replace(':', '-')}.mp4")
            try:
                path = extract_clip(source, float(event["start"]), float(event["end"]),
                                    out_dir / name, pad)
            except Exception as exc:                       # keep going on one bad cut
                ctx.progress(message=f"clip {i} failed: {exc}")
                continue
            files.append({"name": path.name,
                          "path": str(path.relative_to(settings.exports_dir)),
                          "bytes": path.stat().st_size})
        return {"directory": out_dir.name, "files": files}

    return handle


def register_all(runner, settings: Settings) -> None:
    runner.register("index", make_index_handler(settings))
    runner.register("cluster", make_cluster_handler(settings))
    runner.register("ask", make_ask_handler(settings))
    runner.register("export", make_export_handler(settings))
