from __future__ import annotations

import argparse
import json

from dnsforge_manager import __version__
from dnsforge_manager.application.core.manager_application import create_app


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dnsforge-manager", description="DNSForge Manager foundation")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("version", help="Show DNSForge Manager version")
    sub.add_parser("health", help="Show DNSForge Manager foundation health")
    sub.add_parser("boundaries", help="Show product responsibility boundaries")
    nodes = sub.add_parser("nodes", help="List managed DNSForge nodes")
    nodes.add_argument("--format", choices=("json",), default="json")

    inventory = sub.add_parser("inventory", help="Manage Manager Central Inventory")
    inventory_sub = inventory.add_subparsers(dest="inventory_object", required=True)

    _add_inventory_resource(inventory_sub, "site", "site_id")
    _add_inventory_resource(inventory_sub, "cluster", "cluster_id")

    agent = inventory_sub.add_parser("agent", help="Manage inventory agents")
    agent_sub = agent.add_subparsers(dest="inventory_action", required=True)
    agent_sub.add_parser("list", help="List registered agents")
    register = agent_sub.add_parser("register", help="Register an agent")
    register.add_argument("--fingerprint", required=True)
    register.add_argument("--hostname", required=True)
    register.add_argument("--version", required=True)
    register.add_argument("--profile", required=True)
    register.add_argument(
        "--role",
        choices=(
            "authoritative",
            "proxy-forwarder",
            "proxy-hybrid",
            "catalog-publisher",
            "catalog-subscriber",
            "hidden-master",
            "stealth-secondary",
        ),
    )
    register.add_argument("--site", default="default")
    register.add_argument("--cluster")
    register.add_argument("--status", choices=("READY", "WARNING", "FAILED"), default="WARNING")

    environment = inventory_sub.add_parser("environment", help="List inventory environments")
    environment_sub = environment.add_subparsers(dest="inventory_action", required=True)
    environment_sub.add_parser("list", help="List environments")

    role = inventory_sub.add_parser("role", help="List canonical DNSForge agent roles")
    role_sub = role.add_subparsers(dest="inventory_action", required=True)
    role_sub.add_parser("list", help="List canonical agent roles")

    compliance = inventory_sub.add_parser("compliance", help="Manage inventory agent compliance")
    compliance_sub = compliance.add_subparsers(dest="inventory_action", required=True)
    compliance_sub.add_parser("list", help="List agent compliance states")
    history_compliance = compliance_sub.add_parser("history", help="List agent compliance history")
    history_compliance.add_argument("--fingerprint")
    trends_compliance = compliance_sub.add_parser("trends", help="Summarize agent compliance history trends")
    trends_compliance.add_argument("--fingerprint")
    report_compliance = compliance_sub.add_parser("report", help="Build an agent compliance risk report")
    report_compliance.add_argument("--fingerprint")
    update_compliance = compliance_sub.add_parser("update", help="Update one agent compliance state")
    update_compliance.add_argument("--fingerprint", required=True)
    update_compliance.add_argument(
        "--compliance",
        choices=("COMPLIANT", "WARNING", "DRIFTED", "FAILED"),
        required=True,
    )
    update_compliance.add_argument("--drift-count", type=int, default=0)
    update_compliance.add_argument("--last-checked", default="")
    update_compliance.add_argument("--message", default="")

    monitor = sub.add_parser("monitor", help="Monitor DNSForge-managed BIND fleet with DNSBeat")
    monitor_sub = monitor.add_subparsers(dest="monitor_action", required=True)
    monitor_sub.add_parser("status", help="Show DNSBeat fleet status")
    monitor_sub.add_parser("agents", help="Show DNSBeat agent health")
    monitor_sub.add_parser("clusters", help="Show DNSBeat cluster health")
    monitor_sub.add_parser("alerts", help="Show DNSBeat alerts")

    agent = sub.add_parser("agent", help="Execute DNSForge Agent API commands securely")
    agent_sub = agent.add_subparsers(dest="agent_action", required=True)
    execute = agent_sub.add_parser("execute", help="Execute one command on one DNSForge agent")
    execute.add_argument("--node-id", required=True)
    execute.add_argument("--action", required=True)
    execute.add_argument("--operation", required=True)
    execute.add_argument("--payload", default="{}")
    execute.add_argument("--request-id")
    execute.add_argument("--idempotency-key")
    execute_cluster = agent_sub.add_parser(
        "execute-cluster", help="Execute one command on all eligible agents in a cluster"
    )
    execute_cluster.add_argument("--cluster-id", required=True)
    execute_cluster.add_argument("--action", required=True)
    execute_cluster.add_argument("--operation", required=True)
    execute_cluster.add_argument("--payload", default="{}")
    execute_cluster.add_argument("--request-id")
    execute_cluster.add_argument("--idempotency-key")

    dnssync = sub.add_parser("dnssync", help="Orchestrate DNSSync through DNSForge agents")
    dnssync_sub = dnssync.add_subparsers(dest="dnssync_action", required=True)
    dnssync_sub.add_parser("plans", help="List DNSSync plans")
    plan = dnssync_sub.add_parser("plan", help="Create a DNSSync plan")
    _add_dnssync_operation_arguments(plan)
    validate = dnssync_sub.add_parser("validate", help="Validate a DNSSync plan or payload")
    validate.add_argument("--plan-hash")
    _add_dnssync_operation_arguments(validate, required=False)
    dry_run = dnssync_sub.add_parser("dry-run", help="Dry-run a DNSSync operation")
    _add_dnssync_operation_arguments(dry_run)
    apply = dnssync_sub.add_parser("apply", help="Apply a DNSSync operation")
    _add_dnssync_operation_arguments(apply)
    apply.add_argument("--approved-plan-hash", required=True)
    rollback = dnssync_sub.add_parser("rollback", help="Rollback a DNSSync operation")
    _add_dnssync_operation_arguments(rollback)
    rollback.add_argument("--approved-plan-hash", required=True)
    dnssync_sub.add_parser("status", help="Show DNSSync orchestration status")

    trust = sub.add_parser("trust", help="Manage DNSForge agent trust")
    trust_sub = trust.add_subparsers(dest="trust_action", required=True)
    trust_sub.add_parser("list", help="List trusted agents")
    trust_sub.add_parser("enrollments", help="List enrollment requests")
    enroll = trust_sub.add_parser("enroll", help="Create an agent enrollment request")
    enroll.add_argument("--hostname", required=True)
    enroll.add_argument("--version", required=True)
    enroll.add_argument("--profile", required=True)
    enroll.add_argument("--public-key", default="")
    enroll.add_argument("--fingerprint")
    enroll.add_argument("--site", default="default")
    enroll.add_argument("--cluster")
    approve = trust_sub.add_parser("approve", help="Approve an agent enrollment request")
    approve.add_argument("--request-id", required=True)
    revoke = trust_sub.add_parser("revoke", help="Revoke a trusted agent")
    revoke.add_argument("--fingerprint", required=True)
    rotate = trust_sub.add_parser("rotate-token", help="Rotate a trusted agent token")
    rotate.add_argument("--fingerprint", required=True)
    rotate.add_argument("--reason", default="operator-request")
    rotate_certificate = trust_sub.add_parser("rotate-certificate", help="Rotate a trusted agent certificate")
    rotate_certificate.add_argument("--fingerprint", required=True)
    rotate_certificate.add_argument("--public-key")
    rotate_certificate.add_argument("--reason", default="certificate-rotation")
    trust_sub.add_parser("policies", help="List trust policies")
    policy = trust_sub.add_parser("create-policy", help="Create a trust policy")
    policy.add_argument("--policy-id", required=True)
    policy.add_argument("--name")
    policy.add_argument("--allowed-profile", action="append", default=[])
    policy.add_argument("--allowed-site", action="append", default=[])
    policy.add_argument("--require-public-key", action="store_true", default=False)
    policy.add_argument("--auto-approve", action="store_true", default=False)
    policy.add_argument("--max-token-age-days", type=int, default=90)
    policy.add_argument("--certificate-rotation-days", type=int, default=180)
    rotations = trust_sub.add_parser("rotations", help="List trust rotation history")
    rotations.add_argument("--fingerprint")
    return parser


