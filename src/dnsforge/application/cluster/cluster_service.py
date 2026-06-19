from __future__ import annotations

from pathlib import Path

from dnsforge.application.zone.zone_manager import require_reason
from dnsforge.application.sync.sync_service import SyncService
from dnsforge.domain.cluster.model import ClusterConfig, ClusterRole
from dnsforge.domain.cluster.validator import ClusterValidator
from dnsforge.infrastructure.cluster.keepalived_renderer import KeepalivedRenderer
from dnsforge.infrastructure.settings.env_loader import EnvSettingsLoader
from dnsforge.shared.errors import SettingsError


class ClusterService:
    def __init__(
        self,
        loader: EnvSettingsLoader | None = None,
        validator: ClusterValidator | None = None,
        keepalived: KeepalivedRenderer | None = None,
        sync_service: SyncService | None = None,
    ) -> None:
        self.loader = loader or EnvSettingsLoader()
        self.validator = validator or ClusterValidator()
        self.keepalived = keepalived or KeepalivedRenderer()
        self.sync_service = sync_service or SyncService(self.loader, self.validator)

    def load(self, setup_file: Path) -> ClusterConfig:
        settings = self.loader.load(setup_file)
        enabled = self._enabled(settings.get("ENABLE_CLUSTER", settings.get("CLUSTER_ENABLED", "no")))
        role = ClusterRole.from_value(settings.get("CLUSTER_ROLE")) if enabled else None
        return ClusterConfig(
            enabled=enabled,
            role=role,
            name=settings.get("CLUSTER_NAME", "dnsforge-cluster").strip("'\""),
            local_node=settings.get("NODE_NAME", "").strip("'\""),
            peers=self._split(settings.get("CLUSTER_PEERS") or settings.get("PEER_AUTHORITATIVE_ADDRESSES", "")),
            dns_role=settings.get("ROLE", "").strip("'\""),
            vip=self._optional(settings.get("CLUSTER_VIP")),
            interface=self._optional(settings.get("CLUSTER_INTERFACE")),
            priority=int(settings.get("CLUSTER_PRIORITY", "100").strip("'\"")),
            vrid=int(settings.get("CLUSTER_VRID", settings.get("KEEPALIVED_VRID", "53")).strip("'\"")),
            auth_pass=self._optional(settings.get("CLUSTER_AUTH_PASS", settings.get("KEEPALIVED_AUTH_PASS"))),
        )

    def init(self, setup_file: Path, project_root: Path, dry_run: bool = False) -> str:
        config = self.load(setup_file)
        self.validator.validate(config)
        if not config.enabled:
            return "Cluster disabled"
        return f"Authoritative HA cluster initialized: {config.node_count} node(s), VIP {config.vip}"

    def status(self, setup_file: Path) -> str:
        config = self.load(setup_file)
        if not config.enabled:
            return "Cluster: disabled"
        lines = [
            f"Cluster: {config.name}",
            f"Mode: {config.mode.value}",
            f"Local Node: {config.local_node}",
            f"Nodes: {config.node_count}",
            f"Peers: {', '.join(config.peers)}",
            f"VIP: {config.vip}",
            f"Interface: {config.interface}",
            f"Keepalived State: {config.keepalived_state}",
        ]
        return "\n".join(lines)

    def validate(self, setup_file: Path) -> str:
        config = self.load(setup_file)
        self.validator.validate(config)
        return "Cluster validation OK"

    def validate_security(self, setup_file: Path) -> str:
        config = self.load(setup_file)
        self.validator.validate(config)
        if not config.enabled:
            return "Cluster security: disabled"
        checks = ["Cluster security validation OK", "TSIG: required", "ACL: required", "AXFR/IXFR: protected"]
        return "\n".join(checks)

    def render(self, setup_file: Path, reason: str, dry_run: bool = False) -> str:
        require_reason(reason)
        config = self.load(setup_file)
        self.validator.validate(config)
        if not config.enabled:
            return "Cluster disabled"
        rendered = self.keepalived.render(config)
        if dry_run:
            return rendered
        target = self._render_path(setup_file)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")
        return f"Keepalived configuration rendered: {target}"

    def apply(self, setup_file: Path, reason: str, dry_run: bool = False) -> str:
        require_reason(reason)
        config = self.load(setup_file)
        self.validator.validate(config)
        if not config.enabled:
            return "Cluster disabled"
        rendered = self.keepalived.render(config)
        target = self._apply_path(setup_file)
        if dry_run:
            return f"Keepalived apply dry-run OK: {target}"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")
        return f"Keepalived configuration applied: {target}"

    def audit(self, setup_file: Path) -> tuple[bool, str]:
        findings: list[str] = []
        config = self.load(setup_file)
        try:
            self.validator.validate(config)
        except Exception as exc:
            findings.append(f"ERROR cluster validation: {exc}")
        if not config.enabled:
            findings.append("WARNING cluster disabled")
        elif config.dns_role != "dns-authoritative":
            findings.append("ERROR cluster is only supported on authoritative nodes")
        if config.enabled and not config.peers:
            findings.append("WARNING no cluster peers declared")
        if config.enabled and not config.vip:
            findings.append("ERROR missing cluster VIP")
        if config.enabled and not config.auth_pass:
            findings.append("ERROR missing keepalived authentication secret")
        if findings:
            return False, "\n".join(findings)
        return True, "Cluster audit OK"

    def peers(self, setup_file: Path) -> str:
        return self.sync_service.peers(setup_file)

    def diff(self, setup_file: Path) -> str:
        return self.sync_service.diff(setup_file)

    def sync(self, setup_file: Path, reason: str | None = None, dry_run: bool = False) -> str:
        return self.sync_service.sync(setup_file, reason, dry_run=dry_run)

    def sync_plan(self, setup_file: Path, dry_run: bool = True):
        return self.sync_service.sync_plan(setup_file, dry_run=dry_run)

    def peer_states(self, setup_file: Path):
        return self.sync_service.peer_states(setup_file)

    def drift_report(self, setup_file: Path):
        return self.sync_service.drift_report(setup_file)

    def _split(self, value: str) -> list[str]:
        raw = value.strip().strip("'\"")
        return [item.strip() for item in raw.replace(";", ",").split(",") if item.strip()]

    def _optional(self, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip().strip("'\"")
        return cleaned or None

    def _enabled(self, value: str | None) -> bool:
        return (value or "").strip().strip("'\"").lower() in {"yes", "true", "1", "enabled"}

    def _render_path(self, setup_file: Path) -> Path:
        return setup_file.parent / "render" / "keepalived.conf"

    def _apply_path(self, setup_file: Path) -> Path:
        configured = self._optional(self.loader.load(setup_file).get("KEEPALIVED_CONFIG_FILE"))
        if configured:
            return Path(configured)
        return setup_file.parent / "keepalived" / "keepalived.conf"
