from __future__ import annotations

from pathlib import Path

from dnsforge.domain.initialize.plan import InitializePlan
from dnsforge.infrastructure.bind.configuration_backup import BindConfigurationBackup
from dnsforge.application.deploy.deploy_service import DeployService
from dnsforge.infrastructure.bind.layout import BindLayout, BindLayoutDetector
from dnsforge.infrastructure.initialize.state_store import InitializeStateStore
from dnsforge.infrastructure.system.package_manager import PackageManager


class InitializeService:
    """Take ownership of local BIND and deploy the DNSForge-managed layout.

    The wheel installs the DNSForge Python package and console entrypoint. The
    privileged initialize/apply flow automatically installs the BIND package set
    when it is missing, then performs configuration takeover: backup, render,
    deploy, validation, SELinux context restoration and service activation.
    """

    def __init__(
        self,
        bind_backup: BindConfigurationBackup | None = None,
        deploy_service: DeployService | None = None,
        state_store: InitializeStateStore | None = None,
        layout: BindLayout | None = None,
        package_manager: PackageManager | None = None,
    ) -> None:
        self.bind_backup = bind_backup or BindConfigurationBackup()
        self.deploy_service = deploy_service or DeployService()
        self.state_store = state_store or InitializeStateStore()
        self.layout = layout or BindLayoutDetector().detect()
        self.package_manager = package_manager or PackageManager()

    def assert_not_initialized(self, setup_file: Path) -> None:
        self.state_store.assert_not_initialized(setup_file)

    def ensure_bind_installed(self, dry_run: bool = False) -> list[list[str]]:
        """Install BIND automatically when it is missing.

        DNSForge owns BIND deployment and configuration. Python wheel installation
        cannot run privileged OS package operations safely, so the first
        privileged initialize/apply path performs the package bootstrap.
        """
        return self.package_manager.ensure_bind(dry_run=dry_run)

    def apply(self, plan: InitializePlan, setup_file: Path, target_root: Path = Path("/")) -> None:
        self.assert_not_initialized(setup_file)

        commands = self.ensure_bind_installed(dry_run=plan.dry_run)
        if commands:
            print("BIND installed by DNSForge package bootstrap")

        if plan.backup_before_apply:
            result = self.bind_backup.create(target_root=target_root, dry_run=plan.dry_run)
            print(result.summary())

        if plan.render_root is not None:
            self.deploy_service.deploy(plan.render_root, target_root=target_root, dry_run=plan.dry_run)

        if not plan.dry_run:
            self.state_store.mark_initialized(setup_file, role=plan.role, node=plan.node)
