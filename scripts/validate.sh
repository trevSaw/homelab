#!/usr/bin/env bash
# Homelab Phase 10 validation — safe to run locally (read-only checks).
# Does not start, stop, or recreate containers.
set -euo pipefail

export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin${PATH:+:$PATH}"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PASS=0
FAIL=0
WARN=0
SKIP=0

pass() { PASS=$((PASS + 1)); echo "  PASS  $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  FAIL  $1"; }
warn() { WARN=$((WARN + 1)); echo "  WARN  $1"; }
skip() { SKIP=$((SKIP + 1)); echo "  SKIP  $1"; }

echo "=========================================="
echo " Homelab Validation"
echo " Repo: $ROOT"
echo "=========================================="
echo

###############################################################################
# 1. Shell syntax
###############################################################################
echo "## Shell syntax (bash -n)"
while IFS= read -r -d '' script; do
  # Skip archived historical copies from hard failure gate
  case "$script" in
    */Scripts/audit/archive/*) continue ;;
  esac
  if bash -n "$script" 2>/dev/null; then
    pass "bash -n ${script#$ROOT/}"
  else
    fail "bash -n ${script#$ROOT/}"
  fi
done < <(find "$ROOT/Scripts" -type f -name '*.sh' -print0 2>/dev/null)

echo

###############################################################################
# 2. Compose files present + YAML parse (when docker compose available)
###############################################################################
echo "## Compose validation"
mapfile -t COMPOSE_FILES < <(
  find "$ROOT/Services" -type f \( \
    -name 'compose.yml' -o -name 'compose.yaml' -o \
    -name 'docker-compose.yml' -o -name 'docker-compose.yaml' \
  \) ! -path '*/needing-to-be-deleted/*' | sort
)

if [[ ${#COMPOSE_FILES[@]} -eq 0 ]]; then
  fail "No compose files found under Services/"
else
  pass "Found ${#COMPOSE_FILES[@]} compose file(s)"
fi

if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
  for cf in "${COMPOSE_FILES[@]}"; do
    dir="$(dirname "$cf")"
    base="$(basename "$cf")"
    # Config-only validation; does not pull images or start containers.
    # Missing .env secrets may cause interpolation warnings; treat hard errors as FAIL.
    if (
      cd "$dir"
      docker compose -f "$base" config --quiet >/dev/null 2>"$ROOT/.validate_compose_err"
    ); then
      pass "compose config ${cf#$ROOT/}"
    else
      # Soft-fail when only env interpolation is incomplete (common off-host)
      if grep -qiE 'variable is not set|required variable|no such file|env file' "$ROOT/.validate_compose_err" 2>/dev/null; then
        warn "compose config ${cf#$ROOT/} (env/interpolation incomplete off-host)"
      else
        fail "compose config ${cf#$ROOT/}"
        sed 's/^/         /' "$ROOT/.validate_compose_err" 2>/dev/null | head -n 8 || true
      fi
    fi
  done
  rm -f "$ROOT/.validate_compose_err"
else
  skip "docker compose not available — YAML schema checks skipped"
fi
echo

###############################################################################
# 3. Secret hygiene — no obvious plaintext secrets in tracked compose
###############################################################################
echo "## Secret hygiene (compose)"
SECRET_HITS=0
while IFS= read -r -d '' cf; do
  case "$cf" in
    */needing-to-be-deleted/*) continue ;;
  esac
  # Flag likely inline secrets (API keys, passwords, tokens) while allowing ${VAR}
  if grep -nE \
    '(PASSWORD|SECRET|TOKEN|API_KEY|AUTHENTIK_SECRET_KEY)\s*[:=]\s*["'\'']?[^{$"'\''#][^"'\''[:space:]]{8,}' \
    "$cf" 2>/dev/null | grep -vE '\$\{|change_me|example|GENERATE|openssl' >/dev/null; then
    fail "possible plaintext secret in ${cf#$ROOT/}"
    grep -nE \
      '(PASSWORD|SECRET|TOKEN|API_KEY|AUTHENTIK_SECRET_KEY)\s*[:=]' \
      "$cf" | head -n 5 | sed 's/^/         /' || true
    SECRET_HITS=$((SECRET_HITS + 1))
  fi
done < <(find "$ROOT/Services" -type f \( -name 'compose.yml' -o -name 'compose.yaml' -o -name 'docker-compose.yml' -o -name 'docker-compose.yaml' \) -print0)

if (( SECRET_HITS == 0 )); then
  pass "No obvious plaintext secret assignments in compose files"
fi
echo

###############################################################################
# 4. Logging rotation present
###############################################################################
echo "## Logging rotation"
MISSING_LOG=0
for cf in "${COMPOSE_FILES[@]}"; do
  if ! grep -q 'max-size:' "$cf"; then
    warn "logging max-size missing: ${cf#$ROOT/}"
    MISSING_LOG=$((MISSING_LOG + 1))
  fi
done
if (( MISSING_LOG == 0 )); then
  pass "All active compose files declare logging max-size"
fi
echo

###############################################################################
# 5. Restart policy
###############################################################################
echo "## Restart policy"
MISSING_RESTART=0
for cf in "${COMPOSE_FILES[@]}"; do
  if ! grep -qE 'restart:\s*(unless-stopped|always|on-failure)' "$cf"; then
    warn "restart policy missing/unclear: ${cf#$ROOT/}"
    MISSING_RESTART=$((MISSING_RESTART + 1))
  fi
done
if (( MISSING_RESTART == 0 )); then
  pass "Restart policies present on active compose files"
fi
echo

###############################################################################
# 6. .env.example for secret-bearing services
###############################################################################
echo "## .env.example coverage"
for svc in ollama beszel_agent hermes code-server honcho n8n; do
  if [[ -f "$ROOT/Services/$svc/.env.example" ]]; then
    pass "Services/$svc/.env.example"
  else
    fail "Services/$svc/.env.example missing"
  fi
done
if [[ -f "$ROOT/Services/.env.example" ]]; then
  pass "Services/.env.example"
else
  fail "Services/.env.example missing"
fi
echo

###############################################################################
# 7. Markdown structure (lightweight)
###############################################################################
echo "## Markdown presence"
for f in \
  "Scripts/audit/README.md" \
  "Scripts/audit/sample_energy_report.md" \
  "Validation/README.md" \
  "Architecture/standards/StandardsRoadmap.md" \
  "Validation/Phase10/Phase10_Completion_Report.md" \
  "Validation/Phase10/Summary.md" \
  "Validation/Phase10/Remaining_Risks.md" \
  "Validation/Phase10/Validation_Checklist.md"
do
  if [[ -f "$ROOT/$f" ]]; then
    pass "$f"
  else
    fail "missing $f"
  fi
done
echo

###############################################################################
# 8. Broken relative markdown links (best-effort, repo-local)
###############################################################################
echo "## Markdown link spot-check (Phase10 + audit README)"
LINK_FAIL=0
check_md_links() {
  local md="$1"
  [[ -f "$md" ]] || return 0
  local dir
  dir="$(dirname "$md")"
  # Match markdown links: [text](path) excluding http(s) and anchors
  while IFS= read -r link; do
    [[ -z "$link" ]] && continue
    case "$link" in
      http://*|https://*|mailto:*|\#*) continue ;;
    esac
    # Strip anchors
    local path="${link%%#*}"
    [[ -z "$path" ]] && continue
    if [[ -e "$dir/$path" || -e "$ROOT/$path" ]]; then
      :
    else
      warn "broken link in ${md#$ROOT/}: $link"
      LINK_FAIL=$((LINK_FAIL + 1))
    fi
  done < <(grep -oE '\[[^]]+\]\([^)]+\)' "$md" 2>/dev/null | sed -E 's/.*\(([^)]+)\).*/\1/' || true)
}
check_md_links "$ROOT/Scripts/audit/README.md"
check_md_links "$ROOT/Validation/README.md"
check_md_links "$ROOT/Validation/Phase10/Phase10_Completion_Report.md"
if (( LINK_FAIL == 0 )); then
  pass "No broken relative links in spot-checked docs"
