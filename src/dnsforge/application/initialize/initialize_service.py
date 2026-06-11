from __future__ import annotations

from pathlib import Path

from dnsforge.domain.initialize.plan import InitializePlan
from dnsforge.infrastructure.bind.configuration_backup import BindConfigurationBackup
from dnsforge.infrastructure.bind.prerequisites import BindPrerequisites
from dnsforge.infrastructure.bind.validator import BindConfigurationValidator
from dnsforge.infrastructure.bind.layout import BindLayout, BindLayoutDetector
from dnsforge.infrastructure.bind.permissions import BindPermissionApplier
from dnsforge.infrastructure.install.file_installer import FileInstaller
from dnsforge.infrastructure.initialize.state_store import InitializeStateStore
from dnsforge.infrastructure.system.selinux import SELinuxManager
from dnsforge.infrastructure.system.systemd import SystemdManager


class InitializeService:
    """Take ownership of an already installed local BIND instance.

    Package installation is deliberately out of scope. The installer in install/
    owns OS package deployment. initialize owns BIND configuration takeover:
    prerequisite checks, full mv + tar.gz backup, rendered file deployment,
    validation, SELinux context restoration and named service activation.
    """

    def __init__(
        self,
        file_installer: FileInstaller | None = None,
        bind_backup: BindConfigurationBackup | None = None,
        bind_prerequisites: BindPrerequisites | None = None,
        bind_validator: BindConfigurationValidator | None = None,
        selinux: SELinuxManager | None = None,
        systemd: SystemdManager | None = None,
        state_store: InitializeStateStore | None = None,
        permission_applier: BindPermissionApplier | None = None,
        layout: BindLayout | None = None,
    ) -> None:
        self.file_installer = file_installer or FileInstaller()
        self.bind_backup = bind_backup or BindConfigurationBackup()
        self.bind_prerequisites = bind_prerequisites or BindPrerequisites()
        self.bind_validator = bind_validator or BindConfigurationValidator()
        self.selinux = selinux or SELinuxManager()
        self.systemd = systemd or SystemdManager()
        self.state_store = state_store or InitializeStateStore()
        self.layout = layout or BindLayoutDetector().detect()
        self.permission_applier = permission_applier or BindPermissionApplier()

    def assert_not_initialized(self, setup_file: Path) -> None:
        self.state_store.assert_not_initialized(setup_file)

    def apply(self, plan: InitializePlan, setup_file: Path, target_root: Path = Path("/")) -> None:
        self.assert_not_initialized(setup_file)

        if not plan.dry_run:
            self.bind_prerequisites.assert_available()

        if plan.backup_before_apply:
            result = self.bind_backup.create(target_root=target_root, dry_run=plan.dry_run)
            print(result.summary())

        if plan.render_root is not None:
            self.file_installer.install_tree(plan.render_root, target_root=target_root, dry_run=plan.dry_run)

        self.permission_applier.apply(target_root=target_root, dry_run=plan.dry_run)
        self.selinux.ensure_named_contexts(dry_run=plan.dry_run)
        self.bind_validator.checkconf(dry_run=plan.dry_run)
        self.systemd.daemon_reload(dry_run=plan.dry_run)
        self.systemd.enable_now(self.layout.service_name, dry_run=plan.dry_run)
        self.systemd.restart(self.layout.service_name, dry_run=plan.dry_run)

        if not plan.dry_run:
            self.state_store.mark_initialized(setup_file, role=plan.role, node=plan.node)
