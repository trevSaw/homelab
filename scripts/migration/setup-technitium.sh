#!/usr/bin/env bash
# Phase 19 — reproducible Technitium configuration setup
# Idempotent: safe to re-run. Requires .env (DNS_SERVER_ADMIN_PASSWORD) in services/technitium/.
# Uses the Technitium HTTP API to recreate zones, records, apps, and settings.
set -euo pipefail

TECH_DIR="$(cd "$(dirname "$0")/../.." && pwd)/services/technitium"
cd "$TECH_DIR"
source .env

API="${TECH_API_URL:-http://192.168.50.44:5380}"
TOKEN=""

api() { # api <method> <path> [curl extra args...]
  local method="$1" path="$2"; shift 2
  if [ "$method" = "GET" ]; then
    curl -s -m 30 -H "Authorization: Bearer $TOKEN" "$API$path"
  else
    curl -s -m 30 -X "$method" -H "Authorization: Bearer $TOKEN" "$API$path"
  fi
}

log() { echo "[setup] $*"; }

login() {
  TOKEN=$(curl -s -m 10 "$API/api/user/login?user=admin&pass=$DNS_SERVER_ADMIN_PASSWORD" \
    | python3 -c "import json,sys; print(json.load(sys.stdin).get('token',''))")
  [ -n "$TOKEN" ] || { echo "ERROR: login failed"; exit 1; }
  log "authenticated"
}

create_zone() {
  local zone="$1" type="$2"
  local out; out=$(api GET "/api/zones/create?zone=$zone&type=$type")
  if echo "$out" | grep -q '"status":"ok"' || echo "$out" | grep -q 'already exists'; then
    log "zone ok: $zone ($type)"
  else
    log "zone note: $zone -> $out"
  fi
}

add_record() { # add_record <domain> <zone> <type> <extra-query>
  local domain="$1" zone="$2" type="$3" extra="$4"
  local out; out=$(api GET "/api/zones/records/add?domain=$domain&zone=$zone&type=$type&$extra")
  if echo "$out" | grep -q '"status":"ok"'; then
    log "record ok: $type $domain"
  else
    log "record note: $type $domain -> $out"
  fi
}

main() {
  login

  # --- apps ---
  api GET "/api/apps/downloadAndInstall?name=Split%20Horizon&url=https%3A%2F%2Fdownload.technitium.com%2Fdns%2Fapps%2FSplitHorizonApp-v11.zip" >/dev/null || true

  # --- settings ---
  api GET "/api/settings/set?recursion=AllowOnlyForPrivateNetworks&enableBlocking=true&blockingType=AnyAddress&blockListUrls=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote('$DNS_SERVER_BLOCK_LIST_URLS'))")&blockListUpdateIntervalHours=24&dnssecValidation=true" >/dev/null
  log "settings applied"

  # --- zones ---
  # Technitium auto-populates the primary zone's apex NS/SOA from
  # DNS_SERVER_DOMAIN (dns.mocha). This is internal split-horizon authority
  # metadata, not the public Cloudflare delegation. Do not change the local
  # apex NS to Cloudflare; see services/technitium/README.md.
  create_zone "fatherfankscloud.uk" "Primary"
  create_zone "192.168.50.0/24" "Primary"   # -> 50.168.192.in-addr.arpa

  # --- host APP record (Split Horizon) ---
  # 192.168.176.1/32 = docker bridge gateway. Docker's userland proxy (docker-proxy)
  # rewrites the source IP of queries arriving via the Tailscale listener
  # (100.102.139.115:53) to this address, so Tailscale clients would otherwise match
  # "private" and receive the LAN answer. See services/technitium/README.md.
  local sh_data='{"private":["192.168.50.44"],"100.64.0.0/10":["100.102.139.115"],"192.168.176.1/32":["100.102.139.115"]}'
  local sh_enc; sh_enc=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$sh_data")
  add_record "mocha.fatherfankscloud.uk" "fatherfankscloud.uk" "APP" "appName=Split%20Horizon&classPath=SplitHorizon.SimpleAddress&recordData=$sh_enc&overwrite=true"

  # --- service CNAMEs -> mocha ---
  for svc in sso code hermes homeassistant home jellyfin jellyseerr kav nx chat sparkyfitness calib calibre traefik bazarr honcho prowlarr radarr sync chaptarr audiobooks; do
    add_record "$svc.fatherfankscloud.uk" "fatherfankscloud.uk" "CNAME" "cname=mocha.fatherfankscloud.uk&overwrite=true"
  done

  # --- bare hostname parity ---
  add_record "casaos.fatherfankscloud.uk" "fatherfankscloud.uk" "A" "ipAddress=192.168.50.213&overwrite=true"

  # --- PTRs ---
  add_record "44.50.168.192.in-addr.arpa" "50.168.192.in-addr.arpa" "PTR" "ptrName=sso.fatherfankscloud.uk"
  add_record "213.50.168.192.in-addr.arpa" "50.168.192.in-addr.arpa" "PTR" "ptrName=casaos"
  add_record "96.50.168.192.in-addr.arpa" "50.168.192.in-addr.arpa" "PTR" "ptrName=P110M"
  add_record "73.50.168.192.in-addr.arpa" "50.168.192.in-addr.arpa" "PTR" "ptrName=Trevs-iPhone"
  add_record "119.50.168.192.in-addr.arpa" "50.168.192.in-addr.arpa" "PTR" "ptrName=MacBookPro"

  log "DONE"
}

main
