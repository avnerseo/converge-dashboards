# Methodology versions

The selection rules the dashboard actually ran, written down once per rule
state, anchored to the commits that published under them.

This exists because of one property: **a pick is only scoreable if you can say,
without guessing, which rule set produced it.** Before this directory the
dashboard recomputed its criteria on every run and left no record, so 08-28's
tier-1 list and 08-30's were not comparable and nothing could be measured across
them. Nothing here changes what the engine picks. It makes what it already
picked legible, and fixes it in place so the next change is visible as a change.

## What the record shows

Eleven rule states across thirteen days, 2026-08-18 → 08-30. Nine of the ten
transitions carry at least one substantive change — one that could move which
stocks qualify. Only v6 is a pure availability shift.

| version | date | change (**bold** = substantive) |
|---|---|---|
| v1 | 08-18 | first publication; screens named, no source lists |
| v2 | 08-19 | **source lists published; tier-2 defined; conflicting signals excluded** |
| v3 | 08-19 | **source substitutions under blocking** (MOAT ETF as a Morningstar proxy) |
| v4 | 08-20 | **conflicting signals disclosed with a flag instead of excluded** |
| v5 | 08-23 | **WebFetch prohibited** — screen B collapses to GuruFocus alone |
| v6 | 08-24 | available-source mix shifts again (no substantive change) |
| v7 | 08-26 | **methodology section absent from the file**; six picks published under rules that cannot be verified from the publication |
| v8 | 08-27 | **methodology restored, shortened**; markup moves to `data-ticker` |
| v9 | 08-28 | **screen B redeclared without GuruFocus**; WebFetch ban restated |
| v10 | 08-29 | **carry-forward rule added** — picks persist between runs |
| v11 | 08-30 | **carry-forward removed after one run; US-primary-listing requirement added** |

Two of these deserve to be read twice.

**v10's carry-forward** is the only rule in the history that turns *not
choosing* into a choice: 08-28's six picks were republished on 08-29 with no new
research behind them, because the Alpha Vantage quota was exhausted (0 of 18
calls succeeded). The rule existed for exactly one run and was removed the next
day. Rows published under a carry-forward version are re-publications, not entry
events, and `score.py` will not open a position from one.

**v7 has no methodology section at all.** Six tier-1 picks were published on
08-26 with the rules undocumented in the artifact. The version file records them
as `undocumented` rather than copying v6's rules forward — inheriting rules
nobody wrote down would be manufacturing evidence, which is the exact failure
this project exists to avoid.

## Files

- `versions/vN.json` — one frozen rule set. The artifact; edit these by hand.
- `resolve.py` — commit → version, plus freeze and verification.
- Each version carries `evidence`: the verbatim Hebrew clause from `index.html`
  at the commit cited, that establishes each rule.

## Why resolution is by commit, not by date

`2026-08-19` published two different versions (v2 in the morning, v3 later the
same day). A date lookup for that day is genuinely ambiguous, so
`version_for_date` raises rather than picking one. `version_for_commit` is the
real interface; the ledger uses it.

A commit no version claims resolves to `None`, and the ledger records a null
stamp. Never fill that in by proximity. An invented version stamp silently
licenses pooling picks made under different rules, which is worse than an
admitted gap because it cannot be seen afterwards.

## Change control

A version is immutable once its commits are published. To change the rules:

1. Copy the newest `vN.json` to `vN+1.json`.
2. Edit `selection`. Record every difference in `changes_from_previous`, with
   `type` (`deliberate` / `degraded` / `editorial` / `regression`) and
   `substantive` (does it change which stocks can qualify?). `degraded` means a
   source was unavailable, not that the rule was rewritten — the distinction
   matters when deciding whether picks from two versions belong in one sample.
3. List the publishing commits and quote the clause in `index.html` that
   establishes each new rule.
4. `python3 resolve.py --freeze` to stamp `rule_hash`.
5. `python3 resolve.py --verify` — must exit clean.

Never edit a frozen version's `selection` to match a later run. That is the
retroactive rewrite the whole track record is built to make impossible.

## Verification

```
python3 resolve.py --verify
```

Checks that every version's `rule_hash` matches its `selection` block, that no
commit is claimed twice, that every claimed commit exists and is dated inside
the version's range, and — the one that matters — that **every quoted rule is
still present in `index.html` at the commit it cites**. That last check is why
the evidence quotes are not merely decorative: the rule sets are falsifiable
against the hash-chained history, not just asserted.

Three transcription errors were caught by this check while the versions were
being written, and fixed against the committed HTML.

## Commands

```
python3 resolve.py --list              # versions, dates, commits, hashes
python3 resolve.py --commit 489b9f2    # -> v10
python3 resolve.py --diff v9 v10       # what changed, and whether it matters
python3 resolve.py --verify
```
