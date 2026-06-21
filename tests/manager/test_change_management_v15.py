from __future__ import annotations

import pytest

from dnsforge_manager.application.change_management.repository import JsonChangeManagementRepository
from dnsforge_manager.application.change_management.service import ChangeManagementService
from dnsforge_manager.application.core.manager_application import ManagerApplication
from dnsforge_manager.domain.change_management.models import ChangeLifecycleStatus, ChangeRiskLevel
from dnsforge_manager.interfaces.cli.main import build_parser, main
from dnsforge_manager.interfaces.api.fastapi_app import create_fastapi_app


def _payload() -> dict[str, object]:
    return {
        "title": "Create zone",
        "description": "Controlled zone creation",
        "target_scope": "CLUSTER",
        "target_id": "auth-a",
        "operation": "zone.create",
        "payload": {"zone": "example.com"},
    }


def test_change_management_lifecycle_and_gates() -> None:
    service = ChangeManagementService()
    change = service.create_change(_payload(), requested_by="operator")
    assert change.status is ChangeLifecycleStatus.DRAFT
    assert change.risk_level is ChangeRiskLevel.MEDIUM

    reviewed = service.review_change(change.change_id, reviewer="reviewer")
    assert reviewed.status is ChangeLifecycleStatus.REVIEWED

    approved = service.approve_change(change.change_id, approver="admin", comment="approved")
    assert approved.status is ChangeLifecycleStatus.APPROVED

    execution = service.execute_change(
        change.change_id,
        actor="admin",
        signals={"readiness": "READY", "trust": "TRUSTED", "compliance": "COMPLIANT"},
    )
    assert execution.result is ChangeLifecycleStatus.COMPLETED
    assert service.get_change(change.change_id).status is ChangeLifecycleStatus.COMPLETED

    rollback = service.rollback_change(change.change_id, reason="post-check", actor="admin")
    assert rollback.reason == "post-check"
    assert service.get_change(change.change_id).status is ChangeLifecycleStatus.ROLLED_BACK


def test_change_management_blocks_untrusted_execution() -> None:
    service = ChangeManagementService()
    change = service.create_change(_payload())
    service.approve_change(change.change_id, approver="admin")

    with pytest.raises(PermissionError, match="trust"):
        service.execute_change(
            change.change_id, signals={"readiness": "READY", "trust": "REVOKED", "compliance": "COMPLIANT"}
        )

    assert service.get_change(change.change_id).status is ChangeLifecycleStatus.FAILED


def test_change_management_json_repository_persists_requests(tmp_path) -> None:
    repository = JsonChangeManagementRepository(tmp_path / "change-management.json")
    service = ChangeManagementService(repository)
    change = service.create_change(_payload())

    reloaded = ChangeManagementService(JsonChangeManagementRepository(tmp_path / "change-management.json"))
    assert reloaded.get_change(change.change_id).operation == "zone.create"


def test_manager_application_exposes_change_management() -> None:
    app = ManagerApplication()
    created = app.create_managed_change(_payload(), actor="operator", role="operator")
    change_id = str(created["change"]["change_id"])

    assert app.review_managed_change(change_id, actor="reviewer", role="operator")["change"]["status"] == "REVIEWED"
    assert app.approve_managed_change(change_id, actor="admin", role="admin")["change"]["status"] == "APPROVED"
    assert app.execute_managed_change(change_id, actor="admin", role="admin")["change"]["status"] == "COMPLETED"


def test_change_cli_parser_exposes_v15_commands() -> None:
    parser = build_parser()
    parsed = parser.parse_args(
        [
            "change",
            "create",
            "--title",
            "Create zone",
            "--target-id",
            "auth-a",
            "--operation",
            "zone.create",
        ]
    )
    assert parsed.command == "change"
    assert parsed.change_action == "create"


def test_change_cli_create_prints_json(capsys) -> None:
    code = main(
        [
            "change",
            "create",
            "--title",
            "Create zone",
            "--target-id",
            "auth-a",
            "--operation",
            "zone.create",
            "--payload",
            '{"zone":"example.com"}',
        ]
    )
    assert code == 0
    assert '"change"' in capsys.readouterr().out


def test_manager_change_routes_exist_without_fastapi() -> None:
    app = create_fastapi_app()
    paths = {route.path for route in app.routes}
    assert "/changes/{change_id}/review" in paths
    assert "/changes/{change_id}/execute" in paths
    assert "/changes/{change_id}/status" in paths
