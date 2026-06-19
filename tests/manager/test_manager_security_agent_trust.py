from __future__ import annotations

import pytest

from dnsforge_manager.api import create_app, create_fastapi_app
from dnsforge_manager.audit import ManagerAuditRepository
from dnsforge_manager.dnssync import DNSForgeOperation, DNSSyncService, RecordingDNSForgeNodeClient, SyncMode
from dnsforge_manager.inventory import ManagedNode, NodeRegistrationService, NodeRole
from dnsforge_manager.rbac import RbacService


def test_node_registration_is_pending_until_approved() -> None:
    app = create_app()
    registered = app.register_node(
        {"node_id": "dns01", "api_endpoint": "https://dns01:1073", "role": "authoritative"},
        actor="admin",
        role="admin",
    )
    assert registered["node"]["trust_state"] == "pending"
    assert registered["node"]["agent_fingerprint"]

    decision = app.approve_node("dns01", actor="admin", role="admin")
    assert decision["decision"]["approved"] is True
    assert app.node("dns01")["node"]["trust_state"] == "approved"


def test_node_token_rotation_and_revoke_are_audited() -> None:
    audit = ManagerAuditRepository()
    app = create_app()
    app.audit_repository = audit
    app.register_node({"node_id": "dns01", "api_endpoint": "https://dns01:1073", "role": "authoritative"})
    old_token = app.registration_service.get_node("dns01").agent_token
    rotated = app.rotate_node_token("dns01")
    assert rotated["agent_token"]
    assert rotated["agent_token"] != old_token
    revoked = app.revoke_node("dns01")
    assert revoked["node"]["trust_state"] == "revoked"
    assert [event.action for event in audit.list()] == ["node.register", "node.token.rotate", "node.revoke"]


def test_rbac_enforcement_blocks_viewer_mutations() -> None:
    app = create_app()
    with pytest.raises(PermissionError):
        app.register_node(
            {"node_id": "dns01", "api_endpoint": "https://dns01:1073", "role": "authoritative"}, role="viewer"
        )
    RbacService().require("viewer", "manager:nodes:read")


def test_dnssync_requires_dry_run_plan_hash_for_apply() -> None:
    nodes = (ManagedNode("dns01", "dns01", "https://dns01:1073", NodeRole.AUTHORITATIVE, cluster_id="cluster-a"),)
    operation = DNSForgeOperation("zone.create", {"zone": "example.com"})
    service = DNSSyncService()
    plan = service.build_cluster_plan(cluster_id="cluster-a", operation=operation, nodes=nodes, mode=SyncMode.APPLY)
    client = RecordingDNSForgeNodeClient()

    with pytest.raises(PermissionError):
        service.execute(plan, client)

    executed = service.execute(plan, client, approved_plan_hash=plan.plan_hash)
    assert executed.accepted is True
    assert executed.plan_hash == plan.plan_hash


def test_unapproved_nodes_are_not_sync_targets() -> None:
    registration = NodeRegistrationService()
    registration.register_node(
        ManagedNode("dns01", "dns01", "https://dns01:1073", NodeRole.AUTHORITATIVE, cluster_id="cluster-a")
    )
    service = DNSSyncService()
    with pytest.raises(ValueError):
        service.build_cluster_plan(
            cluster_id="cluster-a",
            operation=DNSForgeOperation("catalog.sync", {}),
            nodes=registration.list_nodes(),
        )


def test_manager_security_routes_exist_without_fastapi() -> None:
    app = create_fastapi_app()
    paths = {getattr(route, "path", "") for route in getattr(app, "routes", [])}
    assert "/nodes/{node_id}/approve" in paths
    assert "/nodes/{node_id}/revoke" in paths
    assert "/nodes/{node_id}/rotate-token" in paths
    assert "/audit" in paths
