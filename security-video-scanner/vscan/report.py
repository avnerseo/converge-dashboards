"""Self-contained HTML timeline of results (thumbnails embedded, no assets)."""
from __future__ import annotations

import base64
import datetime as dt
import html
import json
from pathlib import Path
from typing import Sequence

from .events import Event
from .util import LOG, fmt_timecode

_CSS = """
:root { color-scheme: light dark; --bg:#f7f7f8; --fg:#1b1b1f; --card:#fff;
        --muted:#666; --line:#e3e3e8; --accent:#b3421c; }
@media (prefers-color-scheme: dark) {
  :root { --bg:#16161a; --fg:#e9e9ee; --card:#1f1f25; --muted:#9a9aa5;
          --line:#2c2c34; --accent:#ff8a5c; } }
* { box-sizing: border-box; }
body { margin:0; padding:24px; background:var(--bg); color:var(--fg);
       font:14px/1.5 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif; }
h1 { font-size:20px; margin:0 0 4px; }
.sub { color:var(--muted); margin-bottom:20px; }
.q { background:var(--card); border:1px solid var(--line); border-left:3px solid var(--accent);
     border-radius:6px; padding:10px 14px; margin:0 0 20px; }
.grid { display:grid; gap:14px; grid-template-columns:repeat(auto-fill,minmax(260px,1fr)); }
.card { background:var(--card); border:1px solid var(--line); border-radius:10px;
        overflow:hidden; }
.card img { width:100%; display:block; background:#000; aspect-ratio:16/9; object-fit:contain; }
.card .body { padding:10px 12px; }
.t { font-weight:600; font-variant-numeric:tabular-nums; }
.meta, .note { color:var(--muted); font-size:12.5px; margin-top:3px; word-wrap:break-word; }
.bar { height:5px; background:var(--line); border-radius:3px; margin-top:8px; overflow:hidden; }
.bar > i { display:block; height:100%; background:var(--accent); }
table { border-collapse:collapse; width:100%; margin-top:8px; }
td, th { border-bottom:1px solid var(--line); padding:6px 8px; text-align:start; }
footer { color:var(--muted); font-size:12px; margin-top:28px; }
"""


def _thumb_data(path: str | Path | None, max_width: int = 420) -> str | None:
    if not path:
        return None
    p = Path(path)
    if not p.exists():
        return None
    try:
        import cv2
        img = cv2.imread(str(p))
        if img is None:
            return None
        if img.shape[1] > max_width:
            scale = max_width / img.shape[1]
            img = cv2.resize(img, (max_width, max(1, int(img.shape[0] * scale))),
                             interpolation=cv2.INTER_AREA)
        ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 78])
        if not ok:
            return None
        return "data:image/jpeg;base64," + base64.standard_b64encode(buf.tobytes()).decode()
    except Exception as exc:                      # pragma: no cover
        LOG.debug("thumb embed failed for %s: %s", p, exc)
        return None


def write_report(events: Sequence[Event], out: str | Path, title: str,
                 query: str | None = None, index_root: Path | None = None,
                 max_cards: int = 400) -> Path:
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    cards = []
    for e in events[:max_cards]:
        thumb = e.best_thumb
        if thumb and index_root and not Path(thumb).is_absolute():
            thumb = str(index_root / thumb)
        data = _thumb_data(thumb)
        img = (f'<img src="{data}" alt="frame at {fmt_timecode(e.best_t)}">' if data
               else '<div style="height:150px"></div>')
        wall = e.wall()
        wall_html = (f'<div class="meta">{wall:%Y-%m-%d %H:%M:%S}</div>' if wall else "")
        note = html.escape(str(e.meta.get("note", "")))
        note_html = f'<div class="note" dir="auto">{note}</div>' if note else ""
        pct = max(0.0, min(1.0, e.best_score)) * 100
        cards.append(f"""
    <div class="card">{img}
      <div class="body">
        <div class="t">{fmt_timecode(e.start)} &ndash; {fmt_timecode(e.end)}
             <span class="meta">({e.duration:.0f}s)</span></div>
        {wall_html}
        <div class="meta">{html.escape(Path(e.video_path).name)} &middot;
             {e.hits} frame(s) &middot; score {e.best_score:.2f}</div>
        {note_html}
        <div class="bar"><i style="width:{pct:.0f}%"></i></div>
      </div>
    </div>""")

    rows = "".join(
        f"<tr><td>{i + 1}</td><td>{html.escape(Path(e.video_path).name)}</td>"
        f"<td>{fmt_timecode(e.start)}</td><td>{fmt_timecode(e.end)}</td>"
        f"<td>{e.duration:.0f}s</td><td>{e.best_score:.2f}</td>"
        f"<td dir='auto'>{html.escape(str(e.meta.get('note', '')))}</td></tr>"
        for i, e in enumerate(events))

    query_html = (f'<p class="q" dir="auto"><b>Query:</b> {html.escape(query)}</p>'
                  if query else "")
    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><style>{_CSS}</style></head><body>
<h1 dir="auto">{html.escape(title)}</h1>
<p class="sub">{len(events)} event(s) &middot; generated
 {dt.datetime.now():%Y-%m-%d %H:%M}</p>
{query_html}
<div class="grid">{''.join(cards)}</div>
<h2>All events</h2>
<table><thead><tr><th>#</th><th>Video</th><th>Start</th><th>End</th>
<th>Length</th><th>Score</th><th>Note</th></tr></thead><tbody>{rows}</tbody></table>
<footer>Generated by vscan. Times are offsets into each recording; wall-clock
times appear when the source file carries a timestamp.</footer>
</body></html>"""
    out.write_text(doc, encoding="utf-8")
    LOG.info("report written to %s", out)
    return out


def write_json(events: Sequence[Event], out: str | Path, query: str | None = None) -> Path:
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "query": query,
        "count": len(events),
        "events": [e.to_dict() for e in events],
    }
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    LOG.info("json written to %s", out)
    return out


def write_cluster_report(clusters: Sequence[dict], out: str | Path,
                         index_root: Path, title: str = "Faces found in footage") -> Path:
    out = Path(out)
    cards = []
    for c in clusters:
        crop = c.get("best_crop")
        data = _thumb_data(index_root / crop if crop else None, 220)
        img = (f'<img src="{data}" style="aspect-ratio:1;object-fit:cover">' if data
               else '<div style="height:150px"></div>')
        times = c.get("times") or []
        span = (f"{fmt_timecode(times[0])} &ndash; {fmt_timecode(times[-1])}"
                if times else "")
        cards.append(f"""
    <div class="card">{img}<div class="body">
      <div class="t">Cluster #{c['id']}</div>
      <div class="meta">{c['size']} face(s) &middot; {span}</div>
      <div class="meta">{html.escape(', '.join(Path(v).name for v in c['videos'][:3]))}</div>
      <div class="note">vscan label --cluster {c['id']} --name "..."</div>
    </div></div>""")
    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><style>{_CSS}</style></head><body>
<h1>{html.escape(title)}</h1>
<p class="sub">{len(clusters)} apparent person(s), largest first</p>
<div class="grid">{''.join(cards)}</div>
<footer>Each cluster is one apparent person. Name one with
<code>vscan label --cluster N --name "..."</code>, then search for them with
<code>vscan find --person "..."</code>.</footer>
</body></html>"""
    out.write_text(doc, encoding="utf-8")
    LOG.info("cluster report written to %s", out)
    return out
