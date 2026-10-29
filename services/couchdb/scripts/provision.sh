#!/usr/bin/env bash
# CouchDB — Obsidian LiveSync provisioning (idempotent, operator-initiated).
#
# - Sources credentials from .env in this directory (never hardcoded).
# - Requires a healthy CouchDB on http://127.0.0.1:5984 (loopback-only publish).
# - Fails safely: no writes are attempted unless CouchDB reports healthy.
# - Creates: the LiveSync database, the sync user, and database security.
#   The sync user is member-only (least privilege); admin stays infrastructure-only.
set -euo pipefail

cd "$(dirname "$0")/.."

[ -f .env ] || { echo "ERROR: .env not found (cp .env.example .env first)"; exit 1; }
source .env

: "${COUCHDB_USER:?COUCHDB_USER not set}"
: "${COUCHDB_PASSWORD:?COUCHDB_PASSWORD not set}"
: "${SYNC_USER:?SYNC_USER not set}"
: "${SYNC_PASSWORD:?SYNC_PASSWORD not set}"
: "${COUCHDB_DB:?COUCHDB_DB not set}"

BASE="http://127.0.0.1:5984"
ADMIN=(-u "${COUCHDB_USER}:${COUCHDB_PASSWORD}")

fail() { echo "ERROR: $*" >&2; exit 1; }

# 1. CouchDB must be healthy before any write.
for i in $(seq 1 30); do
  if curl -fsS "$BASE/_up" >/dev/null 2>&1; then
    break
  fi
  [ "$i" -eq 30 ] && fail "CouchDB not healthy at $BASE/_up after 30s; refusing to provision"
  sleep 1
done
echo "[provision] CouchDB healthy"

# 2. Ensure required system databases exist (idempotent).
ensure_db() {
  local db="$1"
  local status
  status=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "${ADMIN[@]}" "$BASE/$db")
  case "$status" in
    201) echo "[provision] created database '$db'" ;;
    412) echo "[provision] database '$db' already exists" ;;
    *)   fail "PUT /$db -> HTTP $status" ;;
  esac
}
ensure_db _users
ensure_db _replicator

# 3. Create the LiveSync database (idempotent: 201 created, 412 already exists).
ensure_db "$COUCHDB_DB"

# 4. Create the sync user (idempotent; password hashed server-side).
USER_DOC_ID="org.couchdb.user:$SYNC_USER"
if curl -fsS "${ADMIN[@]}" "$BASE/_users/$USER_DOC_ID" >/dev/null 2>&1; then
  echo "[provision] user '$SYNC_USER' already exists"
else
  body=$(python3 -c "import json,sys; print(json.dumps({'_id':'org.couchdb.user:'+sys.argv[1],'name':sys.argv[1],'type':'user','roles':[],'password':sys.argv[2]}))" "$SYNC_USER" "$SYNC_PASSWORD")
  status=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "${ADMIN[@]}" "$BASE/_users/$USER_DOC_ID" -H 'Content-Type: application/json' -d "$body")
  [ "$status" = "201" ] && echo "[provision] created user '$SYNC_USER'"
  [ "$status" != "201" ] && fail "PUT /_users/$USER_DOC_ID -> HTTP $status"
fi

# 5. Grant the sync user member access to the database (idempotent; admins empty).
body=$(python3 -c "import json,sys; print(json.dumps({'members':{'names':[sys.argv[1]]},'admins':{'names':[]}}))" "$SYNC_USER")
status=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "${ADMIN[@]}" "$BASE/$COUCHDB_DB/_security" -H 'Content-Type: application/json' -d "$body")
[ "$status" = "200" ] && echo "[provision] granted '$SYNC_USER' member access to '$COUCHDB_DB'"
[ "$status" != "200" ] && fail "PUT /$COUCHDB_DB/_security -> HTTP $status"

echo "[provision] DONE — database, user, and security permissions configured."
