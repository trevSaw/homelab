"""Task execution engine: queue, serialization, OpenCode subprocess, validation."""
from __future__ import annotations

import json
import logging
import os
import re
import shutil
import signal
import subprocess
import threading
import time
from datetime import datetime, timezone

from .config import Config
from .store import TaskStore

log = logging.getLogger("taskbridge.executor")

PROFILE_AGENTS = {
    "read_only": "kora-readonly",
    "test_write": "kora-testwrite",
    "production_write": "kora-write",
}
VALID_PROFILES = set(PROFILE_AGENTS)

REPORT_RE = None  # replaced by _extract_report()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _utc_day() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d")


class Executor:
    def __init__(self, cfg: Config, store: TaskStore):
        self.cfg = cfg
        self.store = store
        for d in (cfg.logs_dir, cfg.worktrees_dir):
            os.makedirs(d, exist_ok=True)
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._loop, daemon=True, name="executor")

    # -- lifecycle ----------------------------------------------------------
    def start(self):
        self._sweep_interrupted()
        self._thread.start()

    def stop(self):
        self._stop.set()

    def _sweep_interrupted(self):
        """Tasks left RUNNING/STARTING across a bridge restart are failed."""
        for task_id in self.store.running_tasks():
            self.store.set_status(
                task_id, "FAILED", event="interrupted",
                error="Bridge restarted while task was running; execution state was lost.",
            )
            self._notify(self.store.get_task(task_id), "FAILED")

    def _loop(self):
        while not self._stop.wait(2.0):
            try:
                self._tick()
            except Exception:
                log.exception("tick error")

    def _tick(self):
        active = self.store.count_active()
        if active >= self.cfg.max_concurrent_tasks:
            return
        task = self.store.queued_task()
        if task:
            try:
                self._start(task)
            except Exception:
                log.exception("failed to start task %s", task["id"])
                self.store.set_status(
                    task["id"], "FAILED", event="start_error",
                    error="Executor failed to launch the task.",
                )
                # Best-effort: kill any worker process that may have been orphaned
                # by an exception raised after spawn.
                stale = self.store.get_task(task["id"])
                if stale and stale.get("process_pid"):
                    try:
                        os.killpg(int(stale["process_pid"]), signal.SIGKILL)
                    except (ProcessLookupError, OSError):
                        pass

    # -- task id ------------------------------------------------------------
    def new_task_id(self) -> str:
        prefix = "KORA-" + _utc_day()
        return f"{prefix}-{self.store.next_id(prefix):04d}"

    # -- creation -----------------------------------------------------------
    def create(self, request: str, permission_profile: str, requested_by: str,
               session_id: str | None = None, timeout_seconds: int | None = None,
               working_directory: str | None = None) -> dict:
        if not request or not request.strip():
            raise ValueError("request must not be empty")
        if permission_profile not in VALID_PROFILES:
            raise ValueError(f"permission_profile must be one of {sorted(VALID_PROFILES)}")
        task_id = self.new_task_id()
        timeout = timeout_seconds or self.cfg.task_timeout
        task = self.store.create_task(
            task_id, request.strip(), permission_profile, requested_by,
            session_id, timeout, working_directory,
        )
        if permission_profile == "production_write":
            self.store.set_status(
                task_id, "WAITING_FOR_APPROVAL", event="awaiting_approval",
                error="PRODUCTION_WRITE task requires explicit approval before execution.",
            )
            self._notify(task, "WAITING_FOR_APPROVAL")
        else:
            self.store.add_event(task_id, "queued")
            self._notify(task, "QUEUED")
        return self.store.get_task(task_id)

    # -- approval -----------------------------------------------------------
    def approve(self, task_id: str, approver: str) -> dict:
        task = self.store.get_task(task_id)
        if not task:
            raise KeyError("task not found")
        if task["status"] != "WAITING_FOR_APPROVAL":
            raise ValueError(f"task is {task['status']}, not awaiting approval")
        self.store.update_fields(task_id, approved_by=approver)
        self.store.set_status(task_id, "QUEUED", event=f"approved_by={approver}")
        self.store.add_event(task_id, "queued")
        return self.store.get_task(task_id)

    # -- cancel -------------------------------------------------------------
    def cancel(self, task_id: str, by: str) -> dict:
        task = self.store.get_task(task_id)
        if not task:
            raise KeyError("task not found")
        if task["status"] in ("COMPLETED", "FAILED", "CANCELLED"):
            raise ValueError(f"task already in terminal state {task['status']}")
        pid = task.get("process_pid")
        if pid:
            try:
                os.killpg(int(pid), signal.SIGTERM)
            except ProcessLookupError:
                pass
        self.store.set_status(task_id, "CANCELLED", event=f"cancelled_by={by}")
        self._notify(self.store.get_task(task_id), "CANCELLED")
        return self.store.get_task(task_id)

    # -- execution ----------------------------------------------------------
    def _start(self, task: dict):
        task_id = task["id"]
        profile = task["permission_profile"]
        workdir = task["working_directory"] or self.cfg.repo_dir
        worktree_path = None

        self.store.set_status(task_id, "STARTING", event="starting")
        # Boundary guard: snapshot the canonical working tree before non-production
        # tasks so we can mechanically verify it was not mutated during the run.
        before_state = None
        if profile in ("read_only", "test_write"):
            before_state = _canonical_state(self.cfg.repo_dir)
        if profile == "test_write":
            worktree_path = self._make_worktree(task_id)
            workdir = worktree_path
            self.store.update_fields(task_id, working_directory=workdir)

        prompt = self._build_prompt(task, profile, workdir)
        agent = PROFILE_AGENTS[profile]
        log_path = os.path.join(self.cfg.logs_dir, f"{task_id}.log")

        env = {
            **os.environ,
            "HOME": self.cfg.opencode_home,
            "OPENCODE_CONFIG": self.cfg.opencode_config,
            "TASKBRIDGE_TASK_ID": task_id,
            "TASKBRIDGE_PROFILE": profile,
        }
        cmd = [
            "opencode", "run",
            "--model", self.cfg.model,
            "--agent", agent,
            "--format", "json",
            "--dir", workdir,
            "--title", f"KORA task {task_id}",
            prompt,
        ]
        self.store.set_status(task_id, "RUNNING", event=f"exec:{' '.join(cmd[:6])}...")
        self.store.add_event(task_id, f"opencode_start agent={agent} cwd={workdir}")
        log.info("starting task %s profile=%s agent=%s", task_id, profile, agent)

        exit_code = self._run_opencode(cmd, env, workdir, log_path, task, task_id)

        if exit_code is None:
            self._cleanup_worktree(worktree_path)
            self.store.set_status(
                task_id, "FAILED", event="timeout",
                error=f"Task exceeded {task['timeout_seconds']}s timeout.",
            )
            self._notify(self.store.get_task(task_id), "FAILED")
            return

        result = self._collect_result(task_id, task, workdir, log_path, exit_code)

        # Preserve an explicit CANCELLED state set by cancel() during the run.
        current = self.store.get_task(task_id)
        if current and current["status"] == "CANCELLED":
            self._cleanup_worktree(worktree_path)
            self.store.update_fields(task_id, result=json.dumps(result, default=str), exit_code=exit_code)
            self._notify(current, "CANCELLED")
            return

        # Mechanical boundary check: read_only/test_write tasks must not mutate
        # the canonical repository working tree.
        boundary_violation = False
        if exit_code == 0 and profile in ("read_only", "test_write") and before_state is not None:
            after_state = _canonical_state(self.cfg.repo_dir)
            boundary_violation = after_state != before_state
            result["boundary_check"] = {
                "profile": profile,
                "violation": boundary_violation,
                "new_paths": _canonical_diff(before_state, after_state) if boundary_violation else [],
            }

        if exit_code == 0 and not boundary_violation:
            self.store.set_status(task_id, "VALIDATING", event="validating")
            # Validate while the test_write worktree still exists (validation runs
            # git status / compose config against the working directory).
            result = self._validate(task_id, task, workdir, result)
            self._cleanup_worktree(worktree_path)
            self.store.update_fields(task_id, result=json.dumps(result, default=str), exit_code=0)
            self.store.set_status(task_id, "COMPLETED", event="completed")
        else:
            self._cleanup_worktree(worktree_path)
            result["status"] = "FAILED"
            if boundary_violation:
                result["validation"] = (result["validation"] + " | " if result["validation"] else "") \
                    + "FAIL: canonical repository working tree changed during a read_only/test_write task"
                result["boundary_violation"] = True
                self.store.update_fields(
                    task_id, result=json.dumps(result, default=str), exit_code=exit_code,
                )
                self.store.set_status(
                    task_id, "FAILED", event="boundary_violation",
                    error="Canonical repository working tree changed during a read_only/test_write task.",
                )
            else:
                self.store.update_fields(
                    task_id, result=json.dumps(result, default=str), exit_code=exit_code,
                )
                self.store.set_status(task_id, "FAILED", event="failed", error=result.get("error"))
        self._notify(self.store.get_task(task_id), "COMPLETED" if exit_code == 0 and not boundary_violation else "FAILED")

    def _run_opencode(self, cmd, env, workdir, log_path, task, task_id):
        """Run OpenCode with a bounded retry for model rate-limit (429) errors."""
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            logf = open(log_path, "w", encoding="utf-8")
            try:
                proc = subprocess.Popen(
                    cmd, cwd=workdir, env=env, stdout=logf,
                    stderr=subprocess.STDOUT, start_new_session=True,
                )
            except Exception as exc:  # pragma: no cover
                logf.close()
                self.store.set_status(task_id, "FAILED", event="start_error", error=str(exc))
                return None
            self.store.update_fields(task_id, process_pid=proc.pid)
            try:
                exit_code = self._wait_with_timeout(proc, task["timeout_seconds"], task_id)
            finally:
                logf.close()

            if exit_code is None:
                return None  # timed out
            if exit_code == 0 or attempt == max_attempts:
                return exit_code
            if _log_has_rate_limit(log_path):
                self.store.add_event(task_id, f"retry_after_rate_limit attempt={attempt}")
                log.warning("task %s hit model rate limit; retrying %d/%d",
                            task_id, attempt, max_attempts)
                time.sleep(15 * attempt)
                continue
            return exit_code
        return None

    def _wait_with_timeout(self, proc: subprocess.Popen, timeout: int, task_id: str):
        deadline = time.time() + max(1, int(timeout))
        while time.time() < deadline:
            if proc.poll() is not None:
                return proc.returncode
            # support cancellation mid-run
            task = self.store.get_task(task_id)
            if task and task["status"] == "CANCELLED":
                try:
                    os.killpg(proc.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                proc.wait(timeout=10)
                return -1
            time.sleep(1)
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        proc.wait(timeout=10)
        return None

    def _build_prompt(self, task: dict, profile: str, workdir: str) -> str:
        parts = [
            "You are a KORA-delegated engineering task running inside the OpenCode "
            "worker bridge. Follow /opt/taskbridge/etc/rules/KORA-WORKER.md and your "
            "agent profile's restrictions exactly.",
            "",
            f"Task ID: {task['id']}",
            f"Permission profile: {profile}",
            f"Working directory: {workdir}",
            "",
            "User request:",
            task["request"],
            "",
            "ACT NOW — do not defer, ask questions, or propose next steps. Use your "
            "tools immediately to perform the work: read/search repository files, "
            "inspect git, inspect the read-only Docker state snapshots under "
            "/opt/taskbridge/docker-state (ps.txt / inspect.txt / networks.txt), and "
            "use webfetch/websearch for current documentation where relevant. Base "
            "every statement in your report on actual tool results.",
            "",
            "Report with the required structured format.",
        ]
        return "\n".join(parts)

    def _collect_result(self, task_id, task, workdir, log_path, exit_code) -> dict:
        events = _parse_opencode_ndjson(log_path)
        session_id = None
        texts = []
        for ev in events:
            if ev.get("sessionID"):
                session_id = ev["sessionID"]
            part = ev.get("part") or {}
            if ev.get("type") == "text" and part.get("type") == "text" and part.get("text"):
                texts.append(part["text"])
        final_text = texts[-1] if texts else ""
        if session_id:
            self.store.update_fields(task_id, opencode_session=session_id)

        no_text = not final_text.strip()
        if no_text:
            # Fallback: pull any assistant text from the OpenCode session store.
            try:
                exported = _run(
                    ["opencode", "export", session_id], cwd=workdir, timeout=60,
                ) if session_id else ""
                texts = _extract_texts_from_export(exported)
                final_text = texts[-1] if texts else ""
                no_text = not final_text.strip()
            except Exception:
                no_text = True

        report = _extract_report(final_text)
        result = {
            "status": "COMPLETED" if exit_code == 0 else "FAILED",
            "task_id": task_id,
            "opencode_session": session_id,
            "exit_code": exit_code,
            "summary": report.get("Summary") or _first_line(final_text) or "",
            "investigation": report.get("Investigation", ""),
            "changes": report.get("Changes", ""),
            "validation": report.get("Validation", ""),
            "production_impact": report.get("Production impact", ""),
            "follow_up": report.get("Follow-up", ""),
            "raw_text": final_text,
            "log": os.path.basename(log_path),
        }
        if no_text:
            result["validation"] = (result["validation"] + " | " if result["validation"] else "") \
                + "WARN: worker exited 0 but produced no text report"
            result["no_text_output"] = True
            result["summary"] = result["summary"] or \
                "OpenCode worker completed with exit 0 but produced no text report."
        return result

    def _validate(self, task_id, task, workdir, result: dict) -> dict:
        checks = []
        git_status = ""
        try:
            git_status = _run(["git", "status", "--porcelain"], cwd=workdir, timeout=30)
            checks.append({"check": "git_status_porcelain", "output": git_status})
        except Exception as exc:
            checks.append({"check": "git_status_porcelain", "error": str(exc)})
        changed_compose = [
            line.split(None, 1)[-1]
            for line in (git_status or "").splitlines()
            if line.strip() and line.split(None, 1)[-1].endswith(("compose.yaml", "compose.yml"))
        ]
        compose_result = "SKIPPED"
        if changed_compose:
            try:
                out = _run(
                    ["docker-compose", "-f", changed_compose[0], "config", "-q"],
                    cwd=workdir, timeout=120,
                )
                compose_result = "PASS" if (out is None or out == "") else f"OUTPUT:{out}"
            except Exception as exc:
                compose_result = f"FAIL:{exc}"
            checks.append({"check": "compose_config", "files": changed_compose, "result": compose_result})
        result["validation_checks"] = checks
        if changed_compose and compose_result != "PASS":
            result["validation"] = result.get("validation") or "FAIL"
            result["validation"] += f"\ncompose config: {compose_result}"
        return result

    def _make_worktree(self, task_id: str) -> str:
        path = os.path.join(self.cfg.worktrees_dir, task_id)
        os.makedirs(path, exist_ok=True)
        _run(["git", "worktree", "add", "--detach", path, "HEAD"], cwd=self.cfg.repo_dir, timeout=120)
        return path

    def _cleanup_worktree(self, path: str | None):
        if not path:
            return
        try:
            _run(["git", "-C", self.cfg.repo_dir, "worktree", "remove", "--force", path], timeout=60)
        except Exception:
            shutil.rmtree(path, ignore_errors=True)
        # Tidy stale linked-worktree metadata (removed or orphaned dirs).
        try:
            _run(["git", "-C", self.cfg.repo_dir, "worktree", "prune"], timeout=30)
        except Exception:
            pass

    # -- notifications ------------------------------------------------------
    def _notify(self, task: dict | None, state: str):
        if not task:
            return
        line = f"KORA task {task['id']} [{task['permission_profile']}] -> {state}"
        if state in ("COMPLETED", "FAILED", "WAITING_FOR_APPROVAL"):
            line += f"\nrequest: {task['request'][:300]}"
        if state == "COMPLETED" and task.get("result"):
            r = task["result"]
            if r.get("summary"):
                line += f"\nsummary: {r['summary'][:400]}"
            if r.get("production_impact"):
                line += f"\nproduction: {r['production_impact'][:200]}"
        if self.cfg.discord_webhook:
            _post_webhook(self.cfg.discord_webhook, line)
        if self.cfg.ntfy_url:
            _post_ntfy(self.cfg.ntfy_url, line)


# -- helpers ----------------------------------------------------------------
def _canonical_state(repo: str) -> str | None:
    """Snapshot of the canonical repo working tree for boundary verification.

    Returns a stable string (git status --porcelain + git diff --stat) or None
    if git is unavailable, in which case the boundary check is skipped.
    """
    try:
        status = _run(["git", "status", "--porcelain"], cwd=repo, timeout=30)
        diffstat = _run(["git", "diff", "--stat"], cwd=repo, timeout=30)
        return f"STATUS:\n{status}\nDIFF:\n{diffstat}"
    except Exception:
        return None


def _canonical_diff(before: str, after: str) -> list[str]:
    """Paths that differ between two canonical-tree snapshots (best effort)."""
    def _paths(state: str) -> set[str]:
        paths: set[str] = set()
        for line in (state or "").splitlines():
            line = line.rstrip()
            if not line or line.startswith("STATUS:") or line.startswith("DIFF:") or "|" in line:
                continue
            parts = line.split(None, 1)
            if parts:
                paths.add(parts[-1])
        return paths

    return sorted(_paths(after) - _paths(before))


def _log_has_rate_limit(log_path: str) -> bool:
    try:
        with open(log_path, encoding="utf-8", errors="replace") as fh:
            sample = fh.read(200000)
    except OSError:
        return False
    return ("429" in sample or "too many concurrent requests" in sample) and "Too Many Requests" in sample


def _parse_opencode_ndjson(log_path: str) -> list[dict]:
    events = []
    try:
        with open(log_path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    events.append(json.loads(line))
                except Exception:
                    continue
    except FileNotFoundError:
        pass
    return events


def _extract_report(text: str) -> dict:
    """Extract structured sections from worker reports.

    Supports both 'Summary: ...' and markdown '**Summary**' header styles,
    capturing multi-line content until the next known header.
    """
    labels = ["Summary", "Investigation", "Changes", "Validation",
              "Production impact", "Follow-up"]
    out = {}
    if not text:
        return out
    pattern = re.compile(
        r"(?:\*\*)?(" + "|".join(labels) + r")(?:\*\*)?\s*:?\s*",
        re.MULTILINE,
    )
    matches = list(pattern.finditer(text))
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        value = text[start:end].strip()
        value = re.sub(r"\s*\n\s*", "\n", value).strip()
        out[m.group(1)] = value
    return out


def _extract_texts_from_export(exported: str) -> list[str]:
    """Best-effort extraction of assistant text from `opencode export` JSON."""
    texts: list[str] = []
    try:
        data = json.loads(exported)
    except Exception:
        return texts
    messages = data.get("messages") if isinstance(data, dict) else None
    if not isinstance(messages, list):
        return texts
    for msg in messages:
        parts = msg.get("parts") or []
        for part in parts:
            if isinstance(part, dict) and part.get("type") == "text" and part.get("text"):
                texts.append(part["text"])
    return texts


def _first_line(text: str) -> str:
    for ln in (text or "").splitlines():
        if ln.strip():
            return ln.strip()
    return ""


def _run(cmd, cwd, timeout=60) -> str:
    """Run a command and return trimmed stdout; raise on non-zero exit."""
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        raise RuntimeError(
            f"command failed ({result.returncode}): {' '.join(map(str, cmd))}\n{result.stderr[:500]}"
        )
    return result.stdout.strip()


def _post_webhook(url: str, text: str):
    try:
        import urllib.request
        body = json.dumps({"content": text}).encode()
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            resp.read()
    except Exception as exc:  # pragma: no cover
        log.warning("discord webhook failed: %s", exc)


def _post_ntfy(url: str, text: str):
    try:
        import urllib.request
        req = urllib.request.Request(
            url, data=text.encode(), headers={"Title": "KORA Task", "Priority": "default"},
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            resp.read()
    except Exception as exc:  # pragma: no cover
        log.warning("ntfy notify failed: %s", exc)