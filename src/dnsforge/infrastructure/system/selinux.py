from __future__ import annotations

from dnsforge.infrastructure.system.command import CommandExecutor


class SELinuxManager:
    def __init__(self, executor: CommandExecutor | None = None) -> None:
        self.executor = executor or CommandExecutor()

    def restore_named_contexts(self, dry_run: bool = True) -> list[str]:
        command = ["restorecon", "-Rv", "/etc/named.conf", "/etc/named", "/var/named"]
        return self.executor.run(command, dry_run=dry_run)
