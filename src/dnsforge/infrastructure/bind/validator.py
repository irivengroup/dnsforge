from __future__ import annotations

from dnsforge.infrastructure.system.command import CommandExecutor
from dnsforge.infrastructure.bind.layout import BindLayout, BindLayoutDetector


class BindConfigurationValidator:
    def __init__(self, executor: CommandExecutor | None = None, layout: BindLayout | None = None) -> None:
        self.executor = executor or CommandExecutor()
        self.layout = layout or BindLayoutDetector().detect()

    def checkconf(self, dry_run: bool = True) -> list[str]:
        return self.executor.run(["named-checkconf", str(self.layout.named_conf)], dry_run=dry_run)
