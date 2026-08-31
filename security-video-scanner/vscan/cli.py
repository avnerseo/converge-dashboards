"""vscan command line: index footage, then search it by face or by instruction."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .db import Index
from .events import Event, arrivals, group_hits
from .zones import MODES as ZONE_MODES
from .util import LOG, fmt_timecode, human_size, parse_datetime, parse_timecode, setup_logging

VIDEO_SUFFIXES = {".mp4", ".mkv", ".avi", ".mov", ".m4v", ".mpg", ".mpeg",
                  ".ts", ".webm", ".wmv", ".flv", ".dav", ".asf"}
DEFAULT_INDEX = "vscan-index"


# --------------------------------------------------------------- arg parsing
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="vscan",
        description="Search security-camera footage: who appeared and when, "
                    "or anything else you can describe in words.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""examples:
  vscan index recordings/*.mp4 --objects
  vscan enroll --name "David" photos/david*.jpg
  vscan find --person "David" --arrivals --report david.html
  vscan cluster --report faces.html          # who appears at all?
  vscan label --cluster 0 --name "Courier"
  vscan ask "someone carrying a large box to the front door" --report box.html
  vscan doctor gate.mp4                      # can this camera even be searched?
  vscan similar --video gate --at 00:03:12   # who else looks like that person?
  vscan zone add --video gate --name "front door" --box 0.42,0.30,0.14,0.38
  vscan zone scan --name "front door"        # when did that door open?
  vscan line add --video gate --name "gate" --line 0.5,0.1,0.5,0.9
  vscan line scan --name "gate" --direction out   # who left through it?
""")
    p.add_argument("--version", action="version", version=f"vscan {__version__}")
    p.add_argument("-v", "--verbose", action="store_true")
    p.add_argument("--index", default=DEFAULT_INDEX, metavar="DIR",
                   help=f"index directory (default: ./{DEFAULT_INDEX})")
    sub = p.add_subparsers(dest="command", required=True)

    # ---- index
    s = sub.add_parser("index", help="scan video files into the index")
    s.add_argument("paths", nargs="+", help="video files or directories")
    s.add_argument("--fps", type=float, default=2.0, dest="sample_fps",
                   help="frames sampled per second of footage (default: 2)")
    s.add_argument("--width", type=int, default=1280, help="analysis width in px")
    s.add_argument("--motion", type=float, default=0.004, dest="motion_threshold",
                   help="fraction of pixels that must change to call a frame active; "
                        "0 disables the motion gate")
    s.add_argument("--keyframe", type=float, default=10.0, dest="keyframe_every",
                   metavar="SEC",
                   help="keep a frame this often even when nothing moved, so the "
                        "state of the scene is on record for zone searches "
                        "(default: 10; 0 disables)")
    s.add_argument("--no-faces", action="store_true", help="skip face detection")
    s.add_argument("--objects", action="store_true",
                   help="also run object detection (YOLOX, 80 COCO classes)")
    s.add_argument("--labels", nargs="*", default=["person"],
                   help="object labels to keep (default: person; 'all' for everything)")
    s.add_argument("--object-conf", type=float, default=0.4)
    s.add_argument("--appearance", action="store_true",
                   help="also store appearance (re-id) vectors for each person, so "
                        "they can be found when their face is not visible")
    s.add_argument("--appearance-every", type=float, default=1.5, metavar="SEC",
                   help="seconds between appearance vectors of the same person")
    s.add_argument("--no-thumbs", action="store_true",
                   help="do not store frame thumbnails (disables 'ask' and reports)")
    s.add_argument("--thumb-width", type=int, default=480)
    s.add_argument("--from", dest="start", default="0", metavar="TC")
    s.add_argument("--to", dest="end", default=None, metavar="TC")
    s.add_argument("--start-time", default=None,
                   help="wall-clock time of the first frame, e.g. '2026-08-30 14:00:00'")
    s.add_argument("--force", action="store_true", help="re-index already indexed files")
    s.add_argument("--offline", action="store_true", help="never download models")
    s.add_argument("-r", "--recursive", action="store_true",
                   help="descend into directories")

    # ---- videos
    sub.add_parser("videos", help="list what is in the index")

    # ---- enroll / persons
    s = sub.add_parser("enroll", help="teach vscan a person's face")
    s.add_argument("images", nargs="*", help="portrait images of the person")
    s.add_argument("--name", required=True)
    s.add_argument("--from-video", metavar="VIDEO",
                   help="take reference faces out of a video instead of stills")
    s.add_argument("--at", action="append", default=[], metavar="TC",
                   help="timecode in --from-video (repeatable)")
    s.add_argument("--offline", action="store_true")

    sub.add_parser("persons", help="list enrolled people")
    s = sub.add_parser("forget", help="delete an enrolled person")
    s.add_argument("--name", required=True)

    # ---- find
    s = sub.add_parser("find", help="find when a known person appears")
    s.add_argument("--person", required=True)
    s.add_argument("--threshold", type=float, default=None,
                   help="cosine similarity to accept (default: 0.363)")
    s.add_argument("--min-sharpness", type=float, default=0.0,
                   help="drop blurry faces below this Laplacian variance")
    s.add_argument("--by", choices=["face", "appearance"], default="face",
                   help="match on the face, or on overall appearance (needs an "
                        "index built with --appearance)")
    _add_range_args(s)
    _add_group_args(s)
    _add_output_args(s)

    # ---- objects
    s = sub.add_parser("objects", help="find when objects appear (needs --objects index)")
    s.add_argument("--labels", nargs="+", default=["person"])
    s.add_argument("--min-score", type=float, default=0.4)
    _add_range_args(s)
    _add_group_args(s)
    _add_output_args(s)

    # ---- zones
    s = sub.add_parser("zone", help="watch one rectangle of the picture "
                                    "(a door, a till, a parking bay)")
    zsub = s.add_subparsers(dest="zone_command", required=True)

    z = zsub.add_parser("add", help="save a rectangle to watch")
    z.add_argument("--name", required=True, help='e.g. "front door"')
    z.add_argument("--box", required=True, metavar="X,Y,W,H",
                   help="rectangle as fractions of the frame, e.g. 0.42,0.30,0.14,0.38")
    z.add_argument("--video", default=None,
                   help="the video it was drawn on; omit to watch every video")
    z.add_argument("--mode", choices=list(ZONE_MODES), default="change",
                   help="change: differs from how it usually looks (a door left "
                        "open); motion: differs from the frame before (the moment "
                        "it swung)")
    z.add_argument("--sensitivity", type=float, default=0.15,
                   help="fraction of the rectangle that must differ (0-1)")

    zsub.add_parser("list", help="show the saved zones")

    z = zsub.add_parser("remove", help="delete a saved zone")
    z.add_argument("--name", required=True)
    z.add_argument("--video", default=None)

    z = zsub.add_parser("scan", help="find every moment a zone was not itself")
    z.add_argument("--name", default=None, help="a saved zone")
    z.add_argument("--box", default=None, metavar="X,Y,W,H",
                   help="or a rectangle given here, without saving it")
    z.add_argument("--mode", choices=list(ZONE_MODES), default=None)
    z.add_argument("--sensitivity", type=float, default=None)
    _add_range_args(z)                       # --video lives here
    _add_group_args(z)
    _add_output_args(z)

    # ---- counting lines
    s = sub.add_parser("line", help="count who crosses a line, and which way")
    lsub = s.add_subparsers(dest="line_command", required=True)

    z = lsub.add_parser("add", help="save a counting line")
    z.add_argument("--name", required=True, help='e.g. "front gate"')
    z.add_argument("--line", required=True, metavar="X1,Y1,X2,Y2",
                   help="two points as fractions of the frame, e.g. 0.5,0.1,0.5,0.9")
    z.add_argument("--video", default=None,
                   help="the video it was drawn on; omit to count in every video")
    z.add_argument("--flip", action="store_true",
                   help="swap which side of the line counts as 'in'")
    z.add_argument("--labels", nargs="+", default=["person"],
                   help="what to count (default: person)")

    lsub.add_parser("list", help="show the saved lines")

    z = lsub.add_parser("remove", help="delete a saved line")
    z.add_argument("--name", required=True)
    z.add_argument("--video", default=None)

    z = lsub.add_parser("scan", help="report every crossing")
    z.add_argument("--name", default=None, help="a saved line")
    z.add_argument("--line", default=None, metavar="X1,Y1,X2,Y2",
                   help="or two points given here, without saving them")
    z.add_argument("--direction", choices=("in", "out", "both"), default="both")
    z.add_argument("--flip", action="store_true")
    z.add_argument("--labels", nargs="*", default=None)
    _add_range_args(z)                       # --video lives here
    _add_output_args(z)

    # ---- cluster / label
    s = sub.add_parser("cluster", help="group unknown faces - who appears at all?")
    s.add_argument("--threshold", type=float, default=0.45)
    s.add_argument("--min-size", type=int, default=3,
                   help="ignore clusters with fewer faces than this")
    s.add_argument("--min-sharpness", type=float, default=8.0)
    s.add_argument("--video", nargs="*", default=None, dest="videos")
    s.add_argument("--report", default=None, metavar="FILE")

    s = sub.add_parser("label", help="name a cluster so you can search for it")
    s.add_argument("--cluster", type=int, required=True)
    s.add_argument("--name", required=True)

    # ---- ask
    s = sub.add_parser("ask", help="search the footage with a natural-language instruction")
    s.add_argument("query", help='e.g. "a delivery van at the gate after dark"')
    s.add_argument("--model", default=None)
    s.add_argument("--max-frames", type=int, default=400)
    s.add_argument("--grid", type=int, default=9, help="frames per triage request")
    s.add_argument("--min-confidence", type=float, default=0.5)
    s.add_argument("--no-confirm", action="store_true",
                   help="skip the full-resolution second pass (faster, noisier)")
    s.add_argument("--effort", default="low", choices=["low", "medium", "high", "xhigh", "max"])
    s.add_argument("--concurrency", type=int, default=4)
    s.add_argument("--min-activity", type=float, default=0.0)
    s.add_argument("--dry-run", action="store_true", help="show the plan, call nothing")
    _add_range_args(s)
    _add_group_args(s)
    _add_output_args(s)

    # ---- similar
    s = sub.add_parser("similar",
                       help="find everyone who looks like the person at this moment")
    s.add_argument("--video", required=True, help="indexed video (id, path or name)")
    s.add_argument("--at", required=True, metavar="TC", help="moment to take them from")
    s.add_argument("--box", default=None, metavar="X,Y,W,H",
                   help="crop to use, in analysis pixels; omitted = the person "
                        "already indexed nearest that moment")
    s.add_argument("--threshold", type=float, default=None,
                   help="appearance cosine to accept (default: 0.60)")
    s.add_argument("--enroll", default=None, metavar="NAME",
                   help="also save this appearance as a reference for NAME")
    s.add_argument("--only", nargs="*", default=None, dest="videos",
                   help="search only these videos (default: the whole index)")
    s.add_argument("--from", dest="start", default="0", metavar="TC")
    s.add_argument("--to", dest="end", default=None, metavar="TC")
    _add_group_args(s)
    _add_output_args(s)

    # ---- doctor
    s = sub.add_parser("doctor",
                       help="is this footage searchable? measure before you index")
    s.add_argument("paths", nargs="+", help="video files to examine")
    s.add_argument("--samples", type=int, default=60,
                   help="frames to sample across the file (default: 60)")
    s.add_argument("--width", type=int, default=1280)
    s.add_argument("--from", dest="start", default="0", metavar="TC")
    s.add_argument("--to", dest="end", default=None, metavar="TC")
    s.add_argument("--json", default=None, metavar="FILE")

    # ---- clip
    s = sub.add_parser("clip", help="cut one clip out of an indexed video")
    s.add_argument("--video", required=True)
    s.add_argument("--from", dest="start", required=True, metavar="TC")
    s.add_argument("--to", dest="end", required=True, metavar="TC")
    s.add_argument("--out", required=True)
    s.add_argument("--pad", type=float, default=0.0)

    # ---- models
    s = sub.add_parser("models", help="manage the local ONNX models")
    s.add_argument("action", choices=["list", "fetch"], nargs="?", default="list")

    return p


