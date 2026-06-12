from __future__ import annotations

import shutil

from dnsforge.infrastructure.system.command import CommandExecutor
from dnsforge.infrastructure.bind.layout import BindLayout, BindLayoutDetector


class SELinuxManager:
    def __init__(self, executor: CommandExecutor | None = None, layout: BindLayout | None = None) -> None:
        self.executor = executor or CommandExecutor()
        self.layout = layout or BindLayoutDetector().detect()

    def ensure_named_contexts(self, dry_run: bool = True) -> list[list[str]]:
        """Register and restore SELinux contexts for DNSForge-managed BIND paths.

        semanage may be absent on minimal systems; restorecon remains the final
        authoritative step. Commands are no-ops in dry-run mode.
        """
        commands = [
            ["semanage", "fcontext", "-a", "-t", "named_conf_t", f"{self.layout.config_dir}(/.*)?"],
            ["semanage", "fcontext", "-a", "-t", "named_conf_t", str(self.layout.named_conf)],
            ["semanage", "fcontext", "-a", "-t", "named_zone_t", f"{self.layout.data_dir}(/.*)?"],
            ["semanage", "fcontext", "-a", "-t", "named_log_t", f"{self.layout.log_dir}(/.*)?"],
            ["semanage", "fcontext", "-a", "-t", "named_var_run_t", f"{self.layout.run_dir}(/.*)?"],
            ["restorecon", "-Rv", *[str(path) for path in self.layout.selinux_paths]],
        ]
        executed: list[list[str]] = []
        semanage_available = shutil.which("semanage") is not None
        for command in commands:
            if command[0] == "semanage" and not dry_run and not semanage_available:
                continue
            self.executor.run(command, dry_run=dry_run)
            executed.append(command)
        return executed

    def restore_named_contexts(self, dry_run: bool = True) -> list[str]:
        self.ensure_named_contexts(dry_run=dry_run)
        return ["restorecon", "-Rv", *[str(path) for path in self.layout.selinux_paths]]
