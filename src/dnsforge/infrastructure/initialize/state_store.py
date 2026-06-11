from __future__ import annotations

import datetime as dt
from pathlib import Path

from dnsforge.infrastructure.settings.env_loader import EnvSettingsLoader
from dnsforge.shared.errors import InitializeError


class InitializeAlreadyAppliedError(InitializeError):
    """Raised when dnsforge initialize is attempted after takeover."""


class InitializeStateStore:
    """Persist the one-shot initialize state in a hidden lock file.

    setup.conf remains the functional node source of truth. The initialize lock is
    a technical bootstrap marker stored separately as:
      <setup.conf parent>/.initialized.conf.lock
    Its path must not be exposed in user-facing status output.
    """

    lock_filename = ".initialized.conf.lock"

    def __init__(self, loader: EnvSettingsLoader | None = None) -> None:
        self.loader = loader or EnvSettingsLoader()

    def lock_file_for(self, setup_file: Path) -> Path:
        return setup_file.parent / self.lock_filename

    def is_initialized(self, setup_file: Path) -> bool:
        return self.lock_file_for(setup_file).exists()

    def get_state(self, setup_file: Path) -> dict[str, str]:
        lock_file = self.lock_file_for(setup_file)
        if not lock_file.exists():
            return {}
        return self.loader.load(lock_file)

    def assert_not_initialized(self, setup_file: Path) -> None:
        if self.is_initialized(setup_file):
            raise InitializeAlreadyAppliedError(
                "DNSForge node is already initialized. Further 'dnsforge initialize' attempts are blocked."
            )

    def mark_initialized(self, setup_file: Path, role: str, node: str) -> None:
        lock_file = self.lock_file_for(setup_file)
        lock_file.parent.mkdir(parents=True, exist_ok=True)
        now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")

        content = "\n".join(
            [
                "INITIALIZED=true",
                f"INITIALIZED_AT={now}",
                f"INITIALIZED_ROLE={role}",
                f"INITIALIZED_NODE={node}",
            ]
        ) + "\n"

        tmp_file = lock_file.with_name(f".{lock_file.name}.tmp")
        tmp_file.write_text(content, encoding="utf-8")
        tmp_file.replace(lock_file)
