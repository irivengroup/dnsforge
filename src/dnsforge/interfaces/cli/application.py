from __future__ import annotations


import argparse
import json
import sys
from pathlib import Path

from dnsforge import __version__
from dnsforge.application.audit.product_auditor import ProductAuditor
from dnsforge.application.cluster.cluster_service import ClusterService
from dnsforge.application.catalog.catalog_service import CatalogService
from dnsforge.application.config.config_service import ConfigService
from dnsforge.application.deploy.deploy_service import DeployService
from dnsforge.application.docs.commands_doc_service import CommandDocumentationService
from dnsforge.application.disaster.disaster_service import DisasterRecoveryService
from dnsforge.application.initialize.initialize_command import InitializeCommand
from dnsforge.application.doctor.doctor_service import DoctorService
from dnsforge.application.health.health_service import HealthService
from dnsforge.application.jobs.job_service import JobService
from dnsforge.application.health.score_service import HealthScoreService
from dnsforge.application.reports.report_service import ReportService
from dnsforge.application.drift.drift_service import DriftService
from dnsforge.application.events.event_tail_service import EventTailService
from dnsforge.application.metrics.metrics_service import MetricsCollector
from dnsforge.application.sync.provider_service import SyncProviderService
from dnsforge.application.security.dnssec_policy_service import DnssecPolicyService
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
        self._add_initialize(sub)
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
        self._add_catalog(sub)
        self._add_config(sub)
        self._add_acl(sub)
        self._add_view(sub)
        self._add_dnssec(sub)
        self._add_rpz(sub)
        self._add_version(sub)
        self._add_generate(sub)
        self._add_disaster(sub)
        self._add_job(sub)
        self._add_report(sub)
        self._add_drift(sub)
        self._add_events(sub)
        self._add_metrics(sub)
        self._add_sync(sub)

        return parser

    def _add_job(self, sub) -> None:
        job = sub.add_parser("job", help="Manage local DNSForge operation jobs")
        inner = job.add_subparsers(dest="action", required=True)
        inner.add_parser("list", help="List registered jobs")
        show = inner.add_parser("show", help="Show one job definition")
        show.add_argument("job_id")
        run = inner.add_parser("run", help="Queue or dry-run one local job")
        run.add_argument("job_id")
        run.add_argument("--dry-run", action="store_true")
        cancel = inner.add_parser("cancel", help="Cancel a queued local job")
        cancel.add_argument("job_id")
        inner.add_parser("history", help="Show local job run history")

    def _add_report(self, sub) -> None:
        report = sub.add_parser("report", help="Generate unified DNSForge operational reports")
        inner = report.add_subparsers(dest="action", required=True)
        generate = inner.add_parser("generate")
        generate.add_argument("--format", choices=["json", "yaml", "html"], default="json")
        generate.add_argument("--output")

    def _add_drift(self, sub) -> None:
        drift = sub.add_parser("drift", help="Detect configuration drift against rendered DNSForge state")
        inner = drift.add_subparsers(dest="action", required=True)
        audit = inner.add_parser("audit")
        audit.add_argument("--target-root", default="/")

    def _add_events(self, sub) -> None:
        events = sub.add_parser("events", help="Read local DNSForge audit events")
        events.add_argument("--event-log", default=None)
        inner = events.add_subparsers(dest="action", required=True)
        tail = inner.add_parser("tail")
        tail.add_argument("--limit", type=int, default=20)
        tail.add_argument("--category")

    def _add_metrics(self, sub) -> None:
        metrics = sub.add_parser("metrics", help="Collect local DNSForge metrics")
        inner = metrics.add_subparsers(dest="action", required=True)
        inner.add_parser("show")

    def _add_sync(self, sub) -> None:
        sync = sub.add_parser("sync", help="Show sync provider boundaries")
        inner = sync.add_subparsers(dest="action", required=True)
        inner.add_parser("providers")

    def _add_disaster(self, sub) -> None:
        disaster = sub.add_parser("disaster", help="Manage full-node disaster recovery snapshots")
        disaster.add_argument("--target-root", default="/")
        inner = disaster.add_subparsers(dest="action", required=True)
        snapshot = inner.add_parser("snapshot")
        snapshot.add_argument("--reason", required=True)
        restore = inner.add_parser("restore")
        restore.add_argument("--snapshot", required=True)
        restore.add_argument("--dry-run", action="store_true")
        verify = inner.add_parser("verify")
        verify.add_argument("--snapshot", required=True)

    def _add_version(self, sub) -> None:
        sub.add_parser("version", help="Show DNSForge version")

    def _add_generate(self, sub) -> None:
        generate = sub.add_parser("generate", help="Generate documentation from runtime metadata")
        inner = generate.add_subparsers(dest="action", required=True)
        commands = inner.add_parser("commands-doc", help="Generate docs/COMMANDS.md from the real CLI parser")
        commands.add_argument("--output", default="docs/COMMANDS.md")

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
        root = sub.add_parser("initialize", help="Initialize local DNSForge node from /etc/dnsforge/setup.conf")
        root.add_argument("--render-only", action="store_true")
        root.add_argument(
            "--apply", action="store_true", help="Apply a previously rendered DNSForge BIND configuration"
        )
        root.add_argument("--dry-run", action="store_true")

    def _add_zone(self, sub) -> None:
        zone = sub.add_parser("zone", help="Manage DNS zones")
        inner = zone.add_subparsers(dest="action", required=True)

        list_parser = inner.add_parser("list", help="Inventory configured zones")
        list_parser.add_argument("--enabled", action="store_true", help="Show enabled/active zones only")
        list_parser.add_argument("--format", choices=["text", "json"], default="text")

        history = inner.add_parser("history", help="Show zone change history")
        history.add_argument("name")

        get = inner.add_parser("get", help="Show raw zone metadata")
        get.add_argument("--name", required=True)

        show = inner.add_parser("show", help="Show a zone")
        show.add_argument("name", nargs="?")
        show.add_argument("--zone", dest="zone_name")
        show.add_argument("--version", type=int)

        status = inner.add_parser("status", help="Show zone lifecycle status")
        status.add_argument("name")

        backup = inner.add_parser("backup", help="Create an explicit zone snapshot")
        backup.add_argument("name")
        backup.add_argument("--reason", required=True)

        diff = inner.add_parser("diff", help="Diff two zone history versions")
        diff.add_argument("--zone", dest="zone_name", required=True)
        diff.add_argument("--from", type=int, dest="from_version", required=True)
        diff.add_argument("--to", type=int, dest="to_version", required=True)

        rollback = inner.add_parser("rollback", help="Rollback a zone to a history version")
        rollback.add_argument("--zone", dest="zone_name", required=True)
        rollback.add_argument("--version", type=int, required=True)
        rollback.add_argument("--reason", required=True)

        search = inner.add_parser("search", help="Search zones or records inside a zone")
        search.add_argument("--zone", dest="zone_name")
        search.add_argument("--owner")
        search.add_argument("--view")
        search.add_argument("--state")
        search.add_argument("--environment")
        search.add_argument("--classification")
        search.add_argument("--record-name")
        search.add_argument("--record-type")
        search.add_argument("--value")

        create = inner.add_parser("create", help="Create a zone")
        create.add_argument("name", nargs="?")
        create.add_argument("--name", dest="zone_name")
        create.add_argument("--type", choices=[item.value for item in ZoneType], dest="zone_type", default="master")
        create.add_argument("--views", default="internal")
        create.add_argument("--profile", choices=[item.value for item in ServerProfile], default="authoritative")
        create.add_argument("--cluster")
        create.add_argument("--description", default="")
        create.add_argument("--business-owner", default="")
        create.add_argument("--technical-owner", default="")
        create.add_argument("--environment", default="")
        create.add_argument("--classification", default="")
        create.add_argument("--state", choices=["draft", "active", "deprecated", "retired"], default="draft")
        create.add_argument("--disabled", action="store_true")
        create.add_argument("--reason", required=True)

        edit = inner.add_parser("edit", help="Edit records in a zone")
        edit.add_argument("name")
        edit.add_argument("--add", dest="add_record")
        edit.add_argument("--update", dest="update_record")
        edit.add_argument("--delete", dest="delete_record")
        edit.add_argument("--ttl", type=int)
        edit.add_argument("--reason", required=True)

        for action in ("disable", "enable", "retire", "delete"):
            parser = inner.add_parser(action)
            parser.add_argument("name", nargs="?")
            parser.add_argument("--name", dest="zone_name")
            parser.add_argument("--reason", required=True)

    def _add_audit(self, sub) -> None:
        audit = sub.add_parser("audit", help="Audit product consistency")
        audit.add_argument("--strict", action="store_true")
        inner = audit.add_subparsers(dest="action", required=False)
        inner.add_parser("zones", help="Audit DNS zone governance")
        inner.add_parser("config", help="Audit DNSForge node configuration")
        inner.add_parser("catalog", help="Audit catalog zone publication")
        inner.add_parser("cluster", help="Audit authoritative HA cluster")
        zone = inner.add_parser("zone", help="Audit one DNS zone integrity")
        zone.add_argument("name")

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
        p.add_argument("--format", choices=["text", "json"], default="text")

    def _add_health(self, sub) -> None:
        p = sub.add_parser("health", help="Run local health checks")
        p.add_argument("--setup-file", default="/etc/dnsforge/setup.conf")
        inner = p.add_subparsers(dest="action", required=False)
        score = inner.add_parser("score")
        score.add_argument("--format", choices=["text", "json"], default="text")

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
        p.add_argument("--target-root", default="/")
        p.add_argument("--reason", default=None)
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
        render = inner.add_parser("render")
        render.add_argument("--setup-file", default=None)
        render.add_argument("--reason", required=True)
        render.add_argument("--dry-run", action="store_true")
        apply = inner.add_parser("apply")
        apply.add_argument("--setup-file", default=None)
        apply.add_argument("--reason", required=True)
        apply.add_argument("--dry-run", action="store_true")
        sync = inner.add_parser("sync")
        sync.add_argument("--setup-file", default=None)
        sync.add_argument("--reason", required=True)
        sync.add_argument("--dry-run", action="store_true")
        diff = inner.add_parser("diff")
        diff.add_argument("--setup-file", default=None)
        peers = inner.add_parser("peers")
        peers.add_argument("--setup-file", default=None)
        audit = inner.add_parser("audit")
        audit.add_argument("--setup-file", default=None)
        audit.add_argument("--format", choices=["text", "json"], default="text")

    def _add_catalog(self, sub) -> None:
        catalog = sub.add_parser("catalog", help="Manage BIND catalog zones")
        inner = catalog.add_subparsers(dest="action", required=True)
        status = inner.add_parser("status", help="Show catalog publication status")
        status.add_argument("--format", choices=["text", "json"], default="text")
        enable = inner.add_parser("enable", help="Enable catalog zone publication")
        enable.add_argument("--reason", required=True)
        disable = inner.add_parser("disable", help="Disable catalog zone publication")
        disable.add_argument("--reason", required=True)
        sync = inner.add_parser("sync", help="Synchronize active zones into the catalog zone")
        sync.add_argument("--reason", required=True)
        repair = inner.add_parser("repair", help="Repair catalog publications from active zones")
        repair.add_argument("--reason", required=True)
        list_parser = inner.add_parser("list", help="List published catalog members")
        list_parser.add_argument("--format", choices=["text", "json"], default="text")
        inner.add_parser("validate", help="Validate catalog state against active zones")

    def _add_config(self, sub) -> None:
        config = sub.add_parser("config", help="Manage DNSForge node configuration")
        config.add_argument("--setup-file", default=None)
        inner = config.add_subparsers(dest="action", required=True)
        inner.add_parser("show", help="Show node configuration")
        inner.add_parser("validate", help="Validate node configuration")
        diff = inner.add_parser("diff", help="Diff current setup.conf against history")
        diff.add_argument("--id", type=int)
        diff.add_argument("--id1", type=int)
        diff.add_argument("--id2", type=int)
        inner.add_parser("history", help="Show node configuration history")
        apply = inner.add_parser("apply", help="Render and deploy setup.conf changes")
        apply.add_argument("--reason", required=True)
        apply.add_argument("--dry-run", action="store_true")
        rollback = inner.add_parser("rollback", help="Rollback setup.conf to a history snapshot")
        rollback.add_argument("--id", type=int, required=True)
        rollback.add_argument("--reason", required=True)
        rollback.add_argument("--dry-run", action="store_true")

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
        dnssec = sub.add_parser("dnssec", help="Manage DNSSEC lifecycle")
        dnssec.add_argument("--setup-file", default="/etc/dnsforge/setup.conf")
        inner = dnssec.add_subparsers(dest="action", required=True)

        status = inner.add_parser("status")
        status.add_argument("--zone")

        validate = inner.add_parser("validate")
        validate.add_argument("--zone")

        for action in ("enable", "disable", "sign", "rotate-ksk", "rotate-zsk"):
            parser = inner.add_parser(action)
            parser.add_argument("--zone", required=True)
            parser.add_argument("--reason", required=True)

        policy = inner.add_parser("policy")
        policy_inner = policy.add_subparsers(dest="policy_action", required=True)
        policy_inner.add_parser("show")
        policy_apply = policy_inner.add_parser("apply")
        policy_apply.add_argument("--zsk-rotation-days", type=int, default=30)
        policy_apply.add_argument("--ksk-rotation-days", type=int, default=365)

        check = inner.add_parser("check-expiry")
        check.add_argument("--warn-days", type=int, default=30)

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
            return "proxy", resolved_node, settings.get("PROXY_TYPE", resolved_proxy_type or "hybrid")
        if role_value == DnsRole.AUTHORITATIVE.value:
            return "authoritative", resolved_node, resolved_proxy_type

        print(f"ERROR: unsupported ROLE in {paths.setup_file}: {role_value or '<missing>'}", file=sys.stderr)
        return None

    def dispatch(self, args: argparse.Namespace) -> int:
        paths = ProjectPaths(Path(args.project_root).resolve())

        if args.command == "version":
            print(__version__)
            return 0

        if args.command == "generate":
            if args.action == "commands-doc":
                output_path = Path(args.output)
                if not output_path.is_absolute():
                    output_path = paths.project_root / output_path
                parser = DnsForgeArgumentParserFactory().build()
                written = CommandDocumentationService().write(parser, output_path)
                print(written)
                return 0
            return 2

        if args.command == "job":
            service = JobService(paths)
            if args.action == "list":
                print(service.list())
                return 0
            if args.action == "show":
                print(service.show(args.job_id))
                return 0
            if args.action == "run":
                print(service.run(args.job_id, dry_run=args.dry_run))
                return 0
            if args.action == "cancel":
                print(service.cancel(args.job_id))
                return 0
            if args.action == "history":
                print(service.history())
                return 0
            return 2

        if args.command == "report":
            if args.action == "generate":
                output = Path(args.output) if getattr(args, "output", None) else None
                print(ReportService(paths).generate(output_format=args.format, output=output))
                return 0
            return 2

        if args.command == "drift":
            if args.action == "audit":
                ok, output = DriftService(paths).audit(target_root=Path(args.target_root))
                print(output)
                return 0 if ok else 1
            return 2

        if args.command == "events":
            event_log = (
                Path(args.event_log)
                if getattr(args, "event_log", None)
                else paths.settings_root / "audit" / "events.jsonl"
            )
            if args.action == "tail":
                print(EventTailService(event_log).tail(limit=args.limit, category=args.category))
                return 0
            return 2

        if args.command == "metrics":
            if args.action == "show":
                print(MetricsCollector(paths).render_text())
                return 0
            return 2

        if args.command == "sync":
            if args.action == "providers":
                print(SyncProviderService().providers_status())
                return 0
            return 2

        if args.command == "validate":
            resolved = self._resolve_role_from_setup(
                paths, args.role, getattr(args, "node", None), getattr(args, "proxy_type", None)
            )
            if resolved is None:
                return 2
            role, node, proxy_type = resolved
            if role == "proxy":
                ValidateProxy(paths).execute(node, ProxyType.from_value(proxy_type or "hybrid"))
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
                RenderProxy(paths).execute(node, ProxyType.from_value(proxy_type or "hybrid"))
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

        if args.command == "initialize":
            if getattr(args, "render_only", False) and getattr(args, "apply", False):
                print("ERROR: --render-only and --apply are mutually exclusive", file=sys.stderr)
                return 2
            InitializeCommand(paths).execute(
                render_only=args.render_only,
                dry_run=args.dry_run,
                apply_only=args.apply,
            )
            return 0

        if args.command == "zone":
            manager = ZoneManager(paths)
            if args.action == "list":
                zones = manager.list(enabled_only=args.enabled)
                if getattr(args, "format", "text") == "json":
                    print(
                        json.dumps(
                            [
                                {
                                    "name": zone.name,
                                    "type": zone.zone_type.value,
                                    "enabled": zone.enabled,
                                    "lifecycle": zone.lifecycle.value,
                                    "business_owner": zone.business_owner,
                                    "technical_owner": zone.technical_owner,
                                }
                                for zone in zones
                            ],
                            indent=2,
                            sort_keys=True,
                        )
                    )
                    return 0
                for zone in zones:
                    print(
                        f"{zone.name}\t{zone.zone_type.value}\t{'enabled' if zone.enabled else 'disabled'}\t{zone.lifecycle.value}\t{zone.business_owner or '-'}\t{zone.technical_owner or '-'}"
                    )
                return 0
            if args.action == "get":
                zone = manager.get(args.name)
                print(f"name={zone.name}")
                print(f"type={zone.zone_type.value}")
                print(f"enabled={'yes' if zone.enabled else 'no'}")
                print(f"views={','.join(zone.views)}")
                print(f"lifecycle={zone.lifecycle.value}")
                print(f"business_owner={zone.business_owner}")
                print(f"technical_owner={zone.technical_owner}")
                print(f"environment={zone.environment}")
                print(f"classification={zone.classification}")
                print(f"description={zone.description}")
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
            if args.action == "status":
                print(manager.status(args.name))
                return 0
            if args.action == "backup":
                print(manager.backup(args.name, args.reason))
                return 0
            if args.action == "diff":
                print(manager.history_diff(args.zone_name, args.from_version, args.to_version))
                return 0
            if args.action == "rollback":
                print(manager.rollback(args.zone_name, int(args.version), args.reason))
                return 0
            if args.action == "search":
                if args.zone_name or args.record_name or args.record_type or args.value:
                    if not args.zone_name:
                        print("ERROR: record search requires --zone", file=sys.stderr)
                        return 2
                    for record in manager.search_records(
                        args.zone_name,
                        record_name=args.record_name,
                        record_type=args.record_type,
                        value=args.value,
                    ):
                        print(record.to_bind_line())
                    return 0
                for zone in manager.search_zones(
                    owner=args.owner,
                    view=args.view,
                    state=args.state,
                    environment=args.environment,
                    classification=args.classification,
                ):
                    print(
                        f"{zone.name}	{zone.zone_type.value}	{zone.lifecycle.value}	"
                        f"{zone.business_owner or '-'}	{zone.technical_owner or '-'}"
                    )
                return 0
            if args.action == "create":
                zone_name = getattr(args, "zone_name", None) or getattr(args, "name", None)
                if not zone_name:
                    print("ERROR: zone create requires a zone name", file=sys.stderr)
                    return 2
                views = [i.strip() for i in args.views.replace(";", ",").split(",") if i.strip()]
                manager = ZoneManager(paths, profile=ServerProfile.from_value(args.profile))
                manager.create(
                    zone_name,
                    args.zone_type,
                    views,
                    cluster=args.cluster,
                    enabled=not args.disabled,
                    description=args.description,
                    business_owner=args.business_owner,
                    technical_owner=args.technical_owner,
                    environment=args.environment,
                    classification=args.classification,
                    lifecycle=args.state,
                    reason=args.reason,
                )
                return 0
            if args.action == "edit":
                ops = [args.add_record, args.update_record, args.delete_record]
                if sum(1 for item in ops if item) != 1:
                    print("ERROR: zone edit requires exactly one of --add, --update or --delete", file=sys.stderr)
                    return 2
                if args.add_record:
                    manager.add_record(args.name, args.add_record, ttl=args.ttl, reason=args.reason)
                if args.update_record:
                    manager.update_record(args.name, args.update_record, ttl=args.ttl, reason=args.reason)
                if args.delete_record:
                    manager.delete_record(args.name, args.delete_record, reason=args.reason)
                return 0
            if args.action == "disable":
                zone_name = getattr(args, "zone_name", None) or getattr(args, "name", None)
                if not zone_name:
                    print("ERROR: zone disable requires a zone name", file=sys.stderr)
                    return 2
                manager.disable(zone_name, args.reason)
                return 0
            if args.action == "enable":
                zone_name = getattr(args, "zone_name", None) or getattr(args, "name", None)
                if not zone_name:
                    print("ERROR: zone enable requires a zone name", file=sys.stderr)
                    return 2
                manager.enable(zone_name, args.reason)
                return 0
            if args.action == "retire":
                zone_name = getattr(args, "zone_name", None) or getattr(args, "name", None)
                if not zone_name:
                    print("ERROR: zone retire requires a zone name", file=sys.stderr)
                    return 2
                manager.retire(zone_name, args.reason)
                return 0
            if args.action == "delete":
                zone_name = getattr(args, "zone_name", None) or getattr(args, "name", None)
                if not zone_name:
                    print("ERROR: zone delete requires a zone name", file=sys.stderr)
                    return 2
                manager.delete(zone_name, args.reason)
                return 0
            return 2

        if args.command == "audit":
            if getattr(args, "action", None) == "zones":
                ok, output = ZoneManager(paths).audit_zones()
                print(output)
                return 0 if ok else 1
            if getattr(args, "action", None) == "config":
                ok, output = ConfigService(paths).audit()
                print(output)
                return 0 if ok else 1
            if getattr(args, "action", None) == "catalog":
                ok, output = CatalogService(paths).audit()
                print(output)
                return 0 if ok else 1
            if getattr(args, "action", None) == "cluster":
                ok, output = ClusterService().audit(paths.setup_file)
                print(output)
                return 0 if ok else 1
            if getattr(args, "action", None) == "zone":
                ok, output = ZoneManager(paths).audit_zone(args.name)
                print(output)
                return 0 if ok else 1
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
            output = StatusService().show(Path(args.setup_file))
            if getattr(args, "format", "text") == "json":
                data = {}
                for line in output.splitlines():
                    if ":" in line:
                        key, value = line.split(":", 1)
                        data[key.strip().lower().replace(" ", "_")] = value.strip()
                print(json.dumps(data, indent=2, sort_keys=True))
            else:
                print(output)
            return 0

        if args.command == "health":
            if getattr(args, "action", None) == "score":
                print(HealthScoreService().render(paths, output_format=args.format))
                return 0
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
            result = MigrationService(paths).migrate(
                Path(args.setup_file),
                MigrationTarget.from_value(args.target),
                dry_run=args.dry_run,
                reason=args.reason,
                target_root=Path(args.target_root),
            )
            print(result)
            return 0

        if args.command == "disaster":
            service = DisasterRecoveryService(paths)
            if args.action == "snapshot":
                print(service.snapshot(args.reason, target_root=Path(args.target_root)))
                return 0
            if args.action == "restore":
                print(service.restore(Path(args.snapshot), target_root=Path(args.target_root), dry_run=args.dry_run))
                return 0
            if args.action == "verify":
                print(service.verify(Path(args.snapshot)))
                return 0
            return 2

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
            if args.action == "render":
                print(service.render(setup_file, args.reason, dry_run=args.dry_run))
                return 0
            if args.action == "apply":
                print(service.apply(setup_file, args.reason, dry_run=args.dry_run))
                return 0
            if args.action == "sync":
                print(service.sync(setup_file, args.reason, dry_run=args.dry_run))
                return 0
            if args.action == "diff":
                print(service.diff(setup_file))
                return 0
            if args.action == "peers":
                print(service.peers(setup_file))
                return 0
            if args.action == "audit":
                ok, output = service.audit(setup_file, output_format=args.format)
                print(output)
                return 0 if ok else 1
            return 2

        if args.command == "catalog":
            service = CatalogService(paths)
            if args.action == "status":
                output = service.status()
                if getattr(args, "format", "text") == "json":
                    data = {}
                    for line in output.splitlines():
                        if ":" in line:
                            key, value = line.split(":", 1)
                            data[key.strip().lower().replace(" ", "_")] = value.strip()
                    print(json.dumps(data, indent=2, sort_keys=True))
                else:
                    print(output)
                return 0
            if args.action == "enable":
                print(service.enable(args.reason))
                return 0
            if args.action == "disable":
                print(service.disable(args.reason))
                return 0
            if args.action == "sync":
                print(service.sync(args.reason))
                return 0
            if args.action == "repair":
                print(service.repair(args.reason))
                return 0
            if args.action == "list":
                output = service.list_published()
                if getattr(args, "format", "text") == "json":
                    rows = []
                    for line in output.splitlines()[1:]:
                        parts = line.split("\t")
                        if len(parts) == 4:
                            rows.append(
                                {"zone": parts[0], "type": parts[1], "views": parts[2].split(","), "member": parts[3]}
                            )
                    print(json.dumps(rows, indent=2, sort_keys=True))
                else:
                    print(output)
                return 0
            if args.action == "validate":
                print(service.validate())
                return 0
            return 2

        if args.command == "config":
            config_paths = paths
            if getattr(args, "setup_file", None):
                import os

                os.environ["DNSFORGE_SETUP_FILE"] = args.setup_file
                config_paths = ProjectPaths(paths.project_root)
            service = ConfigService(config_paths)
            if args.action == "show":
                print(service.show())
                return 0
            if args.action == "validate":
                print(service.validate())
                return 0
            if args.action == "diff":
                print(service.diff(identifier=args.id, id1=args.id1, id2=args.id2))
                return 0
            if args.action == "history":
                print(service.history())
                return 0
            if args.action == "apply":
                print(service.apply(args.reason, dry_run=args.dry_run))
                return 0
            if args.action == "rollback":
                print(service.rollback(args.id, args.reason, dry_run=args.dry_run))
                return 0
            return 2

        if args.command == "acl":
            service = AclService(Path(args.state_file))
            if args.action == "list":
                print(service.list_published())
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
                print(service.list_published())
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
            if args.action == "policy":
                policy = DnssecPolicyService(setup_file.parent / "dnssec-policy.json")
                if args.policy_action == "show":
                    print(policy.show())
                    return 0
                if args.policy_action == "apply":
                    print(
                        policy.apply(
                            zsk_rotation_days=args.zsk_rotation_days,
                            ksk_rotation_days=args.ksk_rotation_days,
                        )
                    )
                    return 0
                return 2
            if args.action == "status":
                print(service.status(setup_file, getattr(args, "zone", None)))
                return 0
            if args.action == "validate":
                print(service.validate(setup_file, getattr(args, "zone", None)))
                return 0
            if args.action == "enable":
                print(service.enable(setup_file, args.zone, args.reason))
                return 0
            if args.action == "disable":
                print(service.disable(setup_file, args.zone, args.reason))
                return 0
            if args.action == "sign":
                print(service.sign(setup_file, args.zone, args.reason))
                return 0
            if args.action == "rotate-ksk":
                print(service.rotate_ksk(setup_file, args.zone, args.reason))
                return 0
            if args.action == "rotate-zsk":
                print(service.rotate_zsk(setup_file, args.zone, args.reason))
                return 0
            if args.action == "check-expiry":
                print(service.check_expiry(setup_file, args.warn_days))
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
        normalized_argv = self._normalize_argv(list(sys.argv[1:] if argv is None else argv))
        args = parser.parse_args(normalized_argv)
        try:
            if self._requires_root(args):
                self.privilege_guard.require_root()
            return self.dispatcher.dispatch(args)
        except DnsForgeError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1

    def _requires_root(self, args: argparse.Namespace) -> bool:
        return getattr(args, "command", None) != "version"

    def _normalize_argv(self, argv: list[str]) -> list[str]:
        return argv
