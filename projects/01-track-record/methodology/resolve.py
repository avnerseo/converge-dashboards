#!/usr/bin/env python3
"""
Resolve which methodology version produced a given publication.

The point of this file: a pick is only scoreable if you can say, without
guessing, which rule set produced it. So resolution is anchored to the
publishing COMMIT, never to a date and never to "whatever version is newest".

  * Two versions were published on 2026-08-19. A date lookup for that day is
    ambiguous and this module refuses to answer it. That is the whole reason
    commit anchoring exists rather than a dated table.
  * A commit that no version claims resolves to None. The ledger then records
    methodology_version = null. Never fill it in by proximity — an invented
    version stamp is worse than an admitted gap, because it silently licenses
    pooling picks that were made under different rules.

CLI
  python3 resolve.py --list                 versions, dates, commits, hashes
  python3 resolve.py --commit 280245e       which version produced that run
  python3 resolve.py --diff v9 v10          what changed between two versions
  python3 resolve.py --freeze               stamp rule_hash into each vN.json
  python3 resolve.py --verify               integrity checks (exit 1 on failure)
"""
import json, os, sys, glob, hashlib, subprocess, re, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
VDIR = os.path.join(HERE, "versions")
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

# Chronological order of the version series. Explicit, not derived from the
# filename sort, because "v10" sorts before "v2" in every naive sort there is.
ORDER = ["v%d" % i for i in range(1, 12)]


def _vnum(vid):
    return int(vid[1:])


def load_all():
    out = {}
    for p in glob.glob(os.path.join(VDIR, "v*.json")):
        with open(p) as f:
            v = json.load(f)
        v["_path"] = p
        out[v["version"]] = v
    return out


def ordered(vs):
    return [vs[k] for k in sorted(vs, key=_vnum)]


def rule_hash(v):
    """sha256 over the canonical selection block only.

    Evidence is deliberately outside the hash: it is verifiable against git
    directly (--verify does exactly that), which is a stronger guarantee than
    a self-referential digest.
    """
    canon = json.dumps(v["selection"], ensure_ascii=False, sort_keys=True,
                       separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canon.encode("utf-8")).hexdigest()[:16]


def commit_index(vs):
    idx = {}
    for v in ordered(vs):
        for sha in v["published"]["commits"]:
            idx[sha] = v["version"]
    return idx


def version_for_commit(sha, vs=None):
    """Exact or unique-prefix match on the publishing commit. None if unclaimed."""
    vs = vs or load_all()
    idx = commit_index(vs)
    if sha in idx:
        return idx[sha]
    hits = {v for s, v in idx.items() if s.startswith(sha) or sha.startswith(s)}
    return hits.pop() if len(hits) == 1 else None


def version_for_date(date, vs=None):
    """Only answers when the date is unambiguous. Raises otherwise, by design."""
    vs = vs or load_all()
    hits = [v["version"] for v in ordered(vs)
            if v["published"]["first_date"] <= date <= v["published"]["last_date"]]
    if len(hits) > 1:
        raise ValueError(
            f"{date} spans {len(hits)} methodology versions ({', '.join(hits)}). "
            "Resolve by commit — the date does not identify the rule set.")
    return hits[0] if hits else None


# ----------------------------------------------------------------- git checks
def git(*a):
    return subprocess.run(["git", "-C", REPO, *a],
                          capture_output=True, text=True).stdout


def _norm(s):
    s = re.sub(r"<[^>]+>", " ", s)
    for a, b in (("&amp;", "&"), ("&quot;", '"'), ("&nbsp;", " "), ("&#39;", "'")):
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s).strip()