def _add_dnssync_operation_arguments(parser: argparse.ArgumentParser, *, required: bool = True) -> None:
    parser.add_argument("--cluster-id", required=required)
    parser.add_argument("--operation", required=required)
    parser.add_argument("--payload", default="{}", help="JSON object payload submitted to DNSForge agents")


def _dnssync_payload(args: argparse.Namespace, *, mode: str | None = None) -> dict[str, object]:
    payload: dict[str, object] = {}
    if getattr(args, "cluster_id", None):
        payload["cluster_id"] = args.cluster_id
    if getattr(args, "operation", None):
        payload["operation"] = args.operation
    if getattr(args, "payload", None):
        parsed = json.loads(args.payload)
        if not isinstance(parsed, dict):
            raise ValueError("--payload must be a JSON object")
        payload["payload"] = parsed
    if mode is not None:
        payload["mode"] = mode
    if getattr(args, "plan_hash", None):
        payload["plan_hash"] = args.plan_hash
    if getattr(args, "approved_plan_hash", None):
        payload["approved_plan_hash"] = args.approved_plan_hash
    return payload


def _add_inventory_resource(subparsers: argparse._SubParsersAction, name: str, id_name: str) -> None:
    resource = subparsers.add_parser(name, help=f"Manage inventory {name}s")
    resource_sub = resource.add_subparsers(dest="inventory_action", required=True)
    resource_sub.add_parser("list", help=f"List {name}s")
    create = resource_sub.add_parser("create", help=f"Create a {name}")
    create.add_argument(f"--{id_name.replace('_', '-')}", dest=id_name, required=True)
    create.add_argument("--name")
    create.add_argument("--description", default="")
    create.add_argument("--site", default="default")
    create.add_argument("--environment", default="production")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "version":
        print(__version__)
        return 0
    app = create_app()
    if args.command == "health":
        print(json.dumps(app.health(), sort_keys=True))
        return 0
    if args.command == "boundaries":
        print(json.dumps(app.boundaries(), sort_keys=True))
        return 0
    if args.command == "nodes":
        print(json.dumps(app.nodes(), sort_keys=True))
        return 0
    if args.command == "inventory":
        print(json.dumps(_dispatch_inventory(app, args), sort_keys=True))
        return 0
    if args.command == "dnssync":
        print(json.dumps(_dispatch_dnssync(app, args), sort_keys=True))
        return 0
    if args.command == "monitor":
        print(json.dumps(_dispatch_monitor(app, args), sort_keys=True))
        return 0
    if args.command == "agent":
        print(json.dumps(_dispatch_agent(app, args), sort_keys=True))
        return 0
    if args.command == "trust":
        print(json.dumps(_dispatch_trust(app, args), sort_keys=True))
        return 0
    return 2


