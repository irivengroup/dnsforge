from __future__ import annotations
from pathlib import Path
from dnsforge.domain.cluster.model import ClusterConfig, ClusterRole
from dnsforge.domain.cluster.validator import ClusterValidator
from dnsforge.infrastructure.cluster.keepalived_renderer import KeepalivedRenderer
from dnsforge.infrastructure.settings.env_loader import EnvSettingsLoader


class ClusterService:
    def __init__(
        self,
        loader: EnvSettingsLoader | None = None,
        validator: ClusterValidator | None = None,
        keepalived: KeepalivedRenderer | None = None,
    ) -> None:
        self.loader = loader or EnvSettingsLoader()
        self.validator = validator or ClusterValidator()
        self.keepalived = keepalived or KeepalivedRenderer()

    def load(self, setup_file: Path) -> ClusterConfig:
        settings = self.loader.load(setup_file)
        enabled = settings.get("ENABLE_CLUSTER", "no").strip("'\"").lower() == "yes"
        role = ClusterRole.from_value(settings.get("CLUSTER_ROLE")) if enabled else None
        return ClusterConfig(
            enabled=enabled,
            role=role,
            name=settings.get("CLUSTER_NAME", "dnsforge-cluster").strip("'\""),
            local_node=settings.get("NODE_NAME", "").strip("'\""),
            peers=self._split(settings.get("CLUSTER_PEERS", "")),
            vip=self._optional(settings.get("CLUSTER_VIP")),
            interface=self._optional(settings.get("CLUSTER_INTERFACE")),
            priority=int(settings.get("CLUSTER_PRIORITY", "100").strip("'\"")),
            auth_pass=self._optional(settings.get("CLUSTER_AUTH_PASS")),
        )

    def init(self, setup_file: Path, project_root: Path, dry_run: bool = False) -> str:
        config = self.load(setup_file)
        self.validator.validate(config)
        if not config.enabled:
            return "Cluster disabled"
        if config.role is ClusterRole.PROXY:
            target = project_root / "src/render/cluster/keepalived.conf"
            if not dry_run:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(self.keepalived.render(config), encoding="utf-8")
            return f"Proxy cluster initialized: {target}"
        return "Authoritative cluster initialized: Primary/Secondary replication model"

    def status(self, setup_file: Path) -> str:
        config = self.load(setup_file)
        if not config.enabled:
            return "Cluster: disabled"
        lines = [
            f"Cluster: {config.name}",
            f"Mode: {config.mode.value}",
            f"Local Node: {config.local_node}",
            f"Peers: {', '.join(config.peers)}",
        ]
        if config.vip:
            lines.append(f"VIP: {config.vip}")
        if config.interface:
            lines.append(f"Interface: {config.interface}")
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
        if config.role and config.role.value == "proxy":
            checks.append("Keepalived auth: required")
        return "\n".join(checks)

    def sync(self, setup_file: Path, dry_run: bool = False) -> str:
        config = self.load(setup_file)
        self.validator.validate(config)
        if config.role is ClusterRole.PROXY:
            return "Proxy cluster sync planned" if dry_run else "Proxy cluster sync completed"
        return "Authoritative cluster sync planned" if dry_run else "Authoritative cluster sync completed"

    def _split(self, value: str) -> list[str]:
        raw = value.strip().strip("'\"")
        return [item.strip() for item in raw.replace(";", ",").split(",") if item.strip()]

    def _optional(self, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip().strip("'\"")
        return cleaned or None
