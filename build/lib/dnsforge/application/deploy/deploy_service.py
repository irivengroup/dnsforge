from __future__ import annotations

from pathlib import Path

from dnsforge.infrastructure.bind.layout import BindLayout, BindLayoutDetector
from dnsforge.infrastructure.bind.permissions import BindPermissionApplier
from dnsforge.infrastructure.bind.prerequisites import BindPrerequisites
from dnsforge.infrastructure.bind.validator import BindConfigurationValidator
from dnsforge.infrastructure.install.file_installer import FileInstaller
from dnsforge.infrastructure.system.selinux import SELinuxManager
from dnsforge.infrastructure.system.systemd import SystemdManager


class DeployService:
    """Deploy a previously rendered DNSForge BIND tree.

    Deployment is deliberately separated from rendering and initialization:
    - render creates a staging tree only;
    - deploy copies that tree to the native BIND layout and validates runtime state;
    - initialize orchestrates backup + render + deploy + one-shot lock.
    """

    def __init__(
        self,
        file_installer: FileInstaller | None = None,
        bind_prerequisites: BindPrerequisites | None = None,
        bind_validator: BindConfigurationValidator | None = None,
        permission_applier: BindPermissionApplier | None = None,
        selinux: SELinuxManager | None = None,
        systemd: SystemdManager | None = None,
        layout: BindLayout | None = None,
    ) -> None:
        self.file_installer = file_installer or FileInstaller()
        self.bind_prerequisites = bind_prerequisites or BindPrerequisites()
        self.bind_validator = bind_validator or BindConfigurationValidator()
        self.permission_applier = permission_applier or BindPermissionApplier()
        self.selinux = selinux or SELinuxManager()
        self.systemd = systemd or SystemdManager()
        self.layout = layout or BindLayoutDetector().detect()

    def deploy(self, render_root: Path, target_root: Path = Path("/"), dry_run: bool = False) -> None:
        if not dry_run:
            self.bind_prerequisites.assert_available()

        self.file_installer.install_tree(render_root, target_root=target_root, dry_run=dry_run)
        self.permission_applier.apply(target_root=target_root, dry_run=dry_run)
        self.selinux.ensure_named_contexts(dry_run=dry_run)
        self.bind_validator.checkconf(dry_run=dry_run)
        self.systemd.daemon_reload(dry_run=dry_run)
        self.systemd.enable_now(self.layout.service_name, dry_run=dry_run)
        self.systemd.restart(self.layout.service_name, dry_run=dry_run)
