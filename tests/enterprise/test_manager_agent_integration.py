from __future__ import annotations

from dnsforge_manager.application.core.manager_application import ManagerApplication
from dnsforge_manager.infrastructure.dnssync.client import RecordingDNSForgeNodeClient


def _register_approved_cluster_node(app: ManagerApplication, node_id: str) -> None:
    app.register_node(
        {
            "node_id": node_id,
            "name": node_id,
            "api_endpoint": f"https://{node_id}.example.test:1073",
            "role": "authoritative",
            "cluster_id": "cluster-a",
        },
        actor="admin",
        role="admin",
    )
    app.approve_node(node_id, actor="admin", role="admin")
    app.set_node_status(node_id, "active", actor="operator", role="operator")


def test_manager_dnssync_flows_to_dnsforge_agent_client_only() -> None:
    client = RecordingDNSForgeNodeClient()
    app = ManagerApplication(node_client=client)
    _register_approved_cluster_node(app, "dns01")
    _register_approved_cluster_node(app, "dns02")

    payload = {
        "cluster_id": "cluster-a",
        "operation": "zone.create",
        "payload": {"zone": "example.test"},
    }
    dry_run = app.dry_run_dnssync(payload, actor="operator", role="operator")["execution"]
    app.apply_dnssync(
        {**payload, "approved_plan_hash": dry_run["plan_hash"]},
        actor="admin",
        role="admin",
    )

    assert [(node_id, operation.operation) for node_id, operation in client.operations] == [
        ("dns01", "zone.create"),
        ("dns02", "zone.create"),
    ]


def test_manager_dnssync_apply_requires_approved_dry_run_hash() -> None:
    app = ManagerApplication(node_client=RecordingDNSForgeNodeClient())
    _register_approved_cluster_node(app, "dns01")

    payload = {
        "cluster_id": "cluster-a",
        "operation": "zone.delete",
        "payload": {"zone": "example.test"},
    }

    try:
        app.apply_dnssync({**payload, "approved_plan_hash": "tampered"}, actor="admin", role="admin")
    except PermissionError as exc:
        assert "approved dry-run plan hash" in str(exc)
    else:  # pragma: no cover - defensive assertion path
        raise AssertionError("apply without approved dry-run hash must fail")
