#!/usr/bin/env python3
"""docker-admin — narrow, token-authenticated Docker administration helper.

Phase 3 (KORA/Hermes controlled homelab administration).

This is the only container on the KORA/Hermes administration path that receives
``/var/run/docker.sock``. Hermes and KORA never receive the socket; they can
only call the whitelisted HTTP operations below. (Several unrelated host
services such as portainer/traefik already mount the socket for their own
purposes; Phase 3 does not change those.) There is deliberately **no generic
Docker proxy**: the helper builds fixed ``docker`` / ``docker compose`` argv
from validated arguments.

Exposed (all require ``Authorization: Bearer <token>`` except ``/healthz``):

  GET  /healthz
  GET  /containers
  GET  /containers/<name>
  GET  /containers/<name>/logs?tail=N
  GET  /images/<ref>
  GET  /networks
  GET  /networks/<name>
  GET  /volumes
  GET  /volumes/<name>
  POST /containers/<name>/restart    {"confirm": true}
  POST /compose/validate             {"project": "...", "service": "..." (optional)}
  POST /compose/up                   {"project": "...", "service": "..." (optional), "confirm": true}

Intentionally NOT exposed: rm/delete, rmi, volume/network removal, prune,
exec, attach, kill, build, pull, push, arbitrary ``docker <anything>``, or
arbitrary Docker API paths.
"""

from __future__ import annotations

import hmac
import json
import os
import re
import subprocess
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlparse

VERSION = "1.0.0"

PORT = int(os.environ.get("DOCKER_ADMIN_PORT", "8765"))
REPO = os.environ.get("DOCKER_ADMIN_REPO", "/repo")
SERVICES_DIR = os.path.join(REPO, "services")
DOCKER = os.environ.get("DOCKER_ADMIN_DOCKER", "/usr/local/bin/docker")
TOKEN = os.environ.get("DOCKER_ADMIN_TOKEN", "").strip()

if not TOKEN:
    print("FATAL: DOCKER_ADMIN_TOKEN is not set", file=sys.stderr, flush=True)
    raise SystemExit(2)

COMPOSE_FILES = ("compose.yaml", "compose.yml", "docker-compose.yml")
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")
PROJECT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")
REF_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:/@-]*$")

CMD_TIMEOUT = int(os.environ.get("DOCKER_ADMIN_TIMEOUT", "90"))
MAX_LOG_TAIL = 1000
DEFAULT_LOG_TAIL = 100
MAX_OUTPUT_BYTES = 200_000

# Control-plane / self-reference protection. These must not be lifecycle-managed
# through this helper (a model must not restart the brain or its own tool).
DENY_RESTART = {"hermes", "docker-admin"}
DENY_DEPLOY_PROJECTS = {"hermes", "docker-admin", "taskbridge"}


class AdminError(Exception):
    def __init__(self, status: int, message: str, **extra):
        super().__init__(message)
        self.status = status
        self.message = message
        self.extra = extra


def _run(argv, timeout: int = CMD_TIMEOUT, cwd=None):
    """Run a fixed argv (never a shell string). Returns (rc, stdout, stderr)."""
    try:
        proc = subprocess.run(
            argv,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            text=True,
            cwd=cwd,
        )
    except FileNotFoundError:
        return 127, "", "docker-cli-not-found"
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"
    out = proc.stdout or ""
    err = proc.stderr or ""
    if len(out) > MAX_OUTPUT_BYTES:
        out = out[:MAX_OUTPUT_BYTES] + "\n...[truncated]"
    if len(err) > MAX_OUTPUT_BYTES:
        err = err[:MAX_OUTPUT_BYTES] + "\n...[truncated]"
    return proc.returncode, out, err


SECRET_MARKERS = ("password", "passwd", "token", "secret", "api_key", "apikey", "credential")


