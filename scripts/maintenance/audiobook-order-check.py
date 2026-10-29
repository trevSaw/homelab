#!/usr/bin/env python3
"""
audiobook-order-check.py — Audiobook file-ordering validator.

Detects interleaved leading sequence numbers in multi-part audiobooks
(e.g. GraphicAudio releases such as "Red Rising - GraphicAudio") where the
leading NNN prefix on each file is not a clean 1..N sequence across parts.

Naming convention understood (GraphicAudio style):
    001_REDRISING0101P01.mp3
     ^   ^        ^^  ^^
     |   |        |   +-- track within part  (P01..P99)
     |   |        +------ part id            (0101 = Part 1, 0102 = Part 2)
     |   +--------------- release code       (preserved, never modified)
     +------------------- leading sequence   (the ONLY thing this tool may
                                               change, and only when the order
                                               is provably wrong)

Primary source of truth: Audiobookshelf metadata, read READ-ONLY via the
Audiobookshelf container (the host sqlite3/Python cannot open ABS's newer
SQLite schema). The real filesystem is then cross-checked on the host; the
filesystem filenames are ground truth for any rename.

Default mode is REPORT-ONLY and never modifies anything.
`--apply --confirm` performs an explicit, collision-checked, two-stage
rename of the leading-number prefix only. Nothing is ever scheduled.

Safety invariants (hard-coded):
  * read-only unless --apply --confirm is given
  * changes the leading-number prefix only
  * never deletes any file
  * collision detection before any rename
  * two-stage rename (via temp names) so targets never clobber sources
  * confirmation required per book before applying
  * single-part, single-file, and unparseable books are skipped (no flag)
"""

import argparse
import json
import os
import re
import subprocess
import sys

LIBRARY_DEFAULT = "/hive/library/Audiobooks"
CONTAINER_DEFAULT = "audiobookshelf"
CONTAINER_MOUNT_DEFAULT = "/audiobooks"

AUDIO_EXTS = {".mp3", ".m4b", ".m4a", ".flac", ".aac", ".ogg", ".opus", ".wma"}

LEADING_RE = re.compile(r"^(\d+)_(.+)$")
PART_RE = re.compile(r"010(\d+)", re.I)            # 0101 -> part 1, 0102 -> part 2
TRACK_RE = re.compile(r"P(\d+)(?:\.\w+)?$", re.I)  # P01, P02, ... before extension

# Read-only query executed inside the ABS container via `node -` (stdin).
NODE_QUERY = r"""
const sqlite3 = require('sqlite3');
const db = new sqlite3.Database('/config/absdatabase.sqlite', sqlite3.OPEN_READONLY);
db.all(`SELECT li.id AS itemId, li.path AS itemPath, b.id AS bookId, b.audioFiles
        FROM libraryItems li JOIN books b ON b.id = li.mediaId
        WHERE li.mediaType = 'book'`, (e, rows) => {
  if (e) { console.error('ERR ' + e.message); process.exit(1); }
  const out = rows.map(r => {
    let files = [];
    try { files = JSON.parse(r.audioFiles || '[]'); } catch (_) {}
    return {
      itemId: r.itemId,
      path: r.itemPath,
      files: files.map(f => ({
        index: f.index,
        filename: (f.metadata && f.metadata.filename) || null,
        duration: f.duration || null,
        tagAlbum: (f.metaTags && f.metaTags.tagAlbum) || null,
        tagTrack: (f.metaTags && f.metaTags.tagTrack) || null
      }))
    };
  });
  console.log(JSON.stringify(out));
  db.close();
});
"""


class CollisionError(Exception):
    """Raised when a proposed rename would overwrite an unrelated file."""


# ---------------------------------------------------------------- parsing ---

def parse_filename(fn):
    """Return (leading:int, part:int, track:int, suffix:str) or None if the
    filename does not follow the GraphicAudio convention."""
    m = LEADING_RE.match(fn)
    if not m:
        return None
    leading = int(m.group(1))
    suffix = m.group(2)
    pm = PART_RE.search(fn)
    tm = TRACK_RE.search(fn)
    if not pm or not tm:
        return None
    return leading, int(pm.group(1)), int(tm.group(1)), suffix