def _add_range_args(s: argparse.ArgumentParser) -> None:
    s.add_argument("--video", nargs="*", default=None, dest="videos",
                   help="restrict to these videos (id, path or filename fragment)")
    s.add_argument("--from", dest="start", default="0", metavar="TC")
    s.add_argument("--to", dest="end", default=None, metavar="TC")


def _add_group_args(s: argparse.ArgumentParser) -> None:
    s.add_argument("--gap", type=float, default=5.0,
                   help="seconds of silence that split one appearance from the next")
    s.add_argument("--min-hits", type=int, default=1,
                   help="ignore events backed by fewer frames than this")
    s.add_argument("--arrivals", action="store_true",
                   help="only the first appearance after a long absence")
    s.add_argument("--absence", type=float, default=300.0,
                   help="seconds of absence that count as 'arrived again'")


def _add_output_args(s: argparse.ArgumentParser) -> None:
    s.add_argument("--json", default=None, metavar="FILE")
    s.add_argument("--report", default=None, metavar="FILE", help="write an HTML timeline")
    s.add_argument("--clips", default=None, metavar="DIR",
                   help="cut a video clip per event into this directory")
    s.add_argument("--clip-pad", type=float, default=3.0)
    s.add_argument("--limit", type=int, default=0, help="show at most N events")