def _dispatch_inventory(app: object, args: argparse.Namespace) -> dict[str, object]:
    if args.inventory_object == "site":
        if args.inventory_action == "list":
            return app.inventory_sites()  # type: ignore[attr-defined]
        return app.create_inventory_site(  # type: ignore[attr-defined]
            {"site_id": args.site_id, "name": args.name or args.site_id, "description": args.description}
        )
    if args.inventory_object == "cluster":
        if args.inventory_action == "list":
            return app.inventory_clusters()  # type: ignore[attr-defined]
        return app.create_inventory_cluster(  # type: ignore[attr-defined]
            {
                "cluster_id": args.cluster_id,
                "name": args.name or args.cluster_id,
                "site": args.site,
                "environment": args.environment,
                "description": args.description,
            }
        )
    if args.inventory_object == "agent":
        if args.inventory_action == "list":
            return app.inventory_agents()  # type: ignore[attr-defined]
        return app.register_inventory_agent(  # type: ignore[attr-defined]
            {
                "fingerprint": args.fingerprint,
                "hostname": args.hostname,
                "version": args.version,
                "profile": args.profile,
                "role": args.role or args.profile,
                "site": args.site,
                "cluster": args.cluster,
                "status": args.status,
            }
        )
    if args.inventory_object == "environment":
        return app.inventory_environments()  # type: ignore[attr-defined]
    if args.inventory_object == "role":
        return app.inventory_roles()  # type: ignore[attr-defined]
    if args.inventory_object == "compliance":
        if args.inventory_action == "list":
            return app.inventory_agent_compliance()  # type: ignore[attr-defined]
        if args.inventory_action == "history":
            return app.inventory_agent_compliance_history(args.fingerprint)  # type: ignore[attr-defined]
        if args.inventory_action == "trends":
            return app.inventory_agent_compliance_trends(args.fingerprint)  # type: ignore[attr-defined]
        if args.inventory_action == "report":
            return app.inventory_agent_compliance_report(args.fingerprint)  # type: ignore[attr-defined]
        return app.update_inventory_agent_compliance(  # type: ignore[attr-defined]
            {
                "fingerprint": args.fingerprint,
                "compliance": args.compliance,
                "drift_count": args.drift_count,
                "last_checked": args.last_checked,
                "message": args.message,
            }
        )
    raise ValueError(f"unsupported inventory command: {args.inventory_object}")


