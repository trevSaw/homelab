#!/bin/sh
# Read-only Docker state snapshot for KORA (no docker.sock exposed to any
# container). Refresh by running this on the host (cron or manual).
DEST="$(dirname "$0")"
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}\t{{.Ports}}' > "$DEST/ps.txt" 2>/dev/null
: > "$DEST/inspect.txt"
docker ps --format '{{.Names}}' | while read -r n; do
  docker inspect --format '{{.Name}}|state={{.State.Status}}|health={{if .State.Health}}{{.State.Health.Status}}{{else}}n/a{{end}}|image={{.Config.Image}}|restart={{.HostConfig.RestartPolicy.Name}}|net={{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}' "$n" >> "$DEST/inspect.txt" 2>/dev/null
done
docker network ls --format '{{.Name}}\t{{.Driver}}' > "$DEST/networks.txt" 2>/dev/null
chmod 644 "$DEST"/ps.txt "$DEST"/inspect.txt "$DEST"/networks.txt 2>/dev/null
echo "snapshot written to $DEST ($(date))"