# ------------------------------------------------------------------ helpers
def collect_videos(paths: list[str], recursive: bool) -> list[Path]:
    out: list[Path] = []
    for raw in paths:
        p = Path(raw).expanduser()
        if p.is_dir():
            it = p.rglob("*") if recursive else p.glob("*")
            out.extend(sorted(f for f in it
                              if f.is_file() and f.suffix.lower() in VIDEO_SUFFIXES))
        elif p.exists():
            out.append(p)
        else:
            LOG.warning("no such file: %s", p)
    if not out:
        raise SystemExit("no video files found")
    return out


def _video_ids(index: Index, selectors) -> list[int] | None:
    if not selectors:
        return None
    return [int(r["id"]) for r in index.resolve_videos(selectors)]


def emit(index: Index, args, events: list[Event], title: str,
         query: str | None = None) -> int:
    from .report import write_json, write_report
    from .video import extract_clip

    if getattr(args, "limit", 0):
        events = events[:args.limit]

    if not events:
        print("no matches.")
    for i, e in enumerate(events, 1):
        note = e.meta.get("note")
        print(f"{i:3d}. {e.describe()}")
        if note:
            print(f"      {note}")

    if getattr(args, "json", None):
        write_json(events, args.json, query)
    if getattr(args, "report", None):
        write_report(events, args.report, title, query, index_root=index.root)
    if getattr(args, "clips", None) and events:
        out_dir = Path(args.clips)
        out_dir.mkdir(parents=True, exist_ok=True)
        for i, e in enumerate(events, 1):
            name = f"{i:03d}_{Path(e.video_path).stem}_{fmt_timecode(e.start).replace(':', '-')}.mp4"
            try:
                extract_clip(e.video_path, e.start, e.end, out_dir / name, args.clip_pad)
            except Exception as exc:
                LOG.error("clip %s failed: %s", name, exc)
        LOG.info("clips written to %s", out_dir)
    return 0 if events else 1


