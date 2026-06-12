from __future__ import annotations

from dnsforge.infrastructure.system.command import CommandExecutor


class SystemdManager:
    def __init__(self, executor: CommandExecutor | None = None) -> None:
        self.executor = executor or CommandExecutor()

    def daemon_reload(self, dry_run: bool = True) -> list[str]:
        return self.executor.run(["systemctl", "daemon-reload"], dry_run=dry_run)

    def enable_now(self, service: str, dry_run: bool = True) -> list[str]:
        return self.executor.run(["systemctl", "enable", "--now", service], dry_run=dry_run)

    def restart(self, service: str, dry_run: bool = True) -> list[str]:
        return self.executor.run(["systemctl", "restart", service], dry_run=dry_run)
