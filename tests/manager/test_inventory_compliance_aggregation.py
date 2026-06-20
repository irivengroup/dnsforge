from __future__ import annotations

import json

from dnsforge_manager.application.core.manager_application import create_app
from dnsforge_manager.application.inventory.central_inventory_service import CentralInventoryService
from dnsforge_manager.infrastructure.inventory.central_repository import JsonCentralInventoryRepository
from dnsforge_manager.interfaces.api.fastapi_app import create_fastapi_app
from dnsforge_manager.interfaces.cli.main import main as manager_main


def test_central_inventory_aggregates_agent_compliance_by_worst_state() -> None:
    service = CentralInventoryService()
    service.update_agent_compliance(
        {
            "fingerprint": "agent-1",
            "compliance": "COMPLIANT",
            "drift_count": 0,
            "message": "clean",
        }
    )
    service.update_agent_compliance(
        {
            "fingerprint": "agent-2",
            "compliance": "DRIFTED",
            "drift_count": 3,
            "message": "manual change detected",
            "findings": [{"resource": "/etc/named.conf", "severity": "CRITICAL"}],
        }
    )

    aggregate = service.aggregate_compliance()

    assert aggregate["status"] == "DRIFTED"
    assert aggregate["summary"]["COMPLIANT"] == 1
    assert aggregate["summary"]["DRIFTED"] == 1
    assert aggregate["drift_count"] == 3
    assert service.list_agent_compliance()[1].findings[0]["resource"] == "/etc/named.conf"


def test_json_central_inventory_repository_persists_agent_compliance(tmp_path) -> None:
    repository = JsonCentralInventoryRepository(tmp_path / "central-inventory.json")
    service = CentralInventoryService(repository)
    service.update_agent_compliance(
        {
            "fingerprint": "agent-json",
            "compliance": "FAILED",
            "drift_count": 4,
            "last_checked": "2026-06-20T14:00:00Z",
            "message": "rendered baseline unavailable",
        }
    )

    reloaded = CentralInventoryService(JsonCentralInventoryRepository(tmp_path / "central-inventory.json"))
    aggregate = reloaded.aggregate_compliance()

    assert aggregate["status"] == "FAILED"
    assert aggregate["agents"][0]["fingerprint"] == "agent-json"
    assert aggregate["agents"][0]["last_checked"] == "2026-06-20T14:00:00Z"


def test_manager_application_audits_inventory_compliance_updates() -> None:
    app = create_app()
    updated = app.update_inventory_agent_compliance(
        {
            "fingerprint": "agent-app",
            "compliance": "WARNING",
            "drift_count": 1,
            "message": "minor drift",
        },
        actor="operator",
    )

    listed = app.inventory_agent_compliance()
    audit = app.audit_events()["events"]

    assert updated["agent_compliance"]["compliance"] == "WARNING"
    assert listed["status"] == "WARNING"
    assert audit[-1]["action"] == "inventory.agent.compliance"
    assert audit[-1]["metadata"]["drift_count"] == 1


def test_manager_inventory_compliance_routes_are_exposed_without_fastapi_dependency() -> None:
    api = create_fastapi_app(create_app())
    routes = set()
    for route in getattr(api, "routes", []):
        if hasattr(route, "method"):
            routes.add((route.method, route.path))
        else:
            for method in getattr(route, "methods", set()):
                routes.add((method, getattr(route, "path", "")))

    assert ("GET", "/inventory/agent-compliance") in routes
    assert ("POST", "/inventory/agent-compliance") in routes


def test_manager_inventory_compliance_cli_update_and_list(capsys) -> None:
    assert (
        manager_main(
            [
                "inventory",
                "compliance",
                "update",
                "--fingerprint",
                "agent-cli",
                "--compliance",
                "COMPLIANT",
                "--message",
                "clean",
            ]
        )
        == 0
    )
    update_payload = json.loads(capsys.readouterr().out)

    assert update_payload["agent_compliance"]["fingerprint"] == "agent-cli"
    assert update_payload["agent_compliance"]["compliance"] == "COMPLIANT"

    assert manager_main(["inventory", "compliance", "list"]) == 0
    listed_payload = json.loads(capsys.readouterr().out)
    assert listed_payload["status"] == "COMPLIANT"