def detect_book(filenames):
    """
    Analyse one audiobook directory.

    filenames: list of audio file basenames present on disk.

    Returns a dict:
      status  : 'ok' | 'flagged' | 'single_part' | 'single_file' | 'unparseable'
      reason  : human-readable explanation
      parts   : {part: [filenames]}  (sorted)
      mapping : [{'old','new','changed'}]  for flagged books only
      changes : number of files that would be renamed (flagged only)
    """
    base = {
        "status": None, "reason": "", "parts": {},
        "mapping": [], "changes": 0,
    }

    if len(filenames) < 2:
        base["status"] = "single_file"
        base["reason"] = f"{len(filenames)} audio file(s); nothing to reorder"
        return base

    parsed = []
    for fn in filenames:
        p = parse_filename(fn)
        if p is None:
            base["status"] = "unparseable"
            base["reason"] = f"filename does not follow GraphicAudio convention: {fn}"
            return base
        parsed.append((p[0], p[1], p[2], fn))  # leading, part, track, name

    # Group by part.
    parts = {}
    for leading, part, track, fn in parsed:
        parts.setdefault(part, []).append((track, fn))

    if len(parts) < 2:
        base["status"] = "single_part"
        base["reason"] = f"single part detected ({len(filenames)} file(s)); nothing to interleave"
        return base

    # Every part must have tracks exactly 1..N (provable grouping only).
    for part, tracks in sorted(parts.items()):
        nums = sorted(t for t, _ in tracks)
        if nums != list(range(1, len(nums) + 1)):
            base["status"] = "unparseable"
            base["reason"] = f"part {part:02d} track numbers are not a clean 1..N sequence: {nums}"
            return base

    base["parts"] = {part: [fn for _, fn in sorted(tracks)] for part, tracks in sorted(parts.items())}

    # Expected overall order: sort by part, then by track; leading = 1..N.
    expected = []
    for part in sorted(parts):
        for track, fn in sorted(parts[part]):
            expected.append((part, track, fn))

    width = max(3, len(str(len(expected))))
    mapping = []
    for i, (part, track, fn) in enumerate(expected, start=1):
        new_leading = f"{i:0{width}d}"
        m = LEADING_RE.match(fn)
        old_leading = m.group(1)
        new_fn = new_leading + "_" + m.group(2)
        mapping.append({
            "old": fn,
            "new": new_fn,
            "changed": old_leading != new_leading,
        })
    changes = sum(1 for m in mapping if m["changed"])

    # Contradiction detection — flag ONLY on a provable inconsistency.
    reasons = []

    # (a) same leading number used by >=2 different parts (interleaving signature)
    leading_parts = {}
    for leading, part, _, fn in parsed:
        leading_parts.setdefault(leading, set()).add(part)
    dup = sorted(l for l, ps in leading_parts.items() if len(ps) > 1)
    if dup:
        reasons.append(f"leading number(s) shared across parts: {dup}")

    # (b) leading-number set is not a bijection of 1..N
    current_leads = sorted(l for l, _, _, _ in parsed)
    if current_leads != list(range(1, len(parsed) + 1)):
        reasons.append("leading-number set is not a clean 1..N sequence")

    # (c) current order contradicts (part, track) order
    by_lead = sorted(parsed, key=lambda x: x[0])
    expected_key = [ (part, track) for part, track, _ in expected ]
    current_key = [ (part, track) for _, part, track, _ in by_lead ]
    if current_key != expected_key:
        reasons.append("leading-number order contradicts (part, track) order")

    if not reasons:
        base["status"] = "ok"
        base["reason"] = f"{len(filenames)} files, {len(parts)} parts; ordering consistent ({'–'.join([mapping[0]['new'][:3], mapping[-1]['new'][:3]])})"
        base["mapping"] = mapping
        base["changes"] = 0
        return base

    base["status"] = "flagged"
    base["reason"] = "interleaved numbering: " + "; ".join(reasons)
    base["mapping"] = mapping
    base["changes"] = changes
    return base


# ---------------------------------------------------------------- ABS read ---

