"""Unit tests for the docker-admin helper's safety-critical pure logic.

These tests never touch Docker and never perform writes; they exercise the
argument validation, path-traversal guard, and secret redaction that the
whitelist depends on.

Run:  python3 -m pytest services/docker-admin/tests -q
"""

from __future__ import annotations

import importlib.util
import os
import pathlib

import pytest

APP = pathlib.Path(__file__).resolve().parents[1] / "app.py"


@pytest.fixture(scope="module")
def mod():
    os.environ.setdefault("DOCKER_ADMIN_TOKEN", "test-token-not-real")
    spec = importlib.util.spec_from_file_location("docker_admin_app", APP)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_refuses_to_start_without_token(tmp_path):
    env = dict(os.environ)
    env.pop("DOCKER_ADMIN_TOKEN", None)
    spec = importlib.util.spec_from_file_location("docker_admin_notok", APP)
    module = importlib.util.module_from_spec(spec)
    old = os.environ.pop("DOCKER_ADMIN_TOKEN", None)
    try:
        with pytest.raises(SystemExit):
            spec.loader.exec_module(module)
    finally:
        if old is not None:
            os.environ["DOCKER_ADMIN_TOKEN"] = old


def test_container_name_validation(mod):
    assert mod.NAME_RE.match("sonarr")
    assert mod.NAME_RE.match("my_container-1.2")
    for bad in ["", "../etc", "a/b", "-leadingdash", "white space", "a;b", "$(id)"]:
        assert not mod.NAME_RE.match(bad), bad


def test_project_path_traversal_rejected(mod, tmp_path, monkeypatch):
    services = tmp_path / "services"
    (services / "sonarr").mkdir(parents=True)
    (services / "sonarr" / "compose.yml").write_text("services: {}\n")
    monkeypatch.setattr(mod, "SERVICES_DIR", str(services))
    assert mod._compose_file("sonarr").endswith("compose.yml")
    for bad in ["../", "../..", "sonarr/../..", "/etc", "does-not-exist", "nope;rm"]:
        with pytest.raises(mod.AdminError):
            mod._compose_file(bad)


def test_sanitize_labels_redacts_secrets(mod):
    out = mod._sanitize_labels(
        {"com.homelab.service": "sonarr", "db_password": "hunter2", "MY_TOKEN": "abc"}
    )
    assert out["com.homelab.service"] == "sonarr"
    assert out["db_password"] == "***redacted***"
    assert out["MY_TOKEN"] == "***redacted***"


def test_sanitize_inspect_never_returns_env_values(mod):
    raw = {
        "Id": "a" * 64,
        "Name": "/sonarr",
        "Config": {
            "Image": "linuxserver/sonarr:4.0",
            "Env": ["PUID=1000", "API_KEY=super-secret", "TZ=UTC"],
            "Labels": {"org": "homelab"},
        },
        "State": {"Status": "running", "Running": True, "Health": {"Status": "healthy"}},
        "HostConfig": {"RestartPolicy": {"Name": "unless-stopped"}},
        "NetworkSettings": {"Networks": {"proxy": {}}, "Ports": {}},
        "Mounts": [],
    }
    out = mod._sanitize_inspect(raw)
    assert out["env_keys"] == ["API_KEY", "PUID", "TZ"]  # keys only, no values
    assert "super-secret" not in repr(out)
    assert out["state"]["health"] == "healthy"
    assert out["networks"] == ["proxy"]


def test_control_plane_protected(mod):
    assert "hermes" in mod.DENY_RESTART
    assert "docker-admin" in mod.DENY_RESTART
    assert "hermes" in mod.DENY_DEPLOY_PROJECTS
    assert "docker-admin" in mod.DENY_DEPLOY_PROJECTS
