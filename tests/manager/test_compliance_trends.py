from dnsforge_manager.application.core.manager_application import create_app
from dnsforge_manager.application.inventory.central_inventory_service import CentralInventoryService
from dnsforge_manager.interfaces.api.fastapi_app import create_fastapi_app


def test_compliance_trends_detect_recurrent_drift():
    service = CentralInventoryService()
    service.update_agent_compliance(
        {
            "fingerprint": "agent-a",
            "compliance": "DRIFTED",
            "drift_count": 1,
            "last_checked": "2026-06-20T10:00:00Z",
        }
    )
    service.update_agent_compliance(
        {
            "fingerprint": "agent-a",
            "compliance": "COMPLIANT",
            "drift_count": 0,
            "last_checked": "2026-06-20T11:00:00Z",
        }
    )
    service.update_agent_compliance(
        {
            "fingerprint": "agent-a",
            "compliance": "DRIFTED",
            "drift_count": 2,
            "last_checked": "2026-06-20T12:00:00Z",
        }
    )

    trends = service.summarize_agent_compliance_trends()

    assert trends["summary"]["agents"] == 1
    assert trends["summary"]["recurrent_drift"] == 1
    assert trends["trends"][0]["fingerprint"] == "agent-a"
    assert trends["trends"][0]["current_compliance"] == "DRIFTED"
    assert trends["trends"][0]["observations"] == 3
    assert trends["trends"][0]["drift_observations"] == 2
    assert trends["trends"][0]["recurrent_drift"] is True


def test_manager_exposes_filtered_compliance_trends():
    app = create_app()
    app.update_inventory_agent_compliance(
        {
            "fingerprint": "agent-a",
            "compliance": "WARNING",
            "drift_count": 0,
            "last_checked": "2026-06-20T10:00:00Z",
        }
    )
    app.update_inventory_agent_compliance(
        {
            "fingerprint": "agent-b",
            "compliance": "FAILED",
            "drift_count": 4,
            "last_checked": "2026-06-20T10:05:00Z",
        }
    )

    trends = app.inventory_agent_compliance_trends("agent-b")

    assert trends["summary"]["agents"] == 1
    assert trends["trends"][0]["fingerprint"] == "agent-b"
    assert trends["trends"][0]["current_compliance"] == "FAILED"


def test_manager_compliance_trends_route_is_exposed_without_fastapi_dependency():
    api = create_fastapi_app(create_app())
    routes = set()
    for route in getattr(api, "routes", []):
        if hasattr(route, "method"):
            routes.add((route.method, route.path))
        else:
            for method in getattr(route, "methods", set()):
                routes.add((method, getattr(route, "path", "")))

    assert ("GET", "/inventory/agent-compliance/trends") in routes
