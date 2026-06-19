from __future__ import annotations

import pytest

from dnsforge_manager.application.core.manager_application import create_app
from dnsforge_manager.domain.inventory import NodeRole
from dnsforge_manager.domain.inventory.models import ManagedNode, NodeStatus
from dnsforge_manager.domain.workflows.models import ChangeRequestStatus, ManagerChangeRequest
from dnsforge_manager.application.workflows import ManagerChangeWorkflow
from dnsforge_manager.infrastructure.dnssync import RecordingDNSForgeNodeClient
from dnsforge_manager.interfaces.api.fastapi_app import create_fastapi_app


def _approved_cluster_app():
    app = create_app()
    app.registration_service.register_node(
        ManagedNode(
            "dns01",
            "dns01",
            "https://dns01:1073",
            NodeRole.AUTHORITATIVE,
            cluster_id="cluster-a",
        )
    )
    app.registration_service.approve_node("dns01")
    app.registration_service.set_status("dns01", NodeStatus.HEALTHY)
    return app


def test_change_request_lifecycle_requires_approval_and_dry_run() -> None:
    app = _approved_cluster_app()
    created = app.create_change(
        {"cluster_id": "cluster-a", "operation": "zone.create", "payload": {"zone": "example.com"}},
        actor="operator",
        role="operator",
    )
    change_id = str(created["change"]["change_id"])
    assert created["change"]["status"] == ChangeRequestStatus.PENDING.value

    dry_run = app.dry_run_change(change_id, actor="operator", role="operator")
    plan_hash = str(dry_run["execution"]["plan_hash"])

    approved = app.approve_change(change_id, actor="admin", role="admin")
    assert approved["change"]["status"] == ChangeRequestStatus.APPROVED.value

    applied = app.apply_change(change_id, approved_plan_hash=plan_hash, actor="admin", role="admin")
    assert applied["change"]["status"] == ChangeRequestStatus.APPLIED.value

    rolled_back = app.rollback_change(change_id, approved_plan_hash=plan_hash, actor="admin", role="admin")
    assert rolled_back["change"]["status"] == ChangeRequestStatus.ROLLED_BACK.value


def test_viewer_cannot_create_or_apply_changes() -> None:
    app = _approved_cluster_app()
    with pytest.raises(PermissionError):
        app.create_change({"cluster_id": "cluster-a", "operation": "zone.create", "payload": {}}, role="viewer")


def test_dnsbeat_blocks_apply_when_target_health_is_not_clean() -> None:
    workflow = ManagerChangeWorkflow()
    client = RecordingDNSForgeNodeClient()
    node = ManagedNode(
        "dns01",
        "dns01",
        "https://dns01:1073",
        NodeRole.AUTHORITATIVE,
        cluster_id="cluster-a",
        status=NodeStatus.DEGRADED,
        trust_state="approved",
    )
    change = workflow.create_change(ManagerChangeRequest("cluster-a", "zone.create", {"zone": "example.com"}))
    dry_run = workflow.dry_run_change(change.change_id, (node,))
    workflow.approve_change(change.change_id, actor="admin")

    with pytest.raises(PermissionError, match="DNSBeat blocked"):
        workflow.apply_change(change.change_id, (node,), client, approved_plan_hash=dry_run.plan_hash)


def test_manager_change_routes_exist_without_fastapi() -> None:
    app = create_fastapi_app()
    paths = {getattr(route, "path", "") for route in getattr(app, "routes", [])}
    assert "/changes" in paths
    assert "/changes/{change_id}" in paths
    assert "/changes/{change_id}/dry-run" in paths
    assert "/changes/{change_id}/approve" in paths
    assert "/changes/{change_id}/apply" in paths
    assert "/changes/{change_id}/rollback" in paths
