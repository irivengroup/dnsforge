from __future__ import annotations

from dnsforge.domain.configure.plan import ConfigurePlan
from dnsforge.infrastructure.install.file_installer import FileInstaller
from dnsforge.infrastructure.system.firewalld import FirewalldManager
from dnsforge.infrastructure.system.package_installer import PackageInstaller
from dnsforge.infrastructure.system.selinux import SELinuxManager
from dnsforge.infrastructure.system.systemd import SystemdManager


class ConfigureService:
    def __init__(
        self,
        package_installer: PackageInstaller | None = None,
        file_installer: FileInstaller | None = None,
        firewalld: FirewalldManager | None = None,
        selinux: SELinuxManager | None = None,
        systemd: SystemdManager | None = None,
    ) -> None:
        self.package_installer = package_installer or PackageInstaller()
        self.file_installer = file_installer or FileInstaller()
        self.firewalld = firewalld or FirewalldManager()
        self.selinux = selinux or SELinuxManager()
        self.systemd = systemd or SystemdManager()

    def apply(self, plan: ConfigurePlan) -> None:
        if not plan.skip_install:
            self.package_installer.install_bind_stack(dry_run=plan.dry_run)

        if plan.render_root is not None:
            self.file_installer.install_tree(plan.render_root, dry_run=plan.dry_run)

        self.firewalld.configure_dns(dry_run=plan.dry_run)
        self.selinux.restore_named_contexts(dry_run=plan.dry_run)
        self.systemd.daemon_reload(dry_run=plan.dry_run)
        self.systemd.enable_now("named", dry_run=plan.dry_run)
        self.systemd.restart("named", dry_run=plan.dry_run)
