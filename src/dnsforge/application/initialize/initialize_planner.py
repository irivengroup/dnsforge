from __future__ import annotations

from pathlib import Path

from dnsforge.domain.initialize.plan import InitializePlan
from dnsforge.infrastructure.bind.layout import BindLayout, BindLayoutDetector


class InitializePlanner:
    def __init__(self, layout: BindLayout | None = None) -> None:
        self.layout = layout or BindLayoutDetector().detect()

    def build_proxy_plan(
        self,
        node: str,
        proxy_type: str,
        render_root: Path | None,
        dry_run: bool,
        backup_before_apply: bool,
    ) -> InitializePlan:
        plan = InitializePlan(
            role="dns-proxy",
            node=node,
            render_root=render_root,
            dry_run=dry_run,
            backup_before_apply=backup_before_apply,
        )
        plan.add_step("validate proxy settings", description=f"node={node}, type={proxy_type}")
        plan.add_step("render modular BIND configuration", description=f"layout={self.layout.family}")
        plan.add_step("assert BIND prerequisites", description="named-checkconf, rndc, systemctl must already exist")
        if backup_before_apply:
            plan.add_step(
                "backup existing BIND configuration",
                description="mv live BIND config/data to /var/backups/dnsforge/bind-config/<timestamp>.tar.gz",
            )
        plan.add_step(
            "apply native Enterprise BIND tree",
            description=f"deploy {self.layout.named_conf}, {self.layout.config_dir}, {self.layout.data_dir}, {self.layout.log_dir}",
        )
        plan.add_step(
            "apply ownership and permissions",
            description="root:named for config, named:named for zones/log/runtime; strict modes",
        )
        plan.add_step("configure firewall", ["firewall-cmd", "--permanent", "--add-service=dns"])
        plan.add_step("reload firewall", ["firewall-cmd", "--reload"])
        plan.add_step(
            "apply selinux contexts", ["restorecon", "-Rv", *[str(path) for path in self.layout.selinux_paths]]
        )
        plan.add_step("reload systemd", ["systemctl", "daemon-reload"])
        plan.add_step(f"enable {self.layout.service_name}", ["systemctl", "enable", "--now", self.layout.service_name])
        plan.add_step(f"restart {self.layout.service_name}", ["systemctl", "restart", self.layout.service_name])
        return plan

    def build_authoritative_plan(
        self,
        node: str,
        render_root: Path | None,
        dry_run: bool,
        backup_before_apply: bool,
    ) -> InitializePlan:
        plan = InitializePlan(
            role="dns-authoritative",
            node=node,
            render_root=render_root,
            dry_run=dry_run,
            backup_before_apply=backup_before_apply,
        )
        plan.add_step("validate authoritative settings", description=f"node={node}")
        plan.add_step("render modular BIND configuration", description=f"layout={self.layout.family}")
        plan.add_step("assert BIND prerequisites", description="named-checkconf, rndc, systemctl must already exist")
        if backup_before_apply:
            plan.add_step(
                "backup existing BIND configuration",
                description="mv live BIND config/data to /var/backups/dnsforge/bind-config/<timestamp>.tar.gz",
            )
        plan.add_step(
            "apply native Enterprise BIND tree",
            description=f"deploy {self.layout.named_conf}, {self.layout.config_dir}, {self.layout.data_dir}, {self.layout.log_dir}",
        )
        plan.add_step(
            "apply ownership and permissions",
            description="root:named for config, named:named for zones/log/runtime; strict modes",
        )
        plan.add_step("configure firewall", ["firewall-cmd", "--permanent", "--add-service=dns"])
        plan.add_step("reload firewall", ["firewall-cmd", "--reload"])
        plan.add_step(
            "apply selinux contexts", ["restorecon", "-Rv", *[str(path) for path in self.layout.selinux_paths]]
        )
        plan.add_step("reload systemd", ["systemctl", "daemon-reload"])
        plan.add_step(f"enable {self.layout.service_name}", ["systemctl", "enable", "--now", self.layout.service_name])
        plan.add_step(f"restart {self.layout.service_name}", ["systemctl", "restart", self.layout.service_name])
        return plan