def _sanitize_labels(labels):
    """Redact label VALUES whose key name looks secret-bearing."""
    if not isinstance(labels, dict):
        return {}
    out = {}
    for k, v in labels.items():
        if isinstance(k, str) and any(m in k.lower() for m in SECRET_MARKERS):
            out[k] = "***redacted***"
        else:
            out[k] = v
    return out


def _sanitize_inspect(obj: dict) -> dict:
    state = obj.get("State") or {}
    host = obj.get("HostConfig") or {}
    nets = (obj.get("NetworkSettings") or {}).get("Networks") or {}
    cfg = obj.get("Config") or {}
    mounts = []
    for m in obj.get("Mounts") or []:
        mounts.append(
            {
                "type": m.get("Type"),
                "source": m.get("Source"),
                "destination": m.get("Destination"),
                "mode": m.get("Mode"),
                "rw": m.get("RW"),
            }
        )
    health = None
    if isinstance(state.get("Health"), dict):
        health = state["Health"].get("Status")
    return {
        "id": (obj.get("Id") or "")[:12],
        "name": (obj.get("Name") or "").lstrip("/"),
        "created": obj.get("Created"),
        "image": cfg.get("Image"),
        "image_id": (obj.get("Image") or "")[:19],
        "state": {
            "status": state.get("Status"),
            "running": state.get("Running"),
            "restarting": state.get("Restarting"),
            "exit_code": state.get("ExitCode"),
            "started_at": state.get("StartedAt"),
            "finished_at": state.get("FinishedAt"),
            "health": health,
            "dead": state.get("Dead"),
        },
        "restart_policy": (host.get("RestartPolicy") or {}).get("Name"),
        "networks": sorted(nets.keys()),
        "ports": (obj.get("NetworkSettings") or {}).get("Ports") or {},
        "mounts": mounts,
        "labels": _sanitize_labels(cfg.get("Labels")),
        # Env VALUES are never returned; only the keys (names).
        "env_keys": sorted(
            [(e.split("=", 1)[0]) for e in (cfg.get("Env") or []) if e]
        ),
        "cmd": cfg.get("Cmd"),
        "entrypoint": cfg.get("Entrypoint"),
    }


def _list_containers() -> dict:
    fmt = "{{.Names}}\t{{.State}}\t{{.Status}}\t{{.Image}}\t{{.Networks}}\t{{.Ports}}"
    rc, out, err = _run([DOCKER, "ps", "--all", "--format", fmt])
    if rc != 0:
        raise AdminError(502, "docker-unavailable", detail=err.strip()[:500])
    items = []
    for line in out.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        while len(parts) < 6:
            parts.append("")
        items.append(
            {
                "name": parts[0],
                "state": parts[1],
                "status": parts[2],
                "image": parts[3],
                "networks": [n for n in parts[4].split(",") if n],
                "ports": parts[5],
            }
        )
    return {"service": "docker-admin", "count": len(items), "containers": items}


def _inspect_container(name: str) -> dict:
    rc, out, err = _run([DOCKER, "inspect", name])
    if rc != 0:
        # Do NOT translate "inspect failed" into "container does not exist".
        raise AdminError(502, "inspect-failed", target=name, detail=err.strip()[:500])
    try:
        data = json.loads(out)
    except Exception:
        raise AdminError(502, "inspect-unparseable", target=name)
    if not data:
        raise AdminError(404, "container-not-found", target=name)
    return {"service": "docker-admin", "container": _sanitize_inspect(data[0])}


def _container_logs(name: str, tail: int) -> dict:
    rc, out, err = _run(
        [DOCKER, "logs", "--tail", str(tail), "--timestamps", name], timeout=30
    )
    if rc != 0:
        raise AdminError(502, "logs-unavailable", target=name, detail=err.strip()[:500])
    # Docker writes container stderr to our stderr; treat both as logs.
    text = (out + err).strip()
    return {
        "service": "docker-admin",
        "container": name,
        "tail": tail,
        "lines": len(text.splitlines()) if text else 0,
        "logs": text,
    }


