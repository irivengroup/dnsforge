from __future__ import annotations

import pytest

from dnsforge_manager.application.core.manager_application import ManagerApplication
from dnsforge_manager.interfaces.api.fastapi_app import create_fastapi_app


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


def test_dnssync_requires_dry_run_hash_for_apply_and_rollback() -> None:
    app = _approved_cluster_app()
    payload = {"cluster_id": "cluster-a", "operation": "zone.create", "payload": {"zone": "example.com"}}
    dry_run = app.dry_run_dnssync(payload, actor="operator", role="operator")
    plan_hash = str(dry_run["execution"]["plan_hash"])

    applied = app.apply_dnssync({**payload, "approved_plan_hash": plan_hash}, actor="admin", role="admin")
    assert applied["execution"]["mode"] == "apply"

    rolled_back = app.rollback_dnssync({**payload, "approved_plan_hash": plan_hash}, actor="admin", role="admin")
    assert rolled_back["execution"]["mode"] == "rollback"


def test_viewer_cannot_operate_dnssync() -> None:
    app = _approved_cluster_app()
    with pytest.raises(PermissionError):
        app.dry_run_dnssync(
            {"cluster_id": "cluster-a", "operation": "zone.create", "payload": {}},
            role="viewer",
        )


def test_manager_dnssync_routes_exist_without_fastapi() -> None:
    app = create_fastapi_app()
    paths = {getattr(route, "path", "") for route in getattr(app, "routes", [])}
    assert "/dnssync/plans" in paths
    assert "/dnssync/validate" in paths
    assert "/dnssync/dry-run" in paths
    assert "/dnssync/apply" in paths
    assert "/dnssync/rollback" in paths
    assert "/dnssync/status" in paths
    assert "/dnssync/history" in paths
    assert "/changes" not in paths