# ----------------------------------------------------------------- commands
def cmd_index(args, index: Index) -> int:
    from .indexer import IndexOptions, Indexer
    from .video import probe

    files = collect_videos(args.paths, args.recursive)
    labels = tuple(args.labels or ())
    if "all" in labels:
        labels = ()
    opts = IndexOptions(
        sample_fps=args.sample_fps,
        max_width=args.width,
        motion_threshold=args.motion_threshold,
        keyframe_every=args.keyframe_every,
        detect_faces=not args.no_faces,
        detect_objects=args.objects,
        object_labels=labels,
        object_conf=args.object_conf,
        detect_appearance=args.appearance,
        appearance_every=args.appearance_every,
        thumbs=not args.no_thumbs,
        thumb_width=args.thumb_width,
        start=parse_timecode(args.start),
        end=parse_timecode(args.end) if args.end else None,
        allow_download=not args.offline,
    )
    indexer = Indexer(index, opts)
    total = 0
    for f in files:
        stats = indexer.run(f, force=args.force)
        total += stats.frames_kept
        if args.start_time:
            row = index.find_video(f)
            if row:
                index.conn.execute("UPDATE videos SET started_at = ? WHERE id = ?",
                                   (parse_datetime(args.start_time).isoformat(),
                                    row["id"]))
                index.commit()
    from .vectors import clear_caches
    clear_caches(index.root)
    st = index.stats()
    print(f"indexed {len(files)} file(s); index now holds {st['frames']} frames, "
          f"{st['faces']} faces, {st['appearances']} appearance vectors, "
          f"{st['objects']} objects")
    return 0