def _image_info(ref: str) -> dict:
    rc, out, err = _run([DOCKER, "image", "inspect", ref])
    if rc != 0:
        # Try resolving a container name -> its image, then inspect that.
        rc2, out2, _ = _run([DOCKER, "inspect", ref])
        if rc2 == 0:
            try:
                cfg = json.loads(out2)[0].get("Config") or {}
                image_ref = cfg.get("Image")
            except Exception:
                image_ref = None
            if image_ref and REF_RE.match(image_ref):
                return _image_info(image_ref)
        raise AdminError(502, "image-inspect-failed", target=ref, detail=err.strip()[:500])
    try:
        data = json.loads(out)
    except Exception:
        raise AdminError(502, "image-unparseable", target=ref)
    if not data:
        raise AdminError(404, "image-not-found", target=ref)
    img = data[0]
    return {
        "service": "docker-admin",
        "image": {
            "id": (img.get("Id") or "")[:19],
            "tags": img.get("RepoTags") or [],
            "digests": img.get("RepoDigests") or [],
            "size": img.get("Size"),
            "created": img.get("Created"),
            "architecture": img.get("Architecture"),
            "os": img.get("Os"),
            "labels": _sanitize_labels(img.get("Config", {}).get("Labels")),
        },
    }


def _list_networks() -> dict:
    rc, out, err = _run(
        [DOCKER, "network", "ls", "--format", "{{.Name}}\t{{.Driver}}\t{{.Scope}}"]
    )
    if rc != 0:
        raise AdminError(502, "docker-unavailable", detail=err.strip()[:500])
    items = []
    for line in out.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        while len(parts) < 3:
            parts.append("")
        items.append({"name": parts[0], "driver": parts[1], "scope": parts[2]})
    return {"service": "docker-admin", "count": len(items), "networks": items}


def _inspect_network(name: str) -> dict:
    rc, out, err = _run([DOCKER, "network", "inspect", name])
    if rc != 0:
        raise AdminError(502, "network-inspect-failed", target=name, detail=err.strip()[:500])
    try:
        data = json.loads(out)[0]
    except Exception:
        raise AdminError(502, "network-unparseable", target=name)
    containers = []
    for cname, c in (data.get("Containers") or {}).items():
        containers.append({"name": cname, "ipv4": (c or {}).get("IPv4Address")})
    return {
        "service": "docker-admin",
        "network": {
            "name": data.get("Name"),
            "id": (data.get("Id") or "")[:12],
            "driver": data.get("Driver"),
            "scope": data.get("Scope"),
            "internal": data.get("Internal"),
            "subnets": [i.get("Subnet") for i in ((data.get("IPAM") or {}).get("Config") or [])],
            "containers": containers,
        },
    }


def _list_volumes() -> dict:
    rc, out, err = _run(
        [DOCKER, "volume", "ls", "--format", "{{.Name}}\t{{.Driver}}\t{{.Scope}}"]
    )
    if rc != 0:
        raise AdminError(502, "docker-unavailable", detail=err.strip()[:500])
    items = []
    for line in out.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        while len(parts) < 3:
            parts.append("")
        items.append({"name": parts[0], "driver": parts[1], "scope": parts[2]})
    return {"service": "docker-admin", "count": len(items), "volumes": items}


def _inspect_volume(name: str) -> dict:
    rc, out, err = _run([DOCKER, "volume", "inspect", name])
    if rc != 0:
        raise AdminError(502, "volume-inspect-failed", target=name, detail=err.strip()[:500])
    try:
        data = json.loads(out)[0]
    except Exception:
        raise AdminError(502, "volume-unparseable", target=name)
    return {
        "service": "docker-admin",
        "volume": {
            "name": data.get("Name"),
            "driver": data.get("Driver"),
            "scope": data.get("Scope"),
            "mountpoint": data.get("Mountpoint"),
            "labels": _sanitize_labels(data.get("Labels")),
        },
    }


