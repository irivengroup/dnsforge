from __future__ import annotations


import argparse
import sys
from pathlib import Path

from dnsforge import __version__
from dnsforge.application.audit.product_auditor import ProductAuditor
from dnsforge.application.cluster.cluster_service import ClusterService
from dnsforge.application.deploy.deploy_service import DeployService
from dnsforge.application.initialize.initialize_authoritative import InitializeAuthoritative
from dnsforge.application.initialize.initialize_proxy import InitializeProxy
from dnsforge.application.doctor.doctor_service import DoctorService
from dnsforge.application.health.health_service import HealthService
from dnsforge.application.migration.migration_service import MigrationService
from dnsforge.application.profile.profile_auditor import ProfileAuditor
from dnsforge.application.render.render_authoritative import RenderAuthoritative
from dnsforge.application.render.render_proxy import RenderProxy
from dnsforge.application.security.security_service import SecurityService
from dnsforge.application.security.rpz.rpz_service import RpzService
from dnsforge.application.security.dnssec.dnssec_service import DnssecService
from dnsforge.application.security.view.view_service import ViewService
from dnsforge.application.security.acl.acl_service import AclService
from dnsforge.application.security.security_history_service import SecurityHistoryService
from dnsforge.application.status.status_service import StatusService
from dnsforge.application.validate.validate_authoritative import ValidateAuthoritative
from dnsforge.application.validate.validate_proxy import ValidateProxy
from dnsforge.application.zone.zone_manager import ZoneManager
from dnsforge.domain.zone.model import ZoneType
from dnsforge.domain.zone.policy_validator import ServerProfile
from dnsforge.domain.migration.model import MigrationTarget
from dnsforge.domain.model.proxy_type import ProxyType
from dnsforge.domain.model.roles import DnsRole
from dnsforge.infrastructure.backup.backup_service import BackupService
from dnsforge.infrastructure.filesystem.paths import ProjectPaths
from dnsforge.infrastructure.settings.env_loader import EnvSettingsLoader
from dnsforge.infrastructure.system.privilege_guard import RootPrivilegeGuard
from dnsforge.shared.errors import DnsForgeError


