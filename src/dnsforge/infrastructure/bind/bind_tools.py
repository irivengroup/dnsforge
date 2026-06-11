from __future__ import annotations

from pathlib import Path
from dnsforge.infrastructure.runtime.command_runner import CommandRunner, CommandResult

class BindTools:
    def __init__(self, runner: CommandRunner | None = None) -> None:
        self.runner = runner or CommandRunner()

    def checkconf(self, config: Path) -> CommandResult:
        return self.runner.run(["named-checkconf", str(config)], check=False)

    def checkzone(self, zone: str, zone_file: Path) -> CommandResult:
        return self.runner.run(["named-checkzone", zone, str(zone_file)], check=False)

    def rndc_status(self) -> CommandResult:
        return self.runner.run(["rndc", "status"], check=False)

    def rndc_reload(self, zone: str | None = None) -> CommandResult:
        command = ["rndc", "reload"]
        if zone:
            command.append(zone)
        return self.runner.run(command, check=False)