def _compose_file(project: str) -> str:
    if not PROJECT_RE.match(project):
        raise AdminError(400, "invalid-project", target=project)
    base = os.path.realpath(os.path.join(SERVICES_DIR, project))
    if not (base == os.path.realpath(SERVICES_DIR) or base.startswith(os.path.realpath(SERVICES_DIR) + os.sep)):
        raise AdminError(400, "project-outside-services", target=project)
    if not os.path.isdir(base):
        raise AdminError(404, "project-not-found", target=project)
    for fname in COMPOSE_FILES:
        candidate = os.path.join(base, fname)
        if os.path.isfile(candidate):
            return candidate
    raise AdminError(404, "compose-file-not-found", target=project)


def _compose_validate(project: str) -> dict:
    path = _compose_file(project)
    rc, out, err = _run(
        [DOCKER, "compose", "--project-directory", os.path.dirname(path),
         "-f", path, "config", "--quiet"],
        timeout=60, cwd=os.path.dirname(path),
    )
    return {
        "service": "docker-admin",
        "project": project,
        "compose_file": os.path.relpath(path, REPO),
        "valid": rc == 0,
        "exit_code": rc,
        "detail": (err or out).strip()[:2000],
    }


def _compose_up(project: str, service: str | None) -> dict:
    if project in DENY_DEPLOY_PROJECTS:
        raise AdminError(403, "deploy-target-denied", target=project,
                         reason="control-plane service is not deployable through this helper")
    path = _compose_file(project)
    project_dir = os.path.dirname(path)
    argv = [DOCKER, "compose", "--project-directory", project_dir,
            "-f", path, "up", "-d", "--no-build"]
    if service:
        if not NAME_RE.match(service):
            raise AdminError(400, "invalid-service", target=service)
        argv.append(service)
    rc, out, err = _run(argv, timeout=CMD_TIMEOUT, cwd=project_dir)
    result = {
        "service": "docker-admin",
        "project": project,
        "compose_file": os.path.relpath(path, REPO),
        "service_name": service,
        "exit_code": rc,
        "ok": rc == 0,
        "output": (out + err).strip()[:4000],
    }
    if rc == 0:
        ps_rc, ps_out, _ = _run(
            [DOCKER, "compose", "--project-directory", project_dir,
             "-f", path, "ps", "--format", "json"],
            timeout=30, cwd=project_dir,
        )
        rows = []
        if ps_rc == 0:
            for line in ps_out.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except Exception:
                    pass
        result["containers"] = rows
    return result


def _restart_container(name: str) -> dict:
    if name in DENY_RESTART:
        raise AdminError(403, "restart-target-denied", target=name,
                         reason="control-plane/self target is not restartable through this helper")
    before = _inspect_container(name)["container"]
    rc, out, err = _run([DOCKER, "restart", "--time", "10", name], timeout=CMD_TIMEOUT)
    result = {
        "service": "docker-admin",
        "target": name,
        "issued": True,
        "exit_code": rc,
        "ok": rc == 0,
        "output": (out + err).strip()[:1000],
        "state_before": before.get("state"),
    }
    # Verify the resulting state; never assume success.
    deadline = time.time() + 30
    after = None
    while time.time() < deadline:
        try:
            after = _inspect_container(name)["container"]
        except AdminError:
            after = None
        status = (after or {}).get("state", {}).get("status")
        health = (after or {}).get("state", {}).get("health")
        if status == "running" and health in (None, "healthy"):
            break
        time.sleep(2)
    result["state_after"] = (after or {}).get("state")
    result["started_at_after"] = (after or {}).get("state", {}).get("started_at")
    return result


