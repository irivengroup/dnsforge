from __future__ import annotations

from pathlib import Path

from dnsforge_manager.application.core.manager_application import create_app
from dnsforge_manager.application.inventory.node_registration_service import NodeRegistrationService
from dnsforge_manager.domain.inventory import ManagedNode, NodeRole, NodeStatus
from dnsforge_manager.domain.rbac import MANAGER_ADMIN_ROLE, MANAGER_OPERATOR_ROLE, MANAGER_VIEWER_ROLE
from dnsforge_manager.infrastructure.inventory import JsonNodeInventoryRepository
from dnsforge_manager.interfaces.api.fastapi_app import create_fastapi_app


def test_manager_api_registers_and_reads_node() -> None:
    app = create_app()
    response = app.register_node(
        {
            "node_id": "dns01",
            "name": "dns01",
            "api_endpoint": "https://dns01.example.net:1073",
            "role": "authoritative",
            "cluster_id": "cluster-a",
        }
    )
    assert response["agent_token"]
    assert response["node"]["status"] == "registered"
    assert app.node("dns01")["node"]["api_endpoint"] == "https://dns01.example.net:1073"
    assert app.node_status("dns01")["dnsbeat"]["score"] == 100


def test_manager_api_route_contract_exists_without_requiring_fastapi() -> None:
    app = create_fastapi_app()
    paths = {getattr(route, "path", "") for route in getattr(app, "routes", [])}
    assert "/health" in paths
    assert "/version" in paths
    assert "/nodes" in paths
    assert "/nodes/{node_id}" in paths
    assert "/nodes/{node_id}/status" in paths
    assert "/dnssync/dry-run" in paths
    assert "/changes" not in paths


def test_json_inventory_persists_nodes(tmp_path: Path) -> None:
    repository = JsonNodeInventoryRepository(tmp_path / "nodes.json")
    service = NodeRegistrationService(repository)
    node = service.register_node(
        ManagedNode("dns01", "dns01", "https://dns01:1073", NodeRole.AUTHORITATIVE, cluster_id="cluster-a")
    )
    assert node.agent_token
    reloaded = NodeRegistrationService(JsonNodeInventoryRepository(tmp_path / "nodes.json"))
    assert reloaded.get_node("dns01").node_id == "dns01"
    assert reloaded.set_status("dns01", NodeStatus.ACTIVE).status == NodeStatus.ACTIVE


def test_dnssync_application_supports_dry_run_apply_and_rollback() -> None:
    app = create_app()
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

    payload = {"cluster_id": "cluster-a", "operation": "zone.create", "payload": {"zone": "example.com"}}
    dry_run = app.dry_run_dnssync(payload)["execution"]
    assert dry_run["mode"] == "dry-run"
    assert dry_run["accepted"] is True

    applied = app.apply_dnssync({**payload, "approved_plan_hash": dry_run["plan_hash"]})["execution"]
    assert applied["mode"] == "apply"

    rolled_back = app.rollback_dnssync({**payload, "approved_plan_hash": dry_run["plan_hash"]})["execution"]
    assert rolled_back["mode"] == "rollback"


def test_rbac_minimal_roles_are_stable() -> None:
    assert MANAGER_ADMIN_ROLE.name == "admin"
    assert MANAGER_OPERATOR_ROLE.name == "operator"
    assert MANAGER_VIEWER_ROLE.name == "viewer"
    assert MANAGER_ADMIN_ROLE.allows("manager:rbac:admin") is True
    assert MANAGER_OPERATOR_ROLE.allows("manager:sync:operate") is True
    assert MANAGER_VIEWER_ROLE.allows("manager:sync:operate") is False
    assert MANAGER_VIEWER_ROLE.allows("manager:sync:read") is True
