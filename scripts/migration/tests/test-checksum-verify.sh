#!/usr/bin/env bash
# Regression tests for the migration framework's checksum verification.
#
# Guards the Phase 11 / Jellyfin defect: verification compared two sorted
# checksum inventories positionally, under the operator's ambient locale. glibc
# UTF-8 collation gives many non-ASCII names equal weight, so `sort` left them
# in readdir order — which differs between the ZFS source and btrfs destination.
# Two byte-identical 11 GB trees were reported as a mismatch.
#
# These tests must keep passing under any locale, and must still catch real
# corruption: missing files, extra files, and changed content.
#
# Usage: scripts/migration/tests/test-checksum-verify.sh

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/common.sh"
set +e  # assertions handle their own failures

MIGRATE_QUIET=1

PASS=0
FAIL=0

pass() { PASS=$((PASS + 1)); printf 'ok   %s\n' "$1"; }
fail() { FAIL=$((FAIL + 1)); printf 'FAIL %s\n' "$1"; [[ -n "${2:-}" ]] && printf '       %s\n' "$2"; }

assert_eq() {
  local expected="$1" actual="$2" name="$3"
  if [[ "$expected" == "$actual" ]]; then pass "$name"; else fail "$name" "expected='$expected' actual='$actual'"; fi
}

# Deliberately awkward names: Hangul (the original failure), Japanese kana and
# kanji, accented/precomposed Latin, Cyrillic, emoji, spaces, and a name that is
# NFC vs NFD of the same text.
UNICODE_NAMES=(
  '이정훈.jpg'
  '김융희.jpg'
  '이/이정훈/folder.jpg'
  '日本語のファイル.txt'
  'ハローワールド.nfo'
  'Ångström.txt'
  'café.txt'
  'cafe\u0301.txt'
  'Ünter Straße.log'
  'Привет.txt'
  'movie 🎬 poster 😀.png'
  'plain-ascii.txt'
  'UPPER.TXT'
  'nested/deep/디렉터리/파일.dat'
)