class DnsForgeArgumentParserFactory:
    def build(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(prog="dnsforge", description="DNSForge")
        parser.add_argument("--project-root", default=".", help="Project root")
        sub = parser.add_subparsers(dest="command", required=True)

        self._add_validate(sub)
        self._add_render(sub)
        self._add_deploy(sub)
        self._add_authoritative_profile(sub)
        self._add_proxy_profile(sub)
        self._add_zone(sub)
        self._add_audit(sub)
        self._add_profile(sub)
        self._add_security(sub)
        self._add_status(sub)
        self._add_health(sub)
        self._add_doctor(sub)
        self._add_backup(sub)
        self._add_restore(sub)
        self._add_migrate(sub)
        self._add_cluster(sub)
        self._add_acl(sub)
        self._add_view(sub)
        self._add_dnssec(sub)
        self._add_rpz(sub)
        self._add_version(sub)

        return parser

    def _add_version(self, sub) -> None:
        sub.add_parser("version", help="Show DNSForge version")

    def _add_validate(self, sub) -> None:
        root = sub.add_parser("validate", help="Validate settings")
        inner = root.add_subparsers(dest="role", required=False)
        p = inner.add_parser("proxy")
        p.add_argument("node", nargs="?")
        p.add_argument("--type", choices=ProxyType.choices(), dest="proxy_type")
        a = inner.add_parser("authoritative")
        a.add_argument("node", nargs="?")

    def _add_render(self, sub) -> None:
        root = sub.add_parser("render", help="Render configuration")
        inner = root.add_subparsers(dest="role", required=False)
        p = inner.add_parser("proxy")
        p.add_argument("node", nargs="?")
        p.add_argument("--type", choices=ProxyType.choices(), dest="proxy_type")
        a = inner.add_parser("authoritative")
        a.add_argument("node", nargs="?")

    def _add_deploy(self, sub) -> None:
        root = sub.add_parser("deploy", help="Deploy previously rendered BIND configuration")
        root.add_argument("--target-root", default="/")
        root.add_argument("--dry-run", action="store_true")
        inner = root.add_subparsers(dest="role", required=False)
        p = inner.add_parser("proxy")
        p.add_argument("node", nargs="?")
        p.add_argument("--type", choices=ProxyType.choices(), dest="proxy_type")
        p.add_argument("--target-root", default=None)
        p.add_argument("--dry-run", action="store_true")
        a = inner.add_parser("authoritative")
        a.add_argument("node", nargs="?")
        a.add_argument("--target-root", default=None)
        a.add_argument("--dry-run", action="store_true")

    def _add_initialize(self, sub) -> None:
        root = sub.add_parser("initialize", help="Initialize local DNSForge node")
        inner = root.add_subparsers(dest="role", required=False)
        p = inner.add_parser("proxy")
        p.add_argument("node", nargs="?")
        p.add_argument("--type", choices=ProxyType.choices(), dest="proxy_type")
        p.add_argument("--render-only", action="store_true")
        p.add_argument("--apply", action="store_true", help="Apply a previously rendered DNSForge BIND configuration")
        p.add_argument("--dry-run", action="store_true")
        a = inner.add_parser("authoritative")
        a.add_argument("node", nargs="?")
        a.add_argument("--render-only", action="store_true")
        a.add_argument("--apply", action="store_true", help="Apply a previously rendered DNSForge BIND configuration")
        a.add_argument("--dry-run", action="store_true")
        root.add_argument("--render-only", action="store_true")
        root.add_argument(
            "--apply", action="store_true", help="Apply a previously rendered DNSForge BIND configuration"
        )
        root.add_argument("--dry-run", action="store_true")

    def _add_authoritative_profile(self, sub) -> None:
        root = sub.add_parser("authoritative", help="Manage an authoritative DNS server profile")
        inner = root.add_subparsers(dest="profile_action", required=True)
        init = inner.add_parser("initialize", help="Initialize this node as authoritative")
        init.add_argument("node", nargs="?", default="local")
        init.add_argument("--render-only", action="store_true")
        init.add_argument(
            "--apply", action="store_true", help="Apply a previously rendered authoritative BIND configuration"
        )
        init.add_argument("--dry-run", action="store_true")

    def _add_proxy_profile(self, sub) -> None:
        root = sub.add_parser("proxy", help="Manage a proxy DNS server profile")
        inner = root.add_subparsers(dest="profile_action", required=True)
        init = inner.add_parser("initialize", help="Initialize this node as proxy forwarder or hybrid")
        init.add_argument("node", nargs="?", default="local")
        init.add_argument("--type", choices=ProxyType.choices(), dest="proxy_type", default=ProxyType.HYBRID.value)
        init.add_argument("--render-only", action="store_true")
        init.add_argument("--apply", action="store_true", help="Apply a previously rendered proxy BIND configuration")
        init.add_argument("--dry-run", action="store_true")

    def _add_zone(self, sub) -> None:
        zone = sub.add_parser("zone", help="Manage DNS zones")
        inner = zone.add_subparsers(dest="action", required=True)
        inner.add_parser("list")
        history = inner.add_parser("history")
        history.add_argument("name")
        get = inner.add_parser("get")
        get.add_argument("--name", required=True)
        show = inner.add_parser("show")
        show.add_argument("name", nargs="?")
        show.add_argument("--zone", dest="zone_name")
        show.add_argument("--version", type=int)
        diff = inner.add_parser("diff")
        diff.add_argument("--zone", required=True)
        diff.add_argument("--from", required=True, type=int, dest="from_version")
        diff.add_argument("--to", required=True, type=int, dest="to_version")
        rollback = inner.add_parser("rollback")
        rollback.add_argument("--zone", required=True)
        rollback.add_argument("--version", required=True, type=int)
        create = inner.add_parser("create")
        create.add_argument("--name", required=True)
        create.add_argument("--type", required=True, choices=[item.value for item in ZoneType], dest="zone_type")
        create.add_argument("--views", required=True)
        create.add_argument("--profile", choices=[item.value for item in ServerProfile], default="authoritative")
        create.add_argument("--cluster")
        create.add_argument("--disabled", action="store_true")
        edit = inner.add_parser("edit")
        edit.add_argument("name")
        edit.add_argument("--add", dest="add_record")
        edit.add_argument("--update", dest="update_record")
        edit.add_argument("--delete", dest="delete_record")
        edit.add_argument("--ttl", type=int)
        for action in ("disable", "enable", "delete"):
            parser = inner.add_parser(action)
            parser.add_argument("--name", required=True)

    def _add_audit(self, sub) -> None:
        audit = sub.add_parser("audit", help="Audit product consistency")
        audit.add_argument("--strict", action="store_true")

    def _add_profile(self, sub) -> None:
        profile = sub.add_parser("profile", help="Audit configuration profiles")
        inner = profile.add_subparsers(dest="action", required=True)
        inner.add_parser("audit")

    def _add_security(self, sub) -> None:
        security = sub.add_parser("security", help="Show or audit DNS security controls")
        security.add_argument("--setup-file", default="/etc/dnsforge/setup.conf")
        inner = security.add_subparsers(dest="action", required=True)
        inner.add_parser("show")
        inner.add_parser("audit")
        inner.add_parser("history")
        rollback = inner.add_parser("rollback")
        rollback.add_argument("--version")

    def _add_status(self, sub) -> None:
        p = sub.add_parser("status", help="Show local DNSForge status")
        p.add_argument("--setup-file", default="/etc/dnsforge/setup.conf")

    def _add_health(self, sub) -> None:
        p = sub.add_parser("health", help="Run local health checks")
        p.add_argument("--setup-file", default="/etc/dnsforge/setup.conf")

    def _add_doctor(self, sub) -> None:
        p = sub.add_parser("doctor", help="Show recommendations")
        p.add_argument("--setup-file", default="/etc/dnsforge/setup.conf")

    def _add_backup(self, sub) -> None:
        root = sub.add_parser("backup", help="Manage backups")
        root.add_argument("--backup-root", default="/var/backups/dnsforge")
        inner = root.add_subparsers(dest="action", required=True)
        create = inner.add_parser("create")
        create.add_argument("--setup-file", default="/etc/dnsforge/setup.conf")
        create.add_argument("--dry-run", action="store_true")
        inner.add_parser("list")

    def _add_restore(self, sub) -> None:
        p = sub.add_parser("restore", help="Restore a backup")
        p.add_argument("--backup", required=True)
        p.add_argument("--target-root", default="/")
        p.add_argument("--dry-run", action="store_true")

    def _add_migrate(self, sub) -> None:
        p = sub.add_parser("migrate", help="Migrate proxy-forwarder <-> proxy-hybrid")
        p.add_argument("--to", required=True, choices=["proxy-forwarder", "proxy-hybrid"], dest="target")
        p.add_argument("--setup-file", default="/etc/dnsforge/setup.conf")
        p.add_argument("--dry-run", action="store_true")

    def _add_cluster(self, sub) -> None:
        cluster = sub.add_parser("cluster", help="Manage DNSForge cluster")
        cluster.add_argument("--setup-file", default="/etc/dnsforge/setup.conf")
        inner = cluster.add_subparsers(dest="action", required=True)

        init = inner.add_parser("init")
        init.add_argument("--setup-file", default=None)
        init.add_argument("--dry-run", action="store_true")
        status = inner.add_parser("status")
        status.add_argument("--setup-file", default=None)
        validate = inner.add_parser("validate")
        validate.add_argument("--setup-file", default=None)
        validate_security = inner.add_parser("validate-security")
        validate_security.add_argument("--setup-file", default=None)
        sync = inner.add_parser("sync")
        sync.add_argument("--setup-file", default=None)
        sync.add_argument("--dry-run", action="store_true")

    def _add_acl(self, sub) -> None:
        acl = sub.add_parser("acl", help="Manage DNS ACLs")
        acl.add_argument("--state-file", default="/etc/dnsforge/acls.json")
        inner = acl.add_subparsers(dest="action", required=True)
        inner.add_parser("list")
        show = inner.add_parser("show")
        show.add_argument("name")
        create = inner.add_parser("create")
        create.add_argument("name")
        delete = inner.add_parser("delete")
        delete.add_argument("name")
        add = inner.add_parser("add-network")
        add.add_argument("name")
        add.add_argument("network")
        rm = inner.add_parser("remove-network")
        rm.add_argument("name")
        rm.add_argument("network")

    def _add_view(self, sub) -> None:
        view = sub.add_parser("view", help="Manage DNS views")
        view.add_argument("--state-file", default="/etc/dnsforge/views.json")
        inner = view.add_subparsers(dest="action", required=True)
        inner.add_parser("list")
        create = inner.add_parser("create")
        create.add_argument("name")
        delete = inner.add_parser("delete")
        delete.add_argument("name")
        attach = inner.add_parser("attach-zone")
        attach.add_argument("name")
        attach.add_argument("zone")

    def _add_dnssec(self, sub) -> None:
        dnssec = sub.add_parser("dnssec", help="Manage DNSSEC controls")
        dnssec.add_argument("--setup-file", default="/etc/dnsforge/setup.conf")
        inner = dnssec.add_subparsers(dest="action", required=True)
        for action in ("status", "validate", "rotate-ksk", "rotate-zsk", "check-expiry"):
            inner.add_parser(action)

    def _add_rpz(self, sub) -> None:
        rpz = sub.add_parser("rpz", help="Manage RPZ DNS firewall")
        rpz.add_argument("--setup-file", default="/etc/dnsforge/setup.conf")
        inner = rpz.add_subparsers(dest="action", required=True)
        for action in ("status", "enable", "update"):
            inner.add_parser(action)
        test = inner.add_parser("test")
        test.add_argument("domain")


class DnsForgeCommandDispatcher:
    def _resolve_role_from_setup(
        self, paths: ProjectPaths, role: str | None, node: str | None = None, proxy_type: str | None = None
    ) -> tuple[str, str, str | None] | None:
        resolved_node = node or "local"
        resolved_proxy_type = proxy_type
        if role is not None:
            return role, resolved_node, resolved_proxy_type

        settings = EnvSettingsLoader().load(paths.setup_file)
        role_value = settings.get("ROLE", "").strip()
        resolved_node = settings.get("NODE_NAME", resolved_node) or resolved_node
        if role_value == DnsRole.PROXY.value:
            return "proxy", resolved_node, settings.get("PROXY_TYPE", resolved_proxy_type or "forwarder")
        if role_value == DnsRole.AUTHORITATIVE.value:
            return "authoritative", resolved_node, resolved_proxy_type

        print(f"ERROR: unsupported ROLE in {paths.setup_file}: {role_value or '<missing>'}", file=sys.stderr)
        return None

    def dispatch(self, args: argparse.Namespace) -> int:
        paths = ProjectPaths(Path(args.project_root).resolve())

        if args.command == "version":
            print(__version__)
            return 0

        if args.command == "validate":
            resolved = self._resolve_role_from_setup(
                paths, args.role, getattr(args, "node", None), getattr(args, "proxy_type", None)
            )
            if resolved is None:
                return 2
            role, node, proxy_type = resolved
            if role == "proxy":
                ValidateProxy(paths).execute(node, ProxyType.from_value(proxy_type or "forwarder"))
            elif role == "authoritative":
                ValidateAuthoritative(paths).execute(node)
            else:
                return 2
            return 0

        if args.command == "render":
            resolved = self._resolve_role_from_setup(
                paths, args.role, getattr(args, "node", None), getattr(args, "proxy_type", None)
            )
            if resolved is None:
                return 2
            role, node, proxy_type = resolved
            if role == "proxy":
                RenderProxy(paths).execute(node, ProxyType.from_value(proxy_type or "forwarder"))
            elif role == "authoritative":
                RenderAuthoritative(paths).execute(node)
            else:
                return 2
            return 0

        if args.command == "deploy":
            resolved = self._resolve_role_from_setup(
                paths, args.role, getattr(args, "node", None), getattr(args, "proxy_type", None)
            )
            if resolved is None:
                return 2
            role, node, _proxy_type = resolved

            render_role = DnsRole.PROXY if role == "proxy" else DnsRole.AUTHORITATIVE
            render_root = paths.render_dir(render_role, node)
            target_root = Path(args.target_root or "/")
            DeployService().deploy(render_root, target_root=target_root, dry_run=args.dry_run)
            return 0

        if args.command == "authoritative":
            if args.profile_action == "initialize":
                if getattr(args, "render_only", False) and getattr(args, "apply", False):
                    print("ERROR: --render-only and --apply are mutually exclusive", file=sys.stderr)
                    return 2
                InitializeAuthoritative(paths).execute(
                    args.node,
                    render_only=args.render_only,
                    dry_run=args.dry_run,
                    apply_only=args.apply,
                )
                return 0
            return 2

        if args.command == "proxy":
            if args.profile_action == "initialize":
                if getattr(args, "render_only", False) and getattr(args, "apply", False):
                    print("ERROR: --render-only and --apply are mutually exclusive", file=sys.stderr)
                    return 2
                InitializeProxy(paths).execute(
                    args.node,
                    ProxyType.from_value(args.proxy_type or ProxyType.HYBRID.value),
                    render_only=args.render_only,
                    dry_run=args.dry_run,
                    apply_only=args.apply,
                )
                return 0
            return 2

        if args.command == "zone":
            manager = ZoneManager(paths)
            if args.action == "list":
                for zone in manager.list():
                    print(f"{zone.name}\t{zone.zone_type.value}\t{'enabled' if zone.enabled else 'disabled'}")
                return 0
            if args.action == "get":
                zone = manager.get(args.name)
                print(f"name={zone.name}")
                print(f"type={zone.zone_type.value}")
                print(f"enabled={'yes' if zone.enabled else 'no'}")
                print(f"views={','.join(zone.views)}")
                if zone.cluster:
                    print(f"cluster={zone.cluster}")
                return 0
            if args.action == "history":
                print(manager.history_list(args.name))
                return 0
            if args.action == "show":
                zone_name = getattr(args, "zone_name", None) or getattr(args, "name", None)
                if not zone_name:
                    print("ERROR: zone show requires a zone name", file=sys.stderr)
                    return 2
                if getattr(args, "version", None):
                    print(manager.show_version(zone_name, args.version))
                else:
                    print(manager.show(zone_name))
                return 0
            if args.action == "diff":
                print(manager.history_diff(args.zone, args.from_version, args.to_version))
                return 0
            if args.action == "rollback":
                print(manager.rollback(args.zone, args.version))
                return 0
            if args.action == "create":
                views = [i.strip() for i in args.views.replace(";", ",").split(",") if i.strip()]
                manager = ZoneManager(paths, profile=ServerProfile.from_value(args.profile))
                manager.create(args.name, args.zone_type, views, cluster=args.cluster, enabled=not args.disabled)
                return 0
            if args.action == "edit":
                ops = [args.add_record, args.update_record, args.delete_record]
                if sum(1 for item in ops if item) != 1:
                    print("ERROR: zone edit requires exactly one of --add, --update or --delete", file=sys.stderr)
                    return 2
                if args.add_record:
                    manager.add_record(args.name, args.add_record, ttl=args.ttl)
                if args.update_record:
                    manager.update_record(args.name, args.update_record, ttl=args.ttl)
                if args.delete_record:
                    manager.delete_record(args.name, args.delete_record)
                return 0
            if args.action == "disable":
                manager.disable(args.name)
                return 0
            if args.action == "enable":
                manager.enable(args.name)
                return 0
            if args.action == "delete":
                manager.delete(args.name)
                return 0
            return 2

        if args.command == "audit":
            report = ProductAuditor().audit(paths.project_root)
            print(report.render())
            if not report.ok:
                return 1
            if args.strict and report.findings:
                return 1
            return 0

        if args.command == "profile":
            if args.action == "audit":
                errors = ProfileAuditor().audit_templates()
                if errors:
                    for error in errors:
                        print(f"ERROR: {error}")
                    return 1
                print("Profile audit OK")
                return 0
            return 2

        if args.command == "security":
            service = SecurityService()
            setup_file = Path(args.setup_file)
            if args.action == "show":
                print(service.show(setup_file))
                return 0
            if args.action == "audit":
                ok, output = service.audit(setup_file)
                print(output)
                return 0 if ok else 1
            if args.action == "history":
                print(SecurityHistoryService().history())
                return 0
            if args.action == "rollback":
                print(SecurityHistoryService().rollback(args.version))
                return 0
            return 2

        if args.command == "status":
            print(StatusService().show(Path(args.setup_file)))
            return 0

        if args.command == "health":
            report = HealthService().check(Path(args.setup_file), paths.project_root)
            print(report.render())
            return 0 if report.ok else 1

        if args.command == "doctor":
            print(DoctorService().diagnose(Path(args.setup_file)))
            return 0

        if args.command == "backup":
            service = BackupService(Path(args.backup_root))
            if args.action == "create":
                archive = service.create(paths.project_root, Path(args.setup_file), dry_run=args.dry_run)
                print(archive)
                return 0
            if args.action == "list":
                for item in service.list():
                    print(item)
                return 0
            return 2

        if args.command == "restore":
            BackupService().restore(Path(args.backup), Path(args.target_root), dry_run=args.dry_run)
            print("Restore completed" if not args.dry_run else "Restore dry-run OK")
            return 0

        if args.command == "migrate":
            result = MigrationService().migrate(
                Path(args.setup_file), MigrationTarget.from_value(args.target), dry_run=args.dry_run
            )
            print(result)
            return 0

        if args.command == "cluster":
            service = ClusterService()
            setup_file = Path(args.setup_file or "/etc/dnsforge/setup.conf")
            if args.action == "init":
                print(service.init(setup_file, paths.project_root, dry_run=args.dry_run))
                return 0
            if args.action == "status":
                print(service.status(setup_file))
                return 0
            if args.action == "validate":
                print(service.validate(setup_file))
                return 0
            if args.action == "validate-security":
                print(service.validate_security(setup_file))
                return 0
            if args.action == "sync":
                print(service.sync(setup_file, dry_run=args.dry_run))
                return 0
            return 2

        if args.command == "acl":
            service = AclService(Path(args.state_file))
            if args.action == "list":
                print(service.list())
                return 0
            if args.action == "show":
                print(service.show(args.name))
                return 0
            if args.action == "create":
                print(service.create(args.name))
                return 0
            if args.action == "delete":
                print(service.delete(args.name))
                return 0
            if args.action == "add-network":
                print(service.add_network(args.name, args.network))
                return 0
            if args.action == "remove-network":
                print(service.remove_network(args.name, args.network))
                return 0
            return 2

        if args.command == "view":
            service = ViewService(Path(args.state_file))
            if args.action == "list":
                print(service.list())
                return 0
            if args.action == "create":
                print(service.create(args.name))
                return 0
            if args.action == "delete":
                print(service.delete(args.name))
                return 0
            if args.action == "attach-zone":
                print(service.attach_zone(args.name, args.zone))
                return 0
            return 2

        if args.command == "dnssec":
            service = DnssecService()
            setup_file = Path(args.setup_file)
            if args.action == "status":
                print(service.status(setup_file))
                return 0
            if args.action == "validate":
                print(service.validate(setup_file))
                return 0
            if args.action == "rotate-ksk":
                print(service.rotate_ksk())
                return 0
            if args.action == "rotate-zsk":
                print(service.rotate_zsk())
                return 0
            if args.action == "check-expiry":
                print(service.check_expiry())
                return 0
            return 2

        if args.command == "rpz":
            service = RpzService()
            setup_file = Path(args.setup_file)
            if args.action == "status":
                print(service.status(setup_file))
                return 0
            if args.action == "enable":
                print(service.enable(setup_file))
                return 0
            if args.action == "update":
                print(service.update())
                return 0
            if args.action == "test":
                print(service.test(args.domain))
                return 0
            return 2

        return 2


class DnsForgeCli:
    def __init__(
        self,
        parser_factory: DnsForgeArgumentParserFactory | None = None,
        dispatcher: DnsForgeCommandDispatcher | None = None,
        privilege_guard: RootPrivilegeGuard | None = None,
    ) -> None:
        self.parser_factory = parser_factory or DnsForgeArgumentParserFactory()
        self.dispatcher = dispatcher or DnsForgeCommandDispatcher()
        self.privilege_guard = privilege_guard or RootPrivilegeGuard()

    def run(self, argv: list[str] | None = None) -> int:
        parser = self.parser_factory.build()
        args = parser.parse_args(argv)
        try:
            self.privilege_guard.require_root()
            return self.dispatcher.dispatch(args)
        except DnsForgeError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