def cmd_videos(args, index: Index) -> int:
    rows = index.videos()
    if not rows:
        print("index is empty - run 'vscan index <files>' first")
        return 1
    for r in rows:
        counts = index.conn.execute(
            "SELECT (SELECT COUNT(*) FROM faces WHERE video_id=?) AS f,"
            " (SELECT COUNT(*) FROM objects WHERE video_id=?) AS o",
            (r["id"], r["id"])).fetchone()
        print(f"[{r['id']}] {Path(r['path']).name}")
        print(f"     {fmt_timecode(r['duration'] or 0)}  {r['width']}x{r['height']}"
              f"  {r['codec']}  sampled {r['sample_fps']} fps")
        print(f"     {r['frames_kept']} frames kept, {counts['f']} faces,"
              f" {counts['o']} objects, indexed {r['indexed_at']}")
        if r["started_at"]:
            print(f"     starts at {r['started_at']}")
    st = index.stats()
    print(f"\n{st['videos']} video(s), {st['persons']} enrolled person(s)")
    return 0


def cmd_enroll(args, index: Index) -> int:
    from .faces import FaceEngine
    from .search import enroll_from_video, enroll_images

    engine = FaceEngine(allow_download=not args.offline, min_embed_face=16)
    added = 0
    if args.images:
        added += enroll_images(index, engine, args.name, args.images)
    if args.from_video:
        if not args.at:
            raise SystemExit("--from-video needs at least one --at TIMECODE")
        added += enroll_from_video(index, engine, args.name, args.from_video,
                                   [parse_timecode(t) for t in args.at])
    if not args.images and not args.from_video:
        raise SystemExit("give some images or --from-video VIDEO --at TIMECODE")
    index.commit()
    person = index.person_by_name(args.name)
    total = len(index.person_embeddings(int(person["id"]))) if person else 0
    print(f"{args.name}: added {added} reference face(s), {total} in total")
    return 0 if added else 1


def cmd_persons(args, index: Index) -> int:
    rows = index.persons()
    if not rows:
        print("nobody enrolled yet - see 'vscan enroll --help'")
        return 1
    for r in rows:
        print(f"{r['name']}  ({r['n_emb']} reference face(s), added {r['created_at']})")
    return 0


def cmd_forget(args, index: Index) -> int:
    ok = index.delete_person(args.name)
    print(f"removed {args.name}" if ok else f"no such person: {args.name}")
    return 0 if ok else 1


def cmd_find(args, index: Index) -> int:
    from .appearance import DEFAULT_APPEARANCE_THRESHOLD
    from .faces import DEFAULT_MATCH_THRESHOLD
    from .search import find_person, find_person_appearance, started_at_map

    by_face = args.by == "face"
    default = DEFAULT_MATCH_THRESHOLD if by_face else DEFAULT_APPEARANCE_THRESHOLD
    threshold = args.threshold if args.threshold is not None else default
    start = parse_timecode(args.start)
    end = parse_timecode(args.end) if args.end else None
    if by_face:
        hits = find_person(index, args.person, threshold,
                           _video_ids(index, args.videos), args.min_sharpness,
                           start, end)
    else:
        hits = find_person_appearance(index, args.person, threshold,
                                      _video_ids(index, args.videos), start, end)
    events = group_hits(hits, args.person, args.gap, args.min_hits, started_at_map(index))
    if args.arrivals:
        events = arrivals(events, args.absence)
    title = f"{args.person} - {'arrivals' if args.arrivals else 'appearances'}"
    return emit(index, args, events, title,
                query=f"{args.by} match >= {threshold:.3f}")


def cmd_objects(args, index: Index) -> int:
    from .search import find_objects, started_at_map

    hits = find_objects(index, args.labels, args.min_score, _video_ids(index, args.videos))
    start, end = parse_timecode(args.start), (parse_timecode(args.end) if args.end else None)
    hits = [h for h in hits if h.t >= start and (end is None or h.t <= end)]
    label = ", ".join(args.labels)
    events = group_hits(hits, label, args.gap, args.min_hits, started_at_map(index))
    if args.arrivals:
        events = arrivals(events, args.absence)
    return emit(index, args, events, f"{label} detections", query=label)


def _zone_video_id(index: Index, selector: str | None) -> int | None:
    if not selector:
        return None
    return int(index.resolve_videos([selector])[0]["id"])