make_tree() {
  # make_tree <root> <reverse:0|1> — same content either way, different creation
  # order so the two trees are unlikely to enumerate identically.
  local root="$1" reverse="${2:-0}"
  local -a names=("${UNICODE_NAMES[@]}")
  local i name
  mkdir -p "$root"
  if [[ "$reverse" == "1" ]]; then
    for ((i = ${#names[@]} - 1; i >= 0; i--)); do
      name="${names[$i]}"
      mkdir -p "$root/$(dirname "$name")"
      printf 'content of %s\n' "$name" >"$root/$name"
    done
  else
    for name in "${names[@]}"; do
      mkdir -p "$root/$(dirname "$name")"
      printf 'content of %s\n' "$name" >"$root/$name"
    done
  fi
}

TMPROOT="$(mktemp -d)"
trap 'rm -rf "$TMPROOT"' EXIT

SRC="$TMPROOT/src"
DST="$TMPROOT/dst"
make_tree "$SRC" 0
make_tree "$DST" 1

INV_A="$TMPROOT/inv_a"
INV_B="$TMPROOT/inv_b"
REPORT="$TMPROOT/report.txt"

echo "== checksum verification regression tests =="

# ---------------------------------------------------------------------------
# 1. Identical trees compare clean, despite Unicode names and creation order.
# ---------------------------------------------------------------------------
build_checksum_inventory "$SRC" "$INV_A"
assert_eq "0" "$INVENTORY_SKIPPED" "well-formed unicode names are not flagged unverifiable"
assert_eq "${#UNICODE_NAMES[@]}" "$INVENTORY_RECORDS" "one record per file"
build_checksum_inventory "$DST" "$INV_B"
rm -f "$REPORT"
compare_checksum_inventories "$INV_A" "$INV_B" "$REPORT"
assert_eq "0 0 0" "$CHECKSUM_MISSING $CHECKSUM_CHANGED $CHECKSUM_EXTRA" "identical unicode trees report no differences"
assert_eq "${#UNICODE_NAMES[@]}" "$CHECKSUM_MATCHED" "all unicode files matched"
assert_eq "false" "$([[ -s "$REPORT" ]] && echo true || echo false)" "no difference report written on success"

# ---------------------------------------------------------------------------
# 2. Inventory generation is locale-independent.
#    This is the specific regression: the same tree, inventoried under a UTF-8
#    locale and under C, must produce byte-identical output.
# ---------------------------------------------------------------------------
UTF8_LOCALE=""
for cand in en_US.UTF-8 en_US.utf8 C.UTF-8 C.utf8; do
  if locale -a 2>/dev/null | grep -qix "${cand/UTF-8/utf8}"; then UTF8_LOCALE="$cand"; break; fi
done

if [[ -n "$UTF8_LOCALE" ]]; then
  INV_C="$TMPROOT/inv_c"
  INV_D="$TMPROOT/inv_d"
  ( export LC_ALL="$UTF8_LOCALE" LANG="$UTF8_LOCALE" LC_COLLATE="$UTF8_LOCALE"
    source "$SCRIPT_DIR/../lib/common.sh"
    build_checksum_inventory "$SRC" "$INV_C" )
  ( export LC_ALL=C LANG=C LC_COLLATE=C
    source "$SCRIPT_DIR/../lib/common.sh"
    build_checksum_inventory "$SRC" "$INV_D" )
  if cmp -s "$INV_C" "$INV_D"; then
    pass "inventory identical under $UTF8_LOCALE and C"
  else
    fail "inventory identical under $UTF8_LOCALE and C" "$(diff "$INV_C" "$INV_D" | head -5)"
  fi

  # The underlying hazard still exists in the platform: confirm the ambient
  # locale really does tie these names, so this test keeps its teeth.
  ties="$(printf '%s\n' '이정훈' '김융희' | LC_ALL="$UTF8_LOCALE" sort -u | wc -l)"
  distinct="$(printf '%s\n' '이정훈' '김융희' | LC_ALL=C sort -u | wc -l)"
  if [[ "$ties" == "1" && "$distinct" == "2" ]]; then
    pass "platform collation tie confirmed under $UTF8_LOCALE (C keeps names distinct)"
  else
    pass "platform collation no longer ties these names (ties=$ties distinct=$distinct) — fix still required for other names"
  fi
else
  pass "skipped locale comparison — no UTF-8 locale available"
fi

# ---------------------------------------------------------------------------
# 3. Ordering of the record stream cannot change the verdict — the comparison
#    is keyed by path, so even an unsorted inventory compares correctly.
# ---------------------------------------------------------------------------
INV_SHUF="$TMPROOT/inv_shuf"
shuf "$INV_B" >"$INV_SHUF"
rm -f "$REPORT"
compare_checksum_inventories "$INV_A" "$INV_SHUF" "$REPORT"
assert_eq "0 0 0" "$CHECKSUM_MISSING $CHECKSUM_CHANGED $CHECKSUM_EXTRA" "unsorted record order still compares clean"

# ---------------------------------------------------------------------------
# 3b. Teeth check: replay the exact Phase 11 / Jellyfin failure.
#     Two inventories holding the same records, differing only in the order of
#     two collation-tied Hangul paths. The old positional `diff -q` fails; the
#     set comparison must not. If this test ever starts reporting differences,
#     the ordering bug has been reintroduced.
# ---------------------------------------------------------------------------
OLD_A="$TMPROOT/old_a"
OLD_B="$TMPROOT/old_b"
{
  printf 'data/metadata/People/F/Fumiya Imai/folder.jpg\t1949012578\t143914\n'
  printf 'data/metadata/People/이/이정훈/folder.jpg\t4048988276\t50863\n'
  printf 'data/metadata/People/김/김융희/folder.jpg\t3979359700\t80931\n'
} >"$OLD_A"
{
  printf 'data/metadata/People/F/Fumiya Imai/folder.jpg\t1949012578\t143914\n'
  printf 'data/metadata/People/김/김융희/folder.jpg\t3979359700\t80931\n'
  printf 'data/metadata/People/이/이정훈/folder.jpg\t4048988276\t50863\n'
} >"$OLD_B"

if diff -q "$OLD_A" "$OLD_B" >/dev/null 2>&1; then
  fail "fixture reproduces positional diff failure" "fixtures are byte-identical; ordering hazard not represented"
else
  pass "fixture reproduces the old positional diff failure"
fi

rm -f "$REPORT"
compare_checksum_inventories "$OLD_A" "$OLD_B" "$REPORT"
assert_eq "0 0 0" "$CHECKSUM_MISSING $CHECKSUM_CHANGED $CHECKSUM_EXTRA" "set comparison immune to Hangul ordering (Jellyfin regression)"
assert_eq "3" "$CHECKSUM_MATCHED" "all reordered records matched"

# Canonicalisation makes the two orderings converge to identical files.
LC_ALL=C sort -t$'\t' -k1,1 -o "$OLD_A" "$OLD_A"
LC_ALL=C sort -t$'\t' -k1,1 -o "$OLD_B" "$OLD_B"
if cmp -s "$OLD_A" "$OLD_B"; then
  pass "LC_ALL=C canonicalisation converges both orderings"
else
  fail "LC_ALL=C canonicalisation converges both orderings" "$(diff "$OLD_A" "$OLD_B" | head -5)"
fi

# ---------------------------------------------------------------------------
# 4. Verification is NOT weakened — real defects are still caught, by name.
# ---------------------------------------------------------------------------

# 4a. Missing file at destination.
BROKEN="$TMPROOT/dst_missing"
cp -a "$DST" "$BROKEN"
rm -f "$BROKEN/이정훈.jpg"
build_checksum_inventory "$BROKEN" "$INV_B"
rm -f "$REPORT"
compare_checksum_inventories "$INV_A" "$INV_B" "$REPORT"
assert_eq "1" "$CHECKSUM_MISSING" "missing unicode file detected"
assert_eq "true" "$(grep -q $'^MISSING\t이정훈.jpg' "$REPORT" && echo true || echo false)" "missing file named in report"

# 4b. Extra file at destination.
BROKEN="$TMPROOT/dst_extra"
cp -a "$DST" "$BROKEN"
printf 'unexpected\n' >"$BROKEN/침입자.txt"
build_checksum_inventory "$BROKEN" "$INV_B"
rm -f "$REPORT"
compare_checksum_inventories "$INV_A" "$INV_B" "$REPORT"
assert_eq "1" "$CHECKSUM_EXTRA" "extra unicode file detected"
assert_eq "true" "$(grep -q $'^EXTRA\t침입자.txt' "$REPORT" && echo true || echo false)" "extra file named in report"

# 4c. Changed content, same byte length — size checks alone would miss this.
BROKEN="$TMPROOT/dst_changed"
cp -a "$DST" "$BROKEN"
orig_size="$(stat -c %s "$BROKEN/日本語のファイル.txt")"
printf 'X%.0s' $(seq 1 "$orig_size") >"$BROKEN/日本語のファイル.txt"
build_checksum_inventory "$BROKEN" "$INV_B"
rm -f "$REPORT"
compare_checksum_inventories "$INV_A" "$INV_B" "$REPORT"
assert_eq "1" "$CHECKSUM_CHANGED" "same-size content change detected"
assert_eq "true" "$(grep -q $'^CHANGED\t日本語のファイル.txt' "$REPORT" && echo true || echo false)" "changed file named in report"

# 4d. Truncated file.
BROKEN="$TMPROOT/dst_trunc"
cp -a "$DST" "$BROKEN"
: >"$BROKEN/movie 🎬 poster 😀.png"
build_checksum_inventory "$BROKEN" "$INV_B"
rm -f "$REPORT"
compare_checksum_inventories "$INV_A" "$INV_B" "$REPORT"
assert_eq "1" "$CHECKSUM_CHANGED" "truncated emoji-named file detected"

# ---------------------------------------------------------------------------
# 5. rsync_excludes are honoured, so deliberately-skipped files are not
#    misreported as missing — but a genuinely missing file still is.
# ---------------------------------------------------------------------------
EXSRC="$TMPROOT/ex_src"
EXDST="$TMPROOT/ex_dst"
mkdir -p "$EXSRC/downloads/한국" "$EXSRC/keep" "$EXDST/keep"
printf 'big\n' >"$EXSRC/downloads/한국/영화.mkv"
printf 'log\n' >"$EXSRC/service.log"
printf 'keep\n' >"$EXSRC/keep/설정.xml"
printf 'keep\n' >"$EXDST/keep/설정.xml"

build_checksum_inventory "$EXSRC" "$INV_A" 'downloads/**,*.log'
build_checksum_inventory "$EXDST" "$INV_B"
rm -f "$REPORT"
compare_checksum_inventories "$INV_A" "$INV_B" "$REPORT"
assert_eq "0 0 0" "$CHECKSUM_MISSING $CHECKSUM_CHANGED $CHECKSUM_EXTRA" "excluded paths not reported as differences"
assert_eq "1" "$CHECKSUM_MATCHED" "only non-excluded file compared"

rm -f "$EXDST/keep/설정.xml"
build_checksum_inventory "$EXDST" "$INV_B"
rm -f "$REPORT"
compare_checksum_inventories "$INV_A" "$INV_B" "$REPORT"
assert_eq "1" "$CHECKSUM_MISSING" "non-excluded missing file still detected with excludes active"

# ---------------------------------------------------------------------------
# 6. Names that cannot be represented in the record format must fail closed,
#    never silently reduce the set of verified files.
# ---------------------------------------------------------------------------
NLDIR="$TMPROOT/newline"
mkdir -p "$NLDIR"
printf 'a\n' >"$NLDIR/normal.txt"
printf 'b\n' >"$NLDIR/bad"$'\n'"name.txt"
build_checksum_inventory "$NLDIR" "$INV_A"
if (( INVENTORY_SKIPPED > 0 )); then
  pass "newline in filename flagged as unverifiable (skipped=$INVENTORY_SKIPPED)"
else
  fail "newline in filename flagged as unverifiable" "INVENTORY_SKIPPED=0"
fi

TABDIR="$TMPROOT/tabname"
mkdir -p "$TABDIR"
printf 'a\n' >"$TABDIR/normal.txt"
printf 'b\n' >"$TABDIR/bad"$'\t'"name.txt"
build_checksum_inventory "$TABDIR" "$INV_A"
if (( INVENTORY_SKIPPED > 0 )); then
  pass "tab in filename flagged as unverifiable (skipped=$INVENTORY_SKIPPED)"
else
  fail "tab in filename flagged as unverifiable" "INVENTORY_SKIPPED=0"
fi

echo
echo "passed=$PASS failed=$FAIL"
(( FAIL == 0 )) || exit 1
