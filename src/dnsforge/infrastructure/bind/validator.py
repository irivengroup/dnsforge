from __future__ import annotations

import shutil
from pathlib import Path

from dnsforge.infrastructure.system.command import CommandExecutor
from dnsforge.infrastructure.bind.layout import BindLayout, BindLayoutDetector
from dnsforge.shared.errors import DnsForgeError


class BindConfigurationValidator:
    def __init__(self, executor: CommandExecutor | None = None, layout: BindLayout | None = None) -> None:
        self.executor = executor or CommandExecutor()
        self.layout = layout or BindLayoutDetector().detect()

    def checkconf(self, dry_run: bool = True, target_root: Path = Path("/")) -> list[str]:
        named_conf = self._target_path(self.layout.named_conf, target_root)
        if not dry_run:
            self._require_binary("named-checkconf")
        return self.executor.run(["named-checkconf", str(named_conf)], dry_run=dry_run)

    def checkzone(self, zone: str, zone_file: Path, dry_run: bool = True, target_root: Path = Path("/")) -> list[str]:
        effective_file = self._target_path(zone_file, target_root)
        if not dry_run:
            self._require_binary("named-checkzone")
        return self.executor.run(["named-checkzone", zone, str(effective_file)], dry_run=dry_run)

    def rndc_status(self, dry_run: bool = True) -> list[str]:
        if not dry_run:
            self._require_binary("rndc")
        return self.executor.run(["rndc", "status"], dry_run=dry_run)

    def rndc_reload(self, dry_run: bool = True, zone: str | None = None) -> list[str]:
        command = ["rndc", "reload"]
        if zone:
            command.append(zone)
        if not dry_run:
            self._require_binary("rndc")
        return self.executor.run(command, dry_run=dry_run)

    def validate_deployed_tree(self, dry_run: bool = True, target_root: Path = Path("/"), reload_named: bool = False) -> list[list[str]]:
        commands = [self.checkconf(dry_run=dry_run, target_root=target_root)]
        if reload_named:
            commands.append(self.rndc_reload(dry_run=dry_run))
            commands.append(self.rndc_status(dry_run=dry_run))
        return commands

    def _target_path(self, path: Path, target_root: Path) -> Path:
        if target_root == Path("/") or not path.is_absolute():
            return path
        return target_root / path.relative_to("/")

    def _require_binary(self, name: str) -> None:
        if shutil.which(name) is None:
            raise DnsForgeError(f"required BIND tool not found: {name}")