def cmd_zone(args, index: Index) -> int:
    from .search import started_at_map
    from .zones import Box, DEFAULT_SENSITIVITY, scan

    if args.zone_command == "add":
        video_id = _zone_video_id(index, args.video)
        box = Box.parse(args.box)
        zone_id = index.add_zone(args.name, box.as_tuple(), video_id, args.mode,
                                 args.sensitivity)
        scope = Path(index.get_video(video_id)["path"]).name if video_id else "every video"
        print(f"zone {zone_id}: {args.name!r} on {scope} "
              f"({args.mode}, sensitivity {args.sensitivity:.2f})")
        return 0

    if args.zone_command == "list":
        rows = index.zones()
        if not rows:
            print("no zones yet - add one with 'vscan zone add'.")
            return 1
        for r in rows:
            video = index.get_video(r["video_id"]) if r["video_id"] else None
            scope = Path(video["path"]).name if video else "all videos"
            print(f"{r['id']:3d}. {r['name']:<24} {scope:<28} "
                  f"box {r['x']:.3f},{r['y']:.3f},{r['w']:.3f},{r['h']:.3f}  "
                  f"{r['mode']} >= {r['sensitivity']:.2f}")
        return 0

    if args.zone_command == "remove":
        row = index.zone_by_name(args.name, _zone_video_id(index, args.video))
        if row is None or not index.delete_zone(int(row["id"])):
            LOG.error("no zone called %r", args.name)
            return 1
        print(f"deleted zone {args.name!r}")
        return 0

    # ---- scan
    if not args.name and not args.box:
        LOG.error("give --name of a saved zone, or --box x,y,w,h")
        return 2
    zone = index.zone_by_name(args.name) if args.name else None
    if args.name and zone is None:
        LOG.error("no zone called %r - 'vscan zone list' shows the saved ones",
                  args.name)
        return 1

    box = Box.parse(args.box) if args.box else \
        Box(zone["x"], zone["y"], zone["w"], zone["h"])
    mode = args.mode or (zone["mode"] if zone else "change")
    sensitivity = args.sensitivity if args.sensitivity is not None else \
        (zone["sensitivity"] if zone else DEFAULT_SENSITIVITY)
    label = args.name or "zone"

    selectors = args.videos
    if not selectors and zone is not None and zone["video_id"]:
        selectors = [str(zone["video_id"])]
    video_ids = _video_ids(index, selectors) or [int(v["id"]) for v in index.videos()]
    if not video_ids:
        LOG.error("nothing indexed yet")
        return 1

    start = parse_timecode(args.start)
    end = parse_timecode(args.end) if args.end else None
    hits, examined = [], 0
    for video_id in video_ids:
        try:
            result = scan(index, video_id, box, mode, sensitivity, start, end, label)
        except SystemExit as exc:                 # one unindexed video is not fatal
            LOG.warning("%s", exc)
            continue
        hits.extend(result.hits)
        examined += result.frames_examined
    LOG.info("%d of %d stored frames matched", len(hits), examined)

    events = group_hits(hits, label, args.gap, args.min_hits, started_at_map(index))
    if args.arrivals:
        events = arrivals(events, args.absence)
    return emit(index, args, events, f"{label} - {mode}", query=label)