def _dispatch_monitor(app: object, args: argparse.Namespace) -> dict[str, object]:
    if args.monitor_action == "status":
        return app.monitor_status()  # type: ignore[attr-defined]
    if args.monitor_action == "agents":
        return app.monitor_agents()  # type: ignore[attr-defined]
    if args.monitor_action == "clusters":
        return app.monitor_clusters()  # type: ignore[attr-defined]
    if args.monitor_action == "alerts":
        return app.monitor_alerts()  # type: ignore[attr-defined]
    raise ValueError(f"unsupported monitor command: {args.monitor_action}")


def _dispatch_dnssync(app: object, args: argparse.Namespace) -> dict[str, object]:
    if args.dnssync_action == "plans":
        return app.dnssync_plans()  # type: ignore[attr-defined]
    if args.dnssync_action == "plan":
        return app.create_dnssync_plan(_dnssync_payload(args, mode="dry-run"))  # type: ignore[attr-defined]
    if args.dnssync_action == "validate":
        return app.validate_dnssync_plan(_dnssync_payload(args))  # type: ignore[attr-defined]
    if args.dnssync_action == "dry-run":
        return app.dry_run_dnssync(_dnssync_payload(args))  # type: ignore[attr-defined]
    if args.dnssync_action == "apply":
        return app.apply_dnssync(_dnssync_payload(args))  # type: ignore[attr-defined]
    if args.dnssync_action == "rollback":
        return app.rollback_dnssync(_dnssync_payload(args))  # type: ignore[attr-defined]
    if args.dnssync_action == "status":
        return app.dnssync_status()  # type: ignore[attr-defined]
    raise ValueError(f"unsupported dnssync command: {args.dnssync_action}")


def _dispatch_trust(app: object, args: argparse.Namespace) -> dict[str, object]:
    if args.trust_action == "list":
        return app.trusted_agents()  # type: ignore[attr-defined]
    if args.trust_action == "enrollments":
        return app.trust_enrollments()  # type: ignore[attr-defined]
    if args.trust_action == "enroll":
        return app.enroll_agent(  # type: ignore[attr-defined]
            {
                "hostname": args.hostname,
                "version": args.version,
                "profile": args.profile,
                "public_key": args.public_key,
                "fingerprint": args.fingerprint,
                "site": args.site,
                "cluster": args.cluster,
            }
        )
    if args.trust_action == "approve":
        return app.approve_agent_enrollment(args.request_id)  # type: ignore[attr-defined]
    if args.trust_action == "revoke":
        return app.revoke_trusted_agent(args.fingerprint)  # type: ignore[attr-defined]
    if args.trust_action == "rotate-token":
        return app.rotate_trusted_agent_token(args.fingerprint, reason=args.reason)  # type: ignore[attr-defined]
    if args.trust_action == "rotate-certificate":
        return app.rotate_trusted_agent_certificate(  # type: ignore[attr-defined]
            args.fingerprint,
            public_key=args.public_key,
            reason=args.reason,
        )
    if args.trust_action == "policies":
        return app.trust_policies()  # type: ignore[attr-defined]
    if args.trust_action == "create-policy":
        return app.create_trust_policy(  # type: ignore[attr-defined]
            {
                "policy_id": args.policy_id,
                "name": args.name or args.policy_id,
                "allowed_profiles": args.allowed_profile,
                "allowed_sites": args.allowed_site,
                "require_public_key": args.require_public_key,
                "auto_approve": args.auto_approve,
                "max_token_age_days": args.max_token_age_days,
                "certificate_rotation_days": args.certificate_rotation_days,
            }
        )
    if args.trust_action == "rotations":
        return app.trust_rotations(args.fingerprint)  # type: ignore[attr-defined]
    raise ValueError(f"unsupported trust command: {args.trust_action}")


def _agent_payload(args: argparse.Namespace) -> dict[str, object]:
    parsed = json.loads(args.payload)
    if not isinstance(parsed, dict):
        raise ValueError("--payload must be a JSON object")
    payload: dict[str, object] = {
        "action": args.action,
        "operation": args.operation,
        "payload": parsed,
    }
    if args.request_id:
        payload["request_id"] = args.request_id
    if args.idempotency_key:
        payload["idempotency_key"] = args.idempotency_key
    return payload


def _dispatch_agent(app: object, args: argparse.Namespace) -> dict[str, object]:
    if args.agent_action == "execute":
        return app.agent_execute(args.node_id, _agent_payload(args))  # type: ignore[attr-defined]
    if args.agent_action == "execute-cluster":
        return app.agent_execute_cluster(args.cluster_id, _agent_payload(args))  # type: ignore[attr-defined]
    raise ValueError(f"unsupported agent action: {args.agent_action}")


if __name__ == "__main__":
    raise SystemExit(main())
