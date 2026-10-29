"""Task Bridge configuration from environment."""
from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Config:
    api_token: str = field(default_factory=lambda: os.environ.get("TASKBRIDGE_API_TOKEN", ""))
    data_dir: str = field(default_factory=lambda: os.environ.get("TASKBRIDGE_DATA", "/opt/taskbridge/data"))
    repo_dir: str = field(default_factory=lambda: os.environ.get("TASKBRIDGE_REPO", "/workspace"))
    opencode_config: str = field(default_factory=lambda: os.environ.get("OPENCODE_CONFIG", "/opt/taskbridge/etc/opencode.jsonc"))
    opencode_home: str = field(default_factory=lambda: os.environ.get("OPENCODE_HOME", "/opt/taskbridge/home"))
    model: str = field(default_factory=lambda: os.environ.get("TASKBRIDGE_MODEL", "ollama/gpt-oss:20b-cloud"))
    discord_webhook: str = field(default_factory=lambda: os.environ.get("TASKBRIDGE_DISCORD_WEBHOOK", ""))
    ntfy_url: str = field(default_factory=lambda: os.environ.get("TASKBRIDGE_NTFY_URL", ""))
    task_timeout: int = field(default_factory=lambda: int(os.environ.get("TASKBRIDGE_TASK_TIMEOUT", "3600")))
    max_concurrent_tasks: int = field(default_factory=lambda: int(os.environ.get("TASKBRIDGE_MAX_CONCURRENT", "1")))

    @property
    def db_path(self) -> str:
        return os.path.join(self.data_dir, "tasks.db")

    @property
    def logs_dir(self) -> str:
        return os.path.join(self.data_dir, "logs")

    @property
    def worktrees_dir(self) -> str:
        return os.path.join(self.data_dir, "worktrees")


def load_config() -> Config:
    return Config()