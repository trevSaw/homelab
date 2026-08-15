#!/bin/sh
# KORA → canonical-repo apply helper (approval-gated).
#
# KORA drafts and commits in its hermes-owned workspace clone:
#   /mnt/monarch/appdata/hermes/homelab-workspace  (container: /opt/data/homelab-workspace)
# The canonical repo (/home/fatherfrank/projects/homelab) is NOT mounted into
# Hermes (it contains gitignored .env secrets). This script is the approval-
# gated bridge: it shows what KORA proposes and applies it to the canonical
# repo ONLY after explicit confirmation. KORA itself never writes the canonical
# repo and has no push/remote capability.
#
# Usage:
#   scripts/kora-apply.sh [--commit] [patch-file]
#     patch-file      path to a .patch/.diff (default: workspace 'kora.patch'
#                     or the workspace diff itself)
#     --commit        also commit the applied changes (author = KORA)
set -e

CANONICAL_REPO="${CANONICAL_REPO:-/home/fatherfrank/projects/homelab}"
WORKSPACE="${WORKSPACE:-/mnt/monarch/appdata/hermes/homelab-workspace}"
COMMIT=0
PATCH=""

for a in "$@"; do
  case "$a" in
    --commit) COMMIT=1 ;;
    *) PATCH="$a" ;;
  esac
done

[ -d "$CANONICAL_REPO/.git" ] || { echo "ERROR: canonical repo not found at $CANONICAL_REPO"; exit 1; }

if [ -z "$PATCH" ]; then
  if [ -f "$WORKSPACE/kora.patch" ]; then
    PATCH="$WORKSPACE/kora.patch"
  else
    PATCH="$WORKSPACE/kora.patch"
    # Generate the diff from the workspace working tree vs its HEAD.
    git -C "$WORKSPACE" diff > "$PATCH"
  fi
fi

[ -s "$PATCH" ] || { echo "No patch to apply (patch empty): $PATCH"; echo "KORA: run: git -C $WORKSPACE diff > $WORKSPACE/kora.patch"; exit 1; }

echo "=== Proposed change (stat) ==="
git -C "$CANONICAL_REPO" apply --stat "$PATCH"
echo
echo "=== Full diff preview ==="
cat "$PATCH"
echo
printf "Apply this to the canonical repo? [y/N] "
read -r ans
case "$ans" in
  y|Y|yes|YES)
    git -C "$CANONICAL_REPO" apply --check "$PATCH" && git -C "$CANONICAL_REPO" apply "$PATCH"
    echo "Applied to $CANONICAL_REPO."
    if [ "$COMMIT" = 1 ]; then
      git -C "$CANONICAL_REPO" add -A
      git -C "$CANONICAL_REPO" commit -m "kora(apply): $(head -1 "$PATCH" 2>/dev/null)" --author="KORA <kora@homelab.local>" 2>/dev/null \
        || git -C "$CANONICAL_REPO" commit -m "kora(apply): apply KORA-proposed changes" --author="KORA <kora@homelab.local>"
      echo "Committed."
    fi
    echo "Review: git -C $CANONICAL_REPO status"
    ;;
  *)
    echo "Aborted — nothing applied."
    exit 1
    ;;
esac