class Handler(BaseHTTPRequestHandler):
    server_version = "docker-admin/" + VERSION

    def log_message(self, fmt, *args):  # noqa: A003 - silence default access log
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    # -- helpers -----------------------------------------------------------
    def _send(self, status: int, payload: dict):
        body = json.dumps(payload, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _authed(self) -> bool:
        header = self.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return False
        return hmac.compare_digest(header[7:].strip(), TOKEN)

    def _body(self) -> dict:
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        try:
            data = json.loads(raw.decode("utf-8"))
        except Exception:
            raise AdminError(400, "invalid-json")
        if not isinstance(data, dict):
            raise AdminError(400, "json-object-required")
        return data

    # -- routing -----------------------------------------------------------
    def do_GET(self):  # noqa: N802
        parsed = urlparse(self.path)
        path = unquote(parsed.path).rstrip("/") or "/"
        query = parse_qs(parsed.query)
        if path == "/healthz":
            return self._send(200, {"service": "docker-admin", "status": "ok",
                                    "version": VERSION, "repo": REPO})
        if not self._authed():
            return self._send(401, {"status": "error", "error": "unauthorized"})
        try:
            parts = [p for p in path.split("/") if p]
            if path == "/containers":
                return self._send(200, _list_containers())
            if len(parts) == 2 and parts[0] == "containers":
                return self._send(200, _inspect_container(parts[1]))
            if len(parts) == 3 and parts[0] == "containers" and parts[2] == "logs":
                try:
                    tail = max(1, min(int((query.get("tail") or [DEFAULT_LOG_TAIL])[0]), MAX_LOG_TAIL))
                except (TypeError, ValueError):
                    tail = DEFAULT_LOG_TAIL
                return self._send(200, _container_logs(parts[1], tail))
            if len(parts) == 2 and parts[0] == "images":
                return self._send(200, _image_info(parts[1]))
            if path == "/networks":
                return self._send(200, _list_networks())
            if len(parts) == 2 and parts[0] == "networks":
                return self._send(200, _inspect_network(parts[1]))
            if path == "/volumes":
                return self._send(200, _list_volumes())
            if len(parts) == 2 and parts[0] == "volumes":
                return self._send(200, _inspect_volume(parts[1]))
            return self._send(404, {"status": "error", "error": "not-found", "path": path})
        except AdminError as e:
            return self._send(e.status, {"status": "error", "error": e.message, **e.extra})
        except Exception as e:  # noqa: BLE001
            return self._send(500, {"status": "error", "error": "internal", "detail": str(e)[:300]})

    def do_POST(self):  # noqa: N802
        parsed = urlparse(self.path)
        path = unquote(parsed.path).rstrip("/") or "/"
        if not self._authed():
            return self._send(401, {"status": "error", "error": "unauthorized"})
        try:
            body = self._body()
            parts = [p for p in path.split("/") if p]
            if len(parts) == 3 and parts[0] == "containers" and parts[2] == "restart":
                if body.get("confirm") is not True:
                    raise AdminError(400, "confirmation-required")
                return self._send(200, _restart_container(parts[1]))
            if path == "/compose/validate":
                project = str(body.get("project", "")).strip()
                if not project:
                    raise AdminError(400, "project-required")
                return self._send(200, _compose_validate(project))
            if path == "/compose/up":
                if body.get("confirm") is not True:
                    raise AdminError(400, "confirmation-required")
                project = str(body.get("project", "")).strip()
                if not project:
                    raise AdminError(400, "project-required")
                service = body.get("service")
                service = str(service).strip() if service else None
                return self._send(200, _compose_up(project, service))
            return self._send(404, {"status": "error", "error": "not-found", "path": path})
        except AdminError as e:
            return self._send(e.status, {"status": "error", "error": e.message, **e.extra})
        except Exception as e:  # noqa: BLE001
            return self._send(500, {"status": "error", "error": "internal", "detail": str(e)[:300]})


def main():
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"docker-admin {VERSION} listening on 0.0.0.0:{PORT} (repo={REPO})", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
