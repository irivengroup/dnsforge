from __future__ import annotations

from dnsforge.infrastructure.system.command import CommandExecutor


class FirewalldManager:
    def __init__(self, executor: CommandExecutor | None = None) -> None:
        self.executor = executor or CommandExecutor()

    def dns_commands(self, include_vrrp: bool = False) -> list[list[str]]:
        commands = [
            ["firewall-cmd", "--permanent", "--add-service=dns"],
            ["firewall-cmd", "--permanent", "--add-port=953/tcp"],
        ]
        if include_vrrp:
            commands.append(["firewall-cmd", "--permanent", "--add-protocol=vrrp"])
        commands.append(["firewall-cmd", "--reload"])
        return commands

    def configure_dns(self, dry_run: bool = True, include_vrrp: bool = False) -> list[list[str]]:
        commands = self.dns_commands(include_vrrp=include_vrrp)
        for command in commands:
            self.executor.run(command, dry_run=dry_run)
        return commands
