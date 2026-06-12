from __future__ import annotations

from pathlib import Path

from dnsforge.domain.initialize.plan import InitializePlan
from dnsforge.infrastructure.bind.configuration_backup import BindConfigurationBackup
from dnsforge.application.deploy.deploy_service import DeployService
from dnsforge.infrastructure.bind.layout import BindLayout, BindLayoutDetector
from dnsforge.infrastructure.initialize.state_store import InitializeStateStore


class InitializeService:
    """Take ownership of local BIND and deploy the DNSForge-managed layout.

    OS package installation is handled exclusively by scripts in install/ during
    profile selection. initialize consumes the edited /etc/dnsforge/setup.conf,
    then performs BIND configuration takeover: backup, render/deploy,
    validation, SELinux context restoration and one-shot lock creation.
    """

    def __init__(
        self,
        bind_backup: BindConfigurationBackup | None = None,
        deploy_service: DeployService | None = None,
        state_store: InitializeStateStore | None = None,
        layout: BindLayout | None = None,
    ) -> None:
        self.bind_backup = bind_backup or BindConfigurationBackup()
        self.deploy_service = deploy_service or DeployService()
        self.state_store = state_store or InitializeStateStore()
        self.layout = layout or BindLayoutDetector().detect()

    def assert_not_initialized(self, setup_file: Path) -> None:
        self.state_store.assert_not_initialized(setup_file)

    def apply(self, plan: InitializePlan, setup_file: Path, target_root: Path = Path("/")) -> None:
        self.assert_not_initialized(setup_file)

        if plan.backup_before_apply:
            result = self.bind_backup.create(target_root=target_root, dry_run=plan.dry_run)
            print(result.summary())

        if plan.render_root is not None:
            self.deploy_service.deploy(plan.render_root, target_root=target_root, dry_run=plan.dry_run)

        if not plan.dry_run:
            self.state_store.mark_initialized(setup_file, role=plan.role, node=plan.node)