def cmd_line(args, index: Index) -> int:
    from .search import started_at_map
    from .tripwire import Line, crossings, to_events

    if args.line_command == "add":
        video_id = _zone_video_id(index, args.video)
        line = Line.parse(args.line, args.flip)
        line_id = index.add_tripwire(args.name, line.as_tuple(), video_id,
                                     args.flip, args.labels)
        scope = Path(index.get_video(video_id)["path"]).name if video_id else "every video"
        print(f"line {line_id}: {args.name!r} on {scope} "
              f"(counting {', '.join(args.labels)})")
        return 0

    if args.line_command == "list":
        rows = index.tripwires()
        if not rows:
            print("no lines yet - add one with 'vscan line add'.")
            return 1
        for r in rows:
            video = index.get_video(r["video_id"]) if r["video_id"] else None
            scope = Path(video["path"]).name if video else "all videos"
            print(f"{r['id']:3d}. {r['name']:<24} {scope:<28} "
                  f"{r['x1']:.2f},{r['y1']:.2f} -> {r['x2']:.2f},{r['y2']:.2f}"
                  f"  {r['labels']}{'  (flipped)' if r['flipped'] else ''}")
        return 0

    if args.line_command == "remove":
        row = index.tripwire_by_name(args.name, _zone_video_id(index, args.video))
        if row is None or not index.delete_tripwire(int(row["id"])):
            LOG.error("no line called %r", args.name)
            return 1
        print(f"deleted line {args.name!r}")
        return 0

    # ---- scan
    if not args.name and not args.line:
        LOG.error("give --name of a saved line, or --line x1,y1,x2,y2")
        return 2
    saved = index.tripwire_by_name(args.name) if args.name else None
    if args.name and saved is None:
        LOG.error("no line called %r - 'vscan line list' shows the saved ones",
                  args.name)
        return 1

    if args.line:
        line = Line.parse(args.line, args.flip)
    else:
        line = Line.parse([saved["x1"], saved["y1"], saved["x2"], saved["y2"]],
                          bool(saved["flipped"]))
    labels = args.labels or (
        [l for l in (saved["labels"] or "person").split(",") if l] if saved
        else ["person"])
    label = args.name or "line"

    selectors = args.videos
    if not selectors and saved is not None and saved["video_id"]:
        selectors = [str(saved["video_id"])]
    video_ids = _video_ids(index, selectors) or [int(v["id"]) for v in index.videos()]

    start = parse_timecode(args.start)
    end = parse_timecode(args.end) if args.end else None
    found = []
    for video_id in video_ids:
        found.extend(crossings(index, video_id, line, labels, 0.4, start, end))
    inbound = sum(1 for c in found if c.direction == "in")
    print(f"{len(found)} crossing(s): {inbound} in, {len(found) - inbound} out")

    events = to_events(found, label, started_at_map(index), args.direction)
    return emit(index, args, events, f"{label} - {args.direction}", query=label)


def cmd_cluster(args, index: Index) -> int:
    from .report import write_cluster_report
    from .search import cluster_faces, save_clusters

    clusters = cluster_faces(index, _video_ids(index, args.videos), args.threshold,
                             args.min_sharpness, args.min_size)
    if not clusters:
        print("no face clusters found - index some footage with faces first")
        return 1
    save_clusters(index, clusters)
    for c in clusters:
        times = c["times"]
        span = f"{fmt_timecode(times[0])}-{fmt_timecode(times[-1])}" if times else ""
        print(f"cluster {c['id']:3d}: {c['size']:5d} face(s)  {span}  "
              f"{', '.join(Path(v).name for v in c['videos'][:2])}")
    print("\nname one with:  vscan label --cluster N --name \"Someone\"")
    if args.report:
        write_cluster_report(clusters, args.report, index.root)
    return 0


def cmd_label(args, index: Index) -> int:
    from .search import enroll_from_faces, load_clusters

    clusters = load_clusters(index)
    match = next((c for c in clusters if c["id"] == args.cluster), None)
    if match is None:
        raise SystemExit(f"no cluster {args.cluster} - run 'vscan cluster' again")
    n = enroll_from_faces(index, args.name, match["face_ids"])
    print(f"{args.name}: enrolled from {n} face(s) of cluster {args.cluster}")
    print(f"now try:  vscan find --person \"{args.name}\" --arrivals")
    return 0


def cmd_ask(args, index: Index) -> int:
    from .search import started_at_map
    from .semantic import DEFAULT_MODEL, AskOptions, ask, select_frames

    opts = AskOptions(
        model=args.model or DEFAULT_MODEL,
        grid=max(1, args.grid),
        max_frames=args.max_frames,
        min_confidence=args.min_confidence,
        confirm=not args.no_confirm,
        concurrency=args.concurrency,
        effort=args.effort,
        dry_run=args.dry_run,
    )
    refs = select_frames(index, _video_ids(index, args.videos), parse_timecode(args.start),
                         parse_timecode(args.end) if args.end else None,
                         args.min_activity, args.max_frames)
    result = ask(args.query, refs, opts)
    if args.dry_run:
        print(f"would examine {len(refs)} frame(s) in "
              f"{(len(refs) + opts.grid - 1) // max(1, opts.grid)} grid request(s)"
              f"{' plus one request per candidate' if opts.confirm else ''}")
        return 0
    events = group_hits(result.hits, args.query, args.gap, args.min_hits,
                        started_at_map(index))
    if args.arrivals:
        events = arrivals(events, args.absence)
    return emit(index, args, events, f"Search: {args.query}", query=args.query)


