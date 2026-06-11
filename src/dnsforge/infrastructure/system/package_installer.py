from __future__ import annotations

import shutil

from dnsforge.infrastructure.system.command import CommandExecutor


class PackageInstaller:
    def __init__(self, executor: CommandExecutor | None = None) -> None:
        self.executor = executor or CommandExecutor()

    def package_manager(self) -> str:
        for candidate in ("dnf", "yum"):
            found = shutil.which(candidate)
            if found:
                return found
        return "dnf"

    def bind_stack_command(self) -> list[str]:
        return [self.package_manager(), "-y", "install", "bind", "bind-utils", "keepalived"]

    def install_bind_stack(self, dry_run: bool = True) -> list[str]:
        return self.executor.run(self.bind_stack_command(), dry_run=dry_run)