def read_abs_metadata(container):
    """Query Audiobookshelf DB read-only via the container. Returns a list of
    {itemId, path (container), files:[{index,filename,tagAlbum,tagTrack}]}."""
    try:
        proc = subprocess.run(
            ["docker", "exec", "-i", container, "sh", "-c", "cd /app && node -"],
            input=NODE_QUERY,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except Exception as e:  # docker missing, container down, timeout, ...
        return None, f"could not query ABS container ({e})"

    if proc.returncode != 0:
        return None, proc.stderr.strip() or f"ABS query exited {proc.returncode}"

    try:
        return json.loads(proc.stdout), None
    except json.JSONDecodeError as e:
        return None, f"ABS query returned invalid JSON ({e})"


def abs_path_to_host(abs_path, container_mount, library):
    if not abs_path:
        return None
    if abs_path.startswith(container_mount):
        return os.path.join(library, abs_path[len(container_mount):].lstrip("/"))
    return None


# ------------------------------------------------------------ discovery -----

def find_book_dirs(library):
    """Return list of (abs_dir) host dirs that directly contain audio files."""
    found = []
    for root, dirs, files in os.walk(library):
        dirs[:] = sorted(d for d in dirs if not d.startswith("."))
        has_audio = any(
            f.lower().endswith(tuple(AUDIO_EXTS)) and not f.startswith(".")
            for f in files
        )
        if has_audio:
            found.append(root)
    return sorted(found)


def list_audio_files(directory):
    return sorted(
        f for f in os.listdir(directory)
        if f.lower().endswith(tuple(AUDIO_EXTS)) and not f.startswith(".")
    )


# --------------------------------------------------------------- apply -----

def collision_check(directory, mapping):
    """Raise CollisionError if a target name would overwrite an unrelated file."""
    existing = set(os.listdir(directory))
    vacated = {m["old"] for m in mapping if m["changed"]}
    targets = [m["new"] for m in mapping if m["changed"]]

    if len(set(targets)) != len(targets):
        raise CollisionError("proposed rename produces duplicate target names")

    problems = []
    for t in targets:
        if t in existing and t not in vacated:
            problems.append(f"target exists and is not vacated by this fix: {t}")
    if problems:
        raise CollisionError("; ".join(problems))


def two_stage_rename(directory, mapping):
    """Apply a two-stage rename (temp names -> final names). Never deletes.
    Returns the number of files renamed. Raises CollisionError on collision."""
    changes = [m for m in mapping if m["changed"]]
    if not changes:
        return 0

    collision_check(directory, mapping)

    # Stage 1: move every source to a unique temp name.
    staged = []
    for i, m in enumerate(changes):
        src = os.path.join(directory, m["old"])
        tmp = os.path.join(directory, f".orderfix-{os.getpid()}-{i}.tmp")
        os.rename(src, tmp)
        staged.append((tmp, os.path.join(directory, m["new"]), src))

    # Stage 2: temp -> final. On failure, roll back to the original names.
    try:
        for tmp, dst, _ in staged:
            os.rename(tmp, dst)
    except Exception as e:
        for tmp, _, src in staged:
            if os.path.exists(tmp) and not os.path.exists(src):
                os.rename(tmp, src)
        raise RuntimeError(f"rename failed and was rolled back: {e}")

    return len(changes)


# --------------------------------------------------------------- reporting --

def print_mapping(mapping, indent="       "):
    for m in mapping:
        marker = " (no change)" if not m["changed"] else ""
        print(f"{indent}{m['old']} -> {m['new']}{marker}")


# ------------------------------------------------------------------- main ---

def build_parser():
    p = argparse.ArgumentParser(
        description="Validate audiobook file ordering (report-only by default).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            f"  python3 {os.path.basename(__file__)}                              # report, whole library\n"
            f"  python3 {os.path.basename(__file__)} --book 'Pierce Brown/Red Rising - GraphicAudio'\n"
            f"  python3 {os.path.basename(__file__)} --apply --confirm           # explicit fix (interactive)\n"
        ),
    )
    p.add_argument("--library", default=LIBRARY_DEFAULT,
                   help=f"host audiobook root (default: {LIBRARY_DEFAULT})")
    p.add_argument("--container", default=CONTAINER_DEFAULT,
                   help=f"Audiobookshelf container name (default: {CONTAINER_DEFAULT})")
    p.add_argument("--container-mount", default=CONTAINER_MOUNT_DEFAULT,
                   help=f"ABS container mount point for the library (default: {CONTAINER_MOUNT_DEFAULT})")
    p.add_argument("--report", action="store_true",
                   help="report-only (default behavior; never modifies anything)")
    p.add_argument("--apply", action="store_true",
                   help="apply renames for flagged books (requires --confirm)")
    p.add_argument("--confirm", action="store_true",
                   help="show exact old->new mapping and require confirmation before applying")
    p.add_argument("--json", action="store_true",
                   help="machine-readable JSON output (report mode)")
    p.add_argument("--book", metavar="SUBPATH",
                   help="restrict to one book dir relative to --library, "
                        "e.g. 'Pierce Brown/Red Rising - GraphicAudio'")
    p.add_argument("--no-db", action="store_true",
                   help="skip the Audiobookshelf DB lookup; filesystem-only analysis")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)

    if args.apply and not args.confirm:
        print("ERROR: --apply requires --confirm (renames must be explicitly confirmed).",
              file=sys.stderr)
        return 2

    if not os.path.isdir(args.library):
        print(f"ERROR: library directory not found: {args.library}", file=sys.stderr)
        return 2

    # Resolve the target set of book directories.
    if args.book:
        target = os.path.normpath(os.path.join(args.library, args.book))
        if not target.startswith(os.path.normpath(args.library)) or not os.path.isdir(target):
            print(f"ERROR: --book directory not found under library: {args.book}",
                  file=sys.stderr)
            return 2
        book_dirs = [target]
    else:
        book_dirs = find_book_dirs(args.library)

    # ABS metadata (primary source of truth), read-only.
    abs_items = None
    abs_warning = None
    if not args.no_db:
        abs_items, abs_warning = read_abs_metadata(args.container)
        if abs_items is None:
            print(f"WARNING: Audiobookshelf metadata unavailable ({abs_warning}); "
                  "continuing filesystem-only.", file=sys.stderr)
            abs_items = []

    abs_by_host = {}
    for it in abs_items or []:
        host = abs_path_to_host(it.get("path"), args.container_mount, args.library)
        if host:
            abs_by_host[host] = it

    results = []
    for d in book_dirs:
        rel = os.path.relpath(d, args.library)
        filenames = list_audio_files(d)
        det = detect_book(filenames)

        # Cross-check against ABS metadata for corroboration notes.
        abs_note = ""
        abs_item = abs_by_host.get(d)
        if abs_item:
            abs_names = [f["filename"] for f in abs_item.get("files", []) if f.get("filename")]
            if abs_names and sorted(abs_names) != sorted(filenames):
                abs_note = " [WARNING: ABS metadata filenames differ from disk]"
            elif det["status"] in ("flagged", "ok"):
                # Corroborate part grouping from album/track tags when available.
                tag_albums = sorted({f.get("tagAlbum") for f in abs_item.get("files", []) if f.get("tagAlbum")})
                if len(tag_albums) > 1:
                    abs_note = f" [ABS corroboration: album tags = {tag_albums[0]} | {tag_albums[-1]}]"

        results.append({
            "dir": d,
            "rel": rel,
            "det": det,
            "abs_note": abs_note,
        })

    # ------------------------------------------------------------ report ----
    if not args.apply:
        if args.json:
            print(json.dumps([
                {
                    "book": r["rel"],
                    "status": r["det"]["status"],
                    "reason": r["det"]["reason"],
                    "parts": r["det"]["parts"],
                    "mapping": r["det"]["mapping"],
                    "changes": r["det"]["changes"],
                }
                for r in results
            ], indent=2))
            return 0

        print(f"=== Audiobook Ordering Check ===")
        print(f"Library: {args.library}")
        print(f"Mode: report (read-only) — no changes made")
        print()
        for r in results:
            d = r["det"]
            print(f"[{d['status'].upper()}] {r['rel']}")
            print(f"       {d['reason']}{r['abs_note']}")
            if d["status"] == "flagged":
                print(f"       {d['changes']} of {len(d['mapping'])} file(s) would be renamed:")
                print_mapping(d["mapping"])
            print()
        flagged = [r for r in results if r["det"]["status"] == "flagged"]
        print(f"Summary: {len(results)} book(s) checked, "
              f"{len(flagged)} flagged (use --apply --confirm to fix), "
              f"0 changes made.")
        return 0

    # ------------------------------------------------------------- apply ----
    flagged = [r for r in results if r["det"]["status"] == "flagged"]
    if not flagged:
        print("No flagged audiobooks found. Nothing to apply.")
        return 0

    total_renamed = 0
    for r in flagged:
        d = r["det"]
        print(f"[FLAGGED] {r['rel']}")
        print(f"         {d['reason']}")
        print_mapping(d["mapping"])
        try:
            ans = input(f"Apply {d['changes']} rename(s) in this book? [y/N] ").strip().lower()
        except EOFError:
            ans = ""
        if ans not in ("y", "yes"):
            print("         skipped (no changes made).")
            continue
        try:
            n = two_stage_rename(r["dir"], d["mapping"])
            total_renamed += n
            print(f"         applied {n} rename(s).")
        except CollisionError as e:
            print(f"         REFUSED (collision): {e}. No changes made for this book.")
        except (OSError, RuntimeError) as e:
            print(f"         ERROR: {e}. No changes applied for this book.")

    print()
    print(f"Total renames applied: {total_renamed}.")
    print("NOTE: run an Audiobookshelf scan so it picks up the corrected filenames.")
    return 0


if __name__ == "__main__":
    sys.exit(main())