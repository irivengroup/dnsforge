from __future__ import annotations

from shutil import which
from dnsforge.infrastructure.runtime.command_runner import CommandRunner
from dnsforge.infrastructure.system.distribution import LinuxDistribution, OsReleaseReader


class PackageManager:
    def __init__(self, runner: CommandRunner | None = None, os_reader: OsReleaseReader | None = None) -> None:
        self.runner = runner or CommandRunner()
        self.os_reader = os_reader or OsReleaseReader()

    def bind_present(self) -> bool:
        return all(which(b) is not None for b in ("named", "named-checkconf", "named-checkzone", "rndc"))

    def ensure_bind(self, dry_run: bool = False) -> list[list[str]]:
        if self.bind_present():
            return []
        return self.install_bind(dry_run=dry_run)

    def install_bind(self, dry_run: bool = False) -> list[list[str]]:
        commands = self._commands_for(self.os_reader.read())
        if not dry_run:
            for cmd in commands:
                self.runner.run(cmd, check=True, timeout=600)
        return commands

    def _commands_for(self, distro: LinuxDistribution) -> list[list[str]]:
        if distro.family == "redhat":
            return [["dnf", "install", "-y", "bind", "bind-utils"]]
        if distro.family == "debian":
            return [["apt-get", "update"], ["apt-get", "install", "-y", "bind9", "bind9-utils", "dnsutils"]]
        if distro.family == "suse":
            return [["zypper", "--non-interactive", "install", "bind", "bind-utils"]]
        raise RuntimeError("unsupported Linux distribution for automatic BIND installation")