def verify(vs=None):
    vs = vs or load_all()
    errs, warns, checked = [], [], 0

    seen_commits = {}
    for v in ordered(vs):
        vid = v["version"]

        if v.get("rule_hash") != rule_hash(v):
            errs.append(f"{vid}: rule_hash does not match selection block "
                        f"(run --freeze after an intentional edit)")

        prev = ORDER[_vnum(vid) - 2] if _vnum(vid) > 1 else None
        if v.get("supersedes") != prev:
            errs.append(f"{vid}: supersedes={v.get('supersedes')!r}, expected {prev!r}")

        for sha in v["published"]["commits"]:
            if sha in seen_commits:
                errs.append(f"commit {sha} claimed by both {seen_commits[sha]} and {vid}")
            seen_commits[sha] = vid
            if not git("cat-file", "-t", sha).strip():
                errs.append(f"{vid}: commit {sha} not found in this repository")
                continue
            d = git("log", "-1", "--format=%ad", "--date=short", sha).strip()
            if not (v["published"]["first_date"] <= d <= v["published"]["last_date"]):
                errs.append(f"{vid}: commit {sha} dated {d}, outside "
                            f"{v['published']['first_date']}..{v['published']['last_date']}")

        # every quoted rule must still be findable in the file it is cited from
        for ev in v.get("evidence", []):
            q = ev["quote_he"]
            if ev.get("kind") == "absence":
                continue  # records that a section was missing, not that it said something
            if "..." in q and ev.get("kind") == "rule":
                errs.append(f"{vid}: rule quote is elided and so can never be matched "
                            f"as a substring — split it into verbatim clauses: {q[:50]}…")
                continue
            m = re.search(r"@([0-9a-f]{7,40})", ev["where"])
            if not m:
                warns.append(f"{vid}: evidence has no commit anchor: {ev['where']}")
                continue
            html = git("show", f"{m.group(1)}:index.html")
            checked += 1
            if _norm(q) not in _norm(html):
                errs.append(f"{vid}: quoted rule not found in index.html@{m.group(1)}: "
                            f"{q[:60]}…")

    print(f"versions        : {len(vs)}")
    print(f"commits claimed : {len(seen_commits)}")
    print(f"quotes verified : {checked} against index.html in git")
    for w in warns:
        print("WARN  " + w)
    for e in errs:
        print("FAIL  " + e)
    print("\n" + ("OK — every rule set hashes clean and every quoted rule is in the "
                  "committed HTML it cites." if not errs else f"{len(errs)} failure(s)"))
    return 1 if errs else 0


def freeze(vs=None):
    vs = vs or load_all()
    for v in ordered(vs):
        h = rule_hash(v)
        if v.get("rule_hash") == h:
            continue
        old = v.get("rule_hash")
        body = {k: val for k, val in v.items() if not k.startswith("_")}
        body["rule_hash"] = h
        keys = ["version", "rule_hash", "published", "supersedes", "summary_he",
                "changes_from_previous", "selection", "evidence", "unverifiable"]
        body = {k: body[k] for k in keys if k in body}
        with open(v["_path"], "w") as f:
            json.dump(body, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print(f"{v['version']}: {old or '(none)'} -> {h}")
    return 0


def show_list(vs=None):
    vs = vs or load_all()
    for v in ordered(vs):
        p = v["published"]
        span = p["first_date"] if p["first_date"] == p["last_date"] \
            else f"{p['first_date']}..{p['last_date']}"
        subs = [c for c in v.get("changes_from_previous", []) if c.get("substantive")]
        print(f"{v['version']:<4} {span:<22} {', '.join(p['commits'])}")
        print(f"     {v.get('rule_hash','(unfrozen)')}  substantive changes: {len(subs)}")
        print(f"     {v['summary_he']}")
    return 0


def diff(a, b, vs=None):
    vs = vs or load_all()
    if a not in vs or b not in vs:
        print("unknown version", file=sys.stderr)
        return 1
    print(f"{a} -> {b}")
    for c in vs[b].get("changes_from_previous", []):
        mark = "SUBSTANTIVE" if c.get("substantive") else "cosmetic   "
        print(f"  [{mark}] {c['type']:<10} {c['field']}")
        print(f"      {c['note_he']}")
    if not vs[b].get("changes_from_previous"):
        print("  (no recorded change)")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--commit")
    ap.add_argument("--date")
    ap.add_argument("--diff", nargs=2, metavar=("A", "B"))
    ap.add_argument("--freeze", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ns = ap.parse_args()

    if ns.freeze:
        sys.exit(freeze())
    if ns.verify:
        sys.exit(verify())
    if ns.diff:
        sys.exit(diff(*ns.diff))
    if ns.commit:
        v = version_for_commit(ns.commit)
        print(v or "UNCLAIMED — no methodology version covers this commit")
        sys.exit(0 if v else 1)
    if ns.date:
        try:
            print(version_for_date(ns.date) or "no version covers this date")
        except ValueError as e:
            print(e, file=sys.stderr)
            sys.exit(1)
        sys.exit(0)
    sys.exit(show_list())
