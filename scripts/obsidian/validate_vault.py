#!/usr/bin/env python3
"""Validate the homelab Obsidian vault against the governed vocabulary.

Read-only on the repository. Operates on the vault path as a separate system.
Never mutates canonical repository documentation.

Usage:
    python3 scripts/obsidian/validate_vault.py [--vault /mnt/monarch/obsidian-vault]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEFAULT_VAULT = Path("/mnt/monarch/obsidian-vault")

# ---- Controlled vocabulary (mirrors Documentation/ObsidianHomelabArchitecture.md) ----

APPROVED_TYPES = {
    "service", "architecture", "phase", "adr",
    "guide", "troubleshooting", "research", "moc",
}

APPROVED_STATUS = {"planned", "active", "deprecated", "retired"}

APPROVED_DOMAINS = {
    "infrastructure", "networking", "dns", "storage", "security", "identity",
    "ai", "monitoring", "automation", "media", "productivity", "development",
    "backup", "utilities",
}

APPROVED_TAGS = {
    "split-horizon", "dns", "reverse-proxy", "zfs", "storage", "secrets",
    "security-hardening", "migration", "retirement", "ai-orchestration",
    "memory", "knowledge", "observability", "backup", "sso", "automation",
    "media", "productivity", "development", "utilities", "infrastructure",
}

# Historical/retired technologies that must NOT appear as active on services
HISTORICAL_TECHNOLOGIES = {"pi-hole", "powerdns"}

# Controlled directories where stray files are flagged (templates/settings/mocs)
CONTROLLED_DIRS = {"Templates", "Settings", "MOCs"}

# Secret-ish patterns to detect in note bodies
SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|token|password|passwd|private[_-]?key)\s*[:=]\s*\S+"),
    re.compile(r"(?i)sk-[A-Za-z0-9]{20,}"),
    re.compile(r"(?i)AKIA[0-9A-Z]{16}"),
    re.compile(r"BEGIN (RSA |EC |OPENSSH |PGP )?PRIVATE KEY"),
]


def _real_phases() -> set[str]:
    """Derive real phase values from the canonical repository phase folders,
    including nested sub-phases (e.g. Phase14.2B under Phase14)."""
    phases = set()
    root = REPO / "Documentation"
    for d in root.glob("Phase*"):
        if not d.is_dir():
            continue
        # Top-level phase dir: Documentation/Phase12.2B -> "12.2B"
        if d.name != "Phases":
            phases.add(d.name.removeprefix("Phase"))
        # Nested sub-phase dirs: Documentation/Phase14/Phase14.2A -> "14.2A"
        for sub in d.glob("Phase*"):
            if sub.is_dir():
                phases.add(sub.name.removeprefix("Phase"))
    # Closeout files: Documentation/Phases/Phase14.2B_Closeout.md -> "14.2B"
    closeout_dir = root / "Phases"
    if closeout_dir.is_dir():
        for f in closeout_dir.glob("Phase*"):
            stem = f.stem.removeprefix("Phase")
            for suffix in ("_Closeout", "_Plan", "_Report", "_Completion_Report"):
                if stem.endswith(suffix):
                    stem = stem[: -len(suffix)]
            phases.add(stem)
    return phases


REAL_PHASES = _real_phases()


def _all_md_files(vault: Path) -> list[Path]:
    return [p for p in vault.rglob("*.md") if p.is_file()]


def _parse_yaml_block(text: str) -> tuple[dict | None, str | None]:
    """Return (frontmatter_dict, error). Accepts missing frontmatter (None, None)."""
    if not text.startswith("---"):
        return None, None
    # Split the first fenced YAML block
    lines = text.splitlines()
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return None, "unterminated frontmatter block"
    block = "\n".join(lines[1:end])
    try:
        import yaml
    except ImportError:
        return None, "PyYAML not installed (pip install pyyaml)"
    try:
        data = yaml.safe_load(block)
    except Exception as exc:  # noqa: BLE001
        return None, f"malformed YAML: {exc}"
    if data is None:
        return {}, None
    if not isinstance(data, dict):
        return None, "frontmatter is not a mapping"
    return data, None


def _as_list(value) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _wikilink_targets(text: str) -> list[str]:
    """Extract [[...]] wikilink targets from a note body."""
    return re.findall(r"\[\[([^\]|#]+)(?:[#|][^\]]*)?\]\]", text)


# Folders excluded from note-content checks (templates placeholders, vocab file)
TEMPLATES_DIR = "Templates"
SETTINGS_FILE = "Settings/tags.md"


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate the homelab Obsidian vault.")
    ap.add_argument("--vault", type=Path, default=DEFAULT_VAULT)
    args = ap.parse_args()

    vault: Path = args.vault
    if not vault.is_dir():
        print(f"FAIL vault-not-found: {vault}")
        return 1

    issues: list[tuple[str, str, str]] = []  # (check, path, message)
    checks: dict[str, list[str]] = {}
    failures = 0

    def report(check: str, path: str, ok: bool, msg: str = "") -> None:
        nonlocal failures
        checks.setdefault(check, [])
        if ok:
            checks[check].append(f"PASS {path}")
        else:
            failures += 1
            checks[check].append(f"FAIL {path} {msg}")

    files = _all_md_files(vault)
    report("files-discovered", str(vault), True, f"{len(files)} markdown files")

    # Build set of note names for duplicate detection and wikilink resolution.
    # Include the basename (without extension) of every markdown file so that
    # path-form and name-form wikilinks both resolve.
    names: set[str] = set()
    name_to_path: dict[str, list[Path]] = {}

    for path in files:
        rel = path.relative_to(vault).as_posix()
        stem = path.stem
        names.add(stem)
        names.add(rel.removesuffix(".md"))
        # walk each parent path segment so "MOCs/Architecture" and
        # "Architecture" both resolve
        parts = rel.removesuffix(".md").split("/")
        for i in range(1, len(parts) + 1):
            names.add("/".join(parts[:i]))

    for path in files:
        rel = path.relative_to(vault).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")

        # Templates hold placeholders (not real notes); Settings/tags.md is a
        # vocabulary file, not a note. Both are excluded from content checks.
        is_template = rel.startswith(TEMPLATES_DIR + "/")
        is_settings = rel == SETTINGS_FILE

        data, yerr = _parse_yaml_block(text)
        if yerr:
            report("yaml", rel, False, yerr)
            data = {}

        if is_template or is_settings:
            # Still check YAML parse + secrets, but skip note-content checks.
            continue

        # Approved note type
        ntype = data.get("type") if data else None
        report("type", rel, ntype in APPROVED_TYPES, f"type={ntype!r}")

        # Approved status (derived)
        status = data.get("status") if data else None
        if status is not None:
            report("status", rel, status in APPROVED_STATUS, f"status={status!r}")

        # Approved domains
        for d in _as_list(data.get("domain") if data else None):
            report("domain", rel, d in APPROVED_DOMAINS, f"domain={d!r}")

        # Approved tags (from Settings/tags.md vocabulary)
        if data and "tags" in data:
            for t in _as_list(data["tags"]):
                report("tags", rel, t in APPROVED_TAGS, f"tag={t!r}")
        else:
            report("tags", rel, False, "no tags property")

        # Valid phase references
        for ph in _as_list(data.get("phase") if data else None):
            report("phase", rel, ph in REAL_PHASES,
                   f"phase={ph!r} not in {sorted(REAL_PHASES)}")

        # canonical_source paths exist where present
        cs = data.get("canonical_source") if data else None
        if cs:
            cspath = REPO / str(cs)
            report("canonical_source", rel, cspath.exists(), f"missing: {cs}")

        # Duplicate note identities (by name)
        name = data.get("name") if data else None
        if name:
            key = str(name).strip().lower()
            if key in name_to_path:
                name_to_path[key].append(path)
            else:
                name_to_path[key] = [path]
                names.add(key)

        # Secrets
        for pat in SECRET_PATTERNS:
            if pat.search(text):
                report("secrets", rel, False, f"pattern {pat.pattern}")
                break
        else:
            report("secrets", rel, True)

        # Retired technologies must not be active on services
        if ntype == "service" and data:
            for t in _as_list(data.get("technologies")):
                if str(t).lower() in HISTORICAL_TECHNOLOGIES:
                    report("active-tech", rel, False,
                           f"historical tech listed as active: {t}")

        # Wikilink resolution (detectable targets)
        targets = _wikilink_targets(text)
        for tgt in targets:
            report("wikilink", rel, tgt in names, f"unresolved: [[{tgt}]]")

    # Duplicate identities across files
    for key, paths in name_to_path.items():
        if len(paths) > 1:
            report("duplicate", str(vault), False,
                   f"name '{key}' in {[p.name for p in paths]}")

    # Unexpected files in controlled directories
    for cdir in CONTROLLED_DIRS:
        cpath = vault / cdir
        if not cpath.is_dir():
            continue
        for p in cpath.iterdir():
            if p.is_dir():
                continue
            if p.suffix not in (".md", ".yaml", ".yml", ".json"):
                report("controlled", p.relative_to(vault).as_posix(), False,
                       "unexpected file in controlled dir")

    # Tags file vocabulary consistency: every tag used must be in Settings/tags.md
    tags_file = vault / "Settings" / "tags.md"
    approved_from_file: set[str] = set()
    if tags_file.exists():
        for line in tags_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            approved_from_file.add(line)
    # Cross-check tags actually used against the file vocabulary
    for path in files:
        rel = path.relative_to(vault).as_posix()
        if rel.startswith(TEMPLATES_DIR + "/") or rel == SETTINGS_FILE:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        data, _ = _parse_yaml_block(text)
        if data and "tags" in data:
            for t in _as_list(data["tags"]):
                if approved_from_file and t not in approved_from_file:
                    report("tags-file", rel, False,
                           f"tag {t} not in Settings/tags.md")

    # ---- Summary ----
    print("=" * 60)
    print("Homelab Obsidian Vault Validation")
    print(f"Vault: {vault}")
    print(f"Repository: {REPO}")
    print("=" * 60)
    for check in sorted(checks):
        lines = checks[check]
        n_pass = sum(1 for l in lines if l.startswith("PASS"))
        n_fail = sum(1 for l in lines if l.startswith("FAIL"))
        print(f"\n[{check}] {n_pass} pass / {n_fail} fail")
        for l in lines:
            print(f"  {l}")

    print("\n" + "=" * 60)
    print(f"RESULT: {'FAIL' if failures else 'PASS'} ({failures} issues)")
    print("=" * 60)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
