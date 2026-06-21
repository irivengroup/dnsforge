from __future__ import annotations

from dnsforge_manager.application.core.manager_application import ManagerApplication
from dnsforge_manager.domain.dnssync.models import DNSForgeOperation, SyncMode
from dnsforge_manager.infrastructure.dnssync.repository import DNSSyncRepository
from dnsforge_manager.interfaces.api.fastapi_app import create_fastapi_app
from dnsforge_manager.interfaces.cli.main import build_parser


def _approved_cluster_app() -> ManagerApplication:
    app = ManagerApplication()
    for node_id in ("dns01", "dns02"):
        app.register_node(
            {
                "node_id": node_id,
                "name": node_id,
                "api_endpoint": f"https://{node_id}:1073",
                "role": "authoritative",
                "cluster_id": "cluster-a",
            }
        )
        app.approve_node(node_id)
        app.set_node_status(node_id, "active")
    return app


def test_dnssync_history_tracks_dry_run_apply_and_cluster_filter() -> None:
    app = _approved_cluster_app()
    payload = {"cluster_id": "cluster-a", "operation": "zone.create", "payload": {"zone": "example.com"}}
    dry_run = app.dry_run_dnssync(payload)["execution"]
    app.apply_dnssync({**payload, "approved_plan_hash": dry_run["plan_hash"]})

    history = app.dnssync_history("cluster-a")
    assert [event["mode"] for event in history["executions"]] == ["dry-run", "apply"]
    assert app.dnssync_history("other-cluster")["executions"] == []


def test_dnssync_repository_keeps_plans_and_executions_ordered() -> None:
    app = _approved_cluster_app()
    operation = DNSForgeOperation(operation="catalog.sync", payload={"scope": "cluster"})
    plan = app.dnssync_service.build_cluster_plan(
        cluster_id="cluster-a",
        operation=operation,
        nodes=app.registration_service.list_nodes(),
        mode=SyncMode.DRY_RUN,
    )
    execution = app.dnssync_service.dry_run(plan)
    repository = DNSSyncRepository()
    repository.save_plan(plan)
    repository.save_execution(execution)

    assert repository.get_plan(plan.plan_hash) == plan
    assert repository.list_plans() == (plan,)
    assert repository.list_executions(cluster_id="cluster-a") == (execution,)


def test_dnssync_history_is_exposed_in_cli_and_api_contracts() -> None:
    parser = build_parser()
    parsed = parser.parse_args(["dnssync", "history", "--cluster-id", "cluster-a"])
    assert parsed.command == "dnssync"
    assert parsed.dnssync_action == "history"
    assert parsed.cluster_id == "cluster-a"

    api = create_fastapi_app()
    paths = {getattr(route, "path", "") for route in getattr(api, "routes", [])}
    assert "/dnssync/history" in paths

class _NoReadinessClient:
    def submit(self, node_id, operation):  # type: ignore[no-untyped-def]
        from dnsforge_manager.domain.dnssync.models import DNSForgeOperationResult

        return DNSForgeOperationResult(node_id=node_id, accepted=True, message=operation.operation)


def test_manager_dnssync_plan_validation_and_status_are_repository_backed() -> None:
    app = _approved_cluster_app()
    payload = {"cluster_id": "cluster-a", "operation": "zone.update", "payload": {"zone": "example.com"}}

    created = app.create_dnssync_plan(payload)
    plan_hash = created["plan"]["plan_hash"]

    assert app.dnssync_plans()["plans"][0]["plan_hash"] == plan_hash
    assert app.validate_dnssync_plan({"plan_hash": plan_hash}) == {"valid": True, "plan_hash": plan_hash}
    assert app.validate_dnssync_plan({"plan_hash": "missing"}) == {"valid": False, "plan_hash": "missing"}
    assert app.validate_dnssync_plan(payload)["valid"] is True
    assert app.dnssync_status()["plans"][0]["cluster_id"] == "cluster-a"


def test_manager_nodes_and_readiness_fallback_are_exposed() -> None:
    app = _approved_cluster_app()
    app.node_client = _NoReadinessClient()

    assert len(app.nodes()["nodes"]) == 2
    readiness = app.node_readiness("dns01")["readiness"]
    assert readiness["status"] == "WARNING"
    assert readiness["checks"][0]["critical"] is False


def test_manager_inventory_status_and_compliance_updates_are_audited() -> None:
    app = ManagerApplication()
    status = app.update_inventory_agent_status(
        {
            "fingerprint": "fp01",
            "hostname": "dns01",
            "version": "15.1.0",
            "profile": "authoritative",
            "site": "dc1",
            "cluster": "cluster-a",
            "readiness": "READY",
            "checks": [],
        }
    )["agent_status"]
    compliance = app.update_inventory_agent_compliance(
        {
            "fingerprint": "fp01",
            "compliance": "COMPLIANT",
            "drift_count": 0,
            "last_checked": "2026-06-21T00:00:00Z",
            "message": "ok",
            "findings": [],
        }
    )["agent_compliance"]

    assert status["readiness"] == "READY"
    assert compliance["compliance"] == "COMPLIANT"
    assert app.inventory_agent_compliance()["summary"]["COMPLIANT"] == 1