fi
echo

###############################################################################
# 7. Phase 10.5 migration scripts (syntax + warn-only path check)
###############################################################################
echo "## Phase 10.5 migration framework"
MIG="$ROOT/scripts/migration"
if [[ -d "$MIG" ]]; then
  while IFS= read -r -d '' script; do
    if bash -n "$script" 2>/dev/null; then
      pass "bash -n ${script#$ROOT/}"
    else
      fail "bash -n ${script#$ROOT/}"
    fi
  done < <(find "$MIG" -type f -name '*.sh' -print0 2>/dev/null)

  if [[ -x "$MIG/compose-path-check.sh" ]] || [[ -f "$MIG/compose-path-check.sh" ]]; then
    if bash "$MIG/compose-path-check.sh" >/dev/null 2>&1; then
      pass "compose-path-check.sh"
    else
      # Warn-only: path check may FAIL on policy findings without blocking Phase 10 validate
      warn "compose-path-check.sh reported findings (see Validation/Phase10.5/Compose_Path_Check_Runtime.md)"
    fi
  else
    skip "compose-path-check.sh missing"
  fi
else
  skip "scripts/migration missing"
fi
echo

###############################################################################
# Summary
###############################################################################
echo "=========================================="
echo " Results: PASS=$PASS  WARN=$WARN  FAIL=$FAIL  SKIP=$SKIP"
echo "=========================================="

if (( FAIL > 0 )); then
  exit 1
fi
exit 0