def cmd_similar(args, index: Index) -> int:
    from .appearance import DEFAULT_APPEARANCE_THRESHOLD
    from .search import (appearance_at, enroll_appearance, search_vectors,
                         started_at_map)

    video = index.resolve_videos([args.video])[0]
    at = parse_timecode(args.at)
    box = [float(v) for v in args.box.split(",")] if args.box else None
    taken = appearance_at(index, int(video["id"]), at, box)
    if taken is None:
        raise SystemExit("could not take an appearance vector from that moment")
    emb, used_box = taken
    LOG.info("taking appearance from %s at %s, box %s", Path(video["path"]).name,
             fmt_timecode(at), [round(v) for v in used_box])

    if args.enroll:
        enroll_appearance(index, args.enroll, emb,
                          f"video:{video['path']}@{fmt_timecode(at, ms=True)}")
        print(f"saved as an appearance reference for {args.enroll}")

    threshold = args.threshold if args.threshold is not None \
        else DEFAULT_APPEARANCE_THRESHOLD
    hits = search_vectors(index, "appearances", emb, threshold,
                          _video_ids(index, args.videos), 0.0,
                          parse_timecode(args.start),
                          parse_timecode(args.end) if args.end else None)
    label = f"looks like {Path(video['path']).name}@{fmt_timecode(at)}"
    events = group_hits(hits, label, args.gap, args.min_hits, started_at_map(index))
    if args.arrivals:
        events = arrivals(events, args.absence)
    return emit(index, args, events, label,
                query=f"appearance match >= {threshold:.3f}")


def cmd_doctor(args, index: Index | None) -> int:
    import json as _json

    from .doctor import examine, render

    reports = []
    for raw in collect_videos(args.paths, recursive=False):
        report = examine(raw, args.samples, args.width, parse_timecode(args.start),
                         parse_timecode(args.end) if args.end else None)
        print(render(report))
        print()
        reports.append(report.to_dict())
    if args.json:
        Path(args.json).write_text(_json.dumps(reports, ensure_ascii=False, indent=2),
                                   encoding="utf-8")
        LOG.info("json written to %s", args.json)
    return 0


def cmd_clip(args, index: Index) -> int:
    from .video import extract_clip

    row = index.resolve_videos([args.video])[0]
    out = extract_clip(row["path"], parse_timecode(args.start), parse_timecode(args.end),
                       args.out, args.pad)
    print(f"wrote {out} ({human_size(Path(out).stat().st_size)})")
    return 0


def cmd_models(args, index: Index | None) -> int:
    from . import modelzoo

    if args.action == "fetch":
        for path in modelzoo.fetch_all():
            print(f"ready: {path}")
        return 0
    print(f"model directory: {modelzoo.model_dir()}")
    for spec in modelzoo.MODELS.values():
        path = modelzoo.model_dir() / spec.filename
        state = "cached" if path.exists() else "not downloaded"
        print(f"  {spec.key:12s} {spec.filename}  [{state}]  {spec.note}")
    return 0


COMMANDS = {
    "index": cmd_index, "videos": cmd_videos, "enroll": cmd_enroll,
    "persons": cmd_persons, "forget": cmd_forget, "find": cmd_find,
    "objects": cmd_objects, "cluster": cmd_cluster, "label": cmd_label,
    "ask": cmd_ask, "similar": cmd_similar, "doctor": cmd_doctor,
    "zone": cmd_zone, "line": cmd_line,
    "clip": cmd_clip, "models": cmd_models,
}


# These inspect files or the model cache; they must not create an index
# directory as a side effect of being run.
NO_INDEX = {"doctor", "models"}


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    setup_logging(args.verbose)
    try:
        if args.command in NO_INDEX:
            return COMMANDS[args.command](args, None)
        with Index(args.index) as index:
            return COMMANDS[args.command](args, index)
    except KeyboardInterrupt:
        LOG.warning("interrupted")
        return 130
    except (RuntimeError, ValueError, FileNotFoundError) as exc:
        LOG.error("%s", exc)
        return 2


if __name__ == "__main__":
    sys.exit(main())
