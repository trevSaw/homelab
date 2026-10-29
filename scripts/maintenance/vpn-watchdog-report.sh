#!/bin/bash
# vpn-watchdog-report.sh — emit recent actionable VPN watchdog events for n8n.
# Prints lines that indicate a recovery, key-rotation fix, or unresolved failure
# from the watchdog log, formatted as simple alert lines (one per line).
set -uo pipefail

LOG_FILE="${HOME}/.local/log/vpn-watchdog.log"
STATE_FILE="${HOME}/.local/log/vpn-watchdog-report.state"

# Lines we care about:
#   FIX relay key rotated ...   -> Mullvad rotated the key; we auto-fixed it
#   ACTION restart qbittorrent  -> watchdog had to bounce the downloader
#   INFO recovery complete      -> tunnel recovered
#   WARN qbittorrent tunnel still unhealthy after restart -> didn't recover first try
#   ERROR recovery incomplete   -> still broken
PATTERNS=(
  'FIX relay key rotated'
  'ACTION restart qbittorrent'
  'recovery complete'
  'still unhealthy after restart'
  'ERROR recovery incomplete'
)

# Output only events not yet reported (track last line count).
last=0
if [[ -f "$STATE_FILE" ]]; then
  last=$(cat "$STATE_FILE" 2>/dev/null || echo 0)
fi

total=0
if [[ -f "$LOG_FILE" ]]; then
  total=$(wc -l < "$LOG_FILE")
fi

if (( total <= last )); then
  echo "$total" > "$STATE_FILE"
  exit 0
fi

# Tail from the first unreported line.
tail -n "+$(( last + 1 ))" "$LOG_FILE" 2>/dev/null | grep -F -e "${PATTERNS[0]}" -e "${PATTERNS[1]}" -e "${PATTERNS[2]}" -e "${PATTERNS[3]}" -e "${PATTERNS[4]}"

# Record progress even if the log rotated to a smaller size.
echo "$total" > "$STATE_FILE"