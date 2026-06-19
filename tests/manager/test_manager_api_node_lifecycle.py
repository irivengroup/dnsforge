from __future__ import annotations

from pathlib import Path

from dnsforge_manager.api import create_app, create_fastapi_app
from dnsforge_manager.dnssync import RecordingDNSForgeNodeClient, SyncMode
from dnsforge_manager.inventory import JsonNodeInventoryRepository, ManagedNode, NodeRegistrationService, NodeRole, NodeStatus
from dnsforge_manager.rbac import MANAGER_ADMIN_ROLE, MANAGER_OPERATOR_ROLE, MANAGER_VIEWER_ROLE
from dnsforge_manager.workflows import ManagerChangeRequest, ManagerChangeWorkflow


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


def test_dnssync_workflow_supports_dry_run_apply_and_rollback() -> None:
    nodes = (
        ManagedNode("dns01", "dns01", "https://dns01:1073", NodeRole.AUTHORITATIVE, cluster_id="cluster-a"),
        ManagedNode("dns02", "dns02", "https://dns02:1073", NodeRole.AUTHORITATIVE, cluster_id="cluster-a"),
    )
    workflow = ManagerChangeWorkflow()
    request = ManagerChangeRequest("cluster-a", "zone.create", {"zone": "example.com"})
    dry_run = workflow.dry_run_cluster_change(request, nodes)
    assert dry_run.mode == SyncMode.DRY_RUN
    assert dry_run.accepted is True

    client = RecordingDNSForgeNodeClient()
    applied = workflow.submit_cluster_change(request, nodes, client)
    assert applied.mode == SyncMode.APPLY
    assert [node_id for node_id, _ in client.operations] == ["dns01", "dns02"]

    rolled_back = workflow.rollback_cluster_change(request, nodes, client)
    assert rolled_back.mode == SyncMode.ROLLBACK
    assert client.operations[-1][1].operation == "rollback.zone.create"


def test_rbac_minimal_roles_are_stable() -> None:
    assert MANAGER_ADMIN_ROLE.name == "admin"
    assert MANAGER_OPERATOR_ROLE.name == "operator"
    assert MANAGER_VIEWER_ROLE.name == "viewer"
    assert MANAGER_ADMIN_ROLE.allows("manager:rbac:admin") is True
    assert MANAGER_OPERATOR_ROLE.allows("manager:sync:operate") is True
    assert MANAGER_VIEWER_ROLE.allows("manager:sync:operate") is False
