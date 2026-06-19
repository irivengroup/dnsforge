from __future__ import annotations

from dnsforge_manager.application.core.manager_application import create_app
from dnsforge_manager.domain.core import (
    DNSBEAT_BOUNDARY,
    DNSFORGE_BOUNDARY,
    DNSFORGE_MANAGER_BOUNDARY,
    DNSSYNC_BOUNDARY,
)
from dnsforge_manager.application.dnssync.dnssync_service import DNSSyncService
from dnsforge_manager.domain.dnssync import DNSForgeOperation
from dnsforge_manager.infrastructure.dnssync import RecordingDNSForgeNodeClient
from dnsforge_manager.application.inventory.node_registration_service import NodeRegistrationService
from dnsforge_manager.domain.inventory import ManagedNode, NodeRole
from dnsforge_manager.application.workflows.change_workflow import ManagerChangeWorkflow
from dnsforge_manager.domain.workflows.models import ManagerChangeRequest


def test_product_boundaries_keep_bind_writes_local_to_dnsforge() -> None:
    assert DNSFORGE_BOUNDARY.requires_bind is True
    assert DNSFORGE_BOUNDARY.may_modify_bind_files is True
    assert DNSFORGE_MANAGER_BOUNDARY.requires_bind is False
    assert DNSFORGE_MANAGER_BOUNDARY.may_modify_bind_files is False
    assert DNSBEAT_BOUNDARY.may_modify_bind_files is False
    assert DNSSYNC_BOUNDARY.may_modify_bind_files is False


def test_manager_app_is_framework_neutral_and_does_not_require_bind() -> None:
    app = create_app()
    assert app.health()["status"] == "ok"
    products = app.boundaries()["products"]
    manager = next(product for product in products if product["name"] == "DNSForge Manager")
    assert manager["requires_bind"] is False
    assert manager["may_modify_bind_files"] is False


def test_node_registration_targets_dnsforge_api_endpoint() -> None:
    service = NodeRegistrationService()
    node = ManagedNode(
        node_id="dns01",
        name="dns01",
        api_endpoint="https://dns01.example.net:1073",
        role=NodeRole.AUTHORITATIVE,
        cluster_id="cluster-a",
    )
    service.register_node(node)
    assert service.list_nodes() == (node,)


def test_dnssync_orchestrates_through_dnsforge_node_client() -> None:
    nodes = (
        ManagedNode("dns01", "dns01", "https://dns01:1073", NodeRole.AUTHORITATIVE, cluster_id="cluster-a"),
        ManagedNode("dns02", "dns02", "https://dns02:1073", NodeRole.AUTHORITATIVE, cluster_id="cluster-a"),
    )
    operation = DNSForgeOperation(operation="zone.create", payload={"zone": "example.com"})
    service = DNSSyncService()
    plan = service.build_cluster_plan(cluster_id="cluster-a", operation=operation, nodes=nodes)
    client = RecordingDNSForgeNodeClient()
    dry_run = service.dry_run(plan)
    result = service.execute(plan, client, approved_plan_hash=dry_run.plan_hash)
    assert result.accepted is True
    assert [node_id for node_id, _ in client.operations] == ["dns01", "dns02"]


def test_manager_change_workflow_routes_changes_through_dnssync() -> None:
    nodes = (ManagedNode("dns01", "dns01", "https://dns01:1073", NodeRole.AUTHORITATIVE, cluster_id="cluster-a"),)
    client = RecordingDNSForgeNodeClient()
    request = ManagerChangeRequest(cluster_id="cluster-a", operation="catalog.sync", payload={"scope": "cluster"})
    workflow = ManagerChangeWorkflow()
    workflow.dry_run_cluster_change(request, nodes)
    result = workflow.submit_cluster_change(request, nodes, client)
    assert result.accepted is True
    assert client.operations[0][1].operation == "catalog.sync"
