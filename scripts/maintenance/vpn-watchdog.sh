#!/bin/bash
# VPN watchdog for qbittorrent (hotio WireGuard) + nzbget (shared netns)
#
# Detects a dead Mullvad tunnel (stale handshake / no egress) and:
#   1. Auto-fixes relay pubkey rotation in wg0.conf (Mullvad renumbers+rekeys relays)
#   2. Restarts qbittorrent (re-resolves hostname endpoint)
#   3. Restarts nzbget (re-attaches to qbittorrent's netns)
#
# Runs via user crontab (fatherfrank is in the docker group).
set -uo pipefail

LOG_FILE="${HOME}/.local/log/vpn-watchdog.log"
CONFIG="/mnt/monarch/appdata/hotio/wireguard/wg0.conf"
BACKUP_SUFFIX=".pre-watchdog.bak"
RELAY_API="https://api.mullvad.net/www/relays/all/"
STALE_HANDSHAKE_SECS=300          # ~2 rekey cycles; healthy tunnels rekey every ~120s
STALE_IF_NO_EGRESS_SECS=180
mkdir -p "$(dirname "$LOG_FILE")"

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') $*" >> "$LOG_FILE"; }

tunnel_up() {
    # True if handshake is recent AND tunnel egress works
    local hs epoch now
    hs=$(docker exec qbittorrent wg show wg0 latest-handshakes 2>/dev/null | awk '{print $2}')
    [[ -n "${hs:-}" && "$hs" != "0" ]] || return 1
    now=$(date +%s)
    if (( now - hs > STALE_HANDSHAKE_SECS )); then
        log "WARN handshake stale: ${now} - ${hs} = $(( now - hs ))s"
        return 1
    fi
    # egress probe through the tunnel
    if ! curl -fsS --max-time 8 https://api.ipify.org >/dev/null 2>&1; then
        log "WARN egress probe failed (handshake age $(( now - hs ))s)"
        return 1
    fi
    return 0
}

refresh_relay_key() {
    # If Mullvad rotated the relay key, update wg0.conf so the next restart works.
    local hostname pubkey_cfg pubkey_live found relay tmp
    hostname=$(sed -nE 's/^Endpoint[[:space:]]*=[[:space:]]*([^:]+):.*/\1/p' "$CONFIG" | head -1)
    [[ -n "$hostname" ]] || { log "ERROR could not parse Endpoint hostname from $CONFIG"; return 1; }
    pubkey_cfg=$(sed -nE 's/^PublicKey[[:space:]]*=[[:space:]]*([A-Za-z0-9+/=]+).*/\1/p' "$CONFIG" | head -1)

    tmp=$(mktemp)
    if ! curl -fsSL --max-time 20 "$RELAY_API" -o "$tmp" 2>/dev/null; then
        rm -f "$tmp"; log "ERROR could not fetch Mullvad relay list"; return 1
    fi
    found=""
    pubkey_live=""
    while IFS='|' read -r fq pk; do
        if [[ "$fq" == "$hostname" ]]; then found=1; pubkey_live="$pk"; break; fi
    done < <(python3 -c "
import json,sys
d=json.load(open('$tmp'))
for r in d:
    if r.get('active') and r.get('pubkey'):
        print(r.get('fqdn','')+'|'+r.get('pubkey',''))
")
    rm -f "$tmp"

    if [[ -z "$found" ]]; then
        log "WARN relay '$hostname' not found in Mullvad list (decommissioned?)"
        return 1
    fi
    if [[ "$pubkey_cfg" != "$pubkey_live" ]]; then
        cp -a "$CONFIG" "${CONFIG}${BACKUP_SUFFIX}"
        sed -i "s|^PublicKey[[:space:]]*=.*|PublicKey = ${pubkey_live}|" "$CONFIG"
        log "FIX relay key rotated for $hostname: ${pubkey_cfg:0:8}... -> ${pubkey_live:0:8}..."
    else
        log "INFO relay key for $hostname unchanged"
    fi
    return 0
}

log "=== watchdog run ==="
if tunnel_up; then
    log "INFO tunnel healthy"
    exit 0
fi

log "WARN tunnel unhealthy — beginning recovery"
refresh_relay_key || log "WARN continuing without key refresh (may fail if key rotated)"

log "ACTION restart qbittorrent"
docker restart qbittorrent >>"$LOG_FILE" 2>&1
sleep 25
if tunnel_up; then
    log "INFO qbittorrent tunnel healthy after restart"
else
    log "WARN qbittorrent tunnel still unhealthy after restart"
fi

log "ACTION restart nzbget (re-attach shared netns)"
docker restart nzbget >>"$LOG_FILE" 2>&1
sleep 15

if tunnel_up; then
    log "INFO recovery complete — tunnel healthy"
else
    log "ERROR recovery incomplete — tunnel still down"
fi