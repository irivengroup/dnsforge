from __future__ import annotations

from dnsforge.infrastructure.runtime.command_runner import CommandRunner, CommandResult

class ServiceManager:
    def __init__(self, runner: CommandRunner | None = None) -> None:
        self.runner = runner or CommandRunner()

    def is_active(self, service: str) -> bool:
        return self.runner.run(["systemctl", "is-active", "--quiet", service]).ok

    def restart(self, service: str) -> CommandResult:
        return self.runner.run(["systemctl", "restart", service], check=False)

    def reload(self, service: str) -> CommandResult:
        return self.runner.run(["systemctl", "reload", service], check=False)

    def enable_now(self, service: str) -> CommandResult:
        return self.runner.run(["systemctl", "enable", "--now", service], check=False)
