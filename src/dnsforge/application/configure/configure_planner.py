from __future__ import annotations

from pathlib import Path

from dnsforge.domain.configure.plan import ConfigurePlan


class ConfigurePlanner:
    def build_proxy_plan(
        self,
        node: str,
        proxy_type: str,
        render_root: Path | None,
        dry_run: bool,
        skip_install: bool,
    ) -> ConfigurePlan:
        plan = ConfigurePlan(
            role="dns-proxy",
            node=node,
            render_root=render_root,
            dry_run=dry_run,
            skip_install=skip_install,
        )
        plan.add_step("validate proxy settings", description=f"node={node}, type={proxy_type}")
        plan.add_step("render proxy configuration", description=str(render_root or "legacy-render"))
        if not skip_install:
            plan.add_step("install required packages", ["dnf", "-y", "install", "bind", "bind-utils", "keepalived"])
        plan.add_step("apply rendered files", description="/etc/named*, /var/named*, systemd override")
        plan.add_step("configure firewall", ["firewall-cmd", "--permanent", "--add-service=dns"])
        plan.add_step("reload firewall", ["firewall-cmd", "--reload"])
        plan.add_step("restore selinux contexts", ["restorecon", "-Rv", "/etc/named.conf", "/etc/named", "/var/named"])
        plan.add_step("reload systemd", ["systemctl", "daemon-reload"])
        plan.add_step("enable named", ["systemctl", "enable", "--now", "named"])
        plan.add_step("restart named", ["systemctl", "restart", "named"])
        return plan

    def build_authoritative_plan(
        self,
        node: str,
        render_root: Path | None,
        dry_run: bool,
        skip_install: bool,
    ) -> ConfigurePlan:
        plan = ConfigurePlan(
            role="dns-authoritative",
            node=node,
            render_root=render_root,
            dry_run=dry_run,
            skip_install=skip_install,
        )
        plan.add_step("validate authoritative settings", description=f"node={node}")
        plan.add_step("render authoritative configuration", description=str(render_root or "legacy-render"))
        if not skip_install:
            plan.add_step("install required packages", ["dnf", "-y", "install", "bind", "bind-utils", "keepalived"])
        plan.add_step("apply rendered files", description="/etc/named*, /var/named*, systemd override")
        plan.add_step("configure firewall", ["firewall-cmd", "--permanent", "--add-service=dns"])
        plan.add_step("reload firewall", ["firewall-cmd", "--reload"])
        plan.add_step("restore selinux contexts", ["restorecon", "-Rv", "/etc/named.conf", "/etc/named", "/var/named"])
        plan.add_step("reload systemd", ["systemctl", "daemon-reload"])
        plan.add_step("enable named", ["systemctl", "enable", "--now", "named"])
        plan.add_step("restart named", ["systemctl", "restart", "named"])
        return plan
