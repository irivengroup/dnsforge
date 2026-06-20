from dnsforge_manager.application.core.manager_application import create_app
from dnsforge_manager.application.inventory.central_inventory_service import CentralInventoryService
from dnsforge_manager.interfaces.api.fastapi_app import create_fastapi_app


def test_compliance_report_combines_aggregate_trends_and_risk():
    service = CentralInventoryService()
    service.update_agent_compliance(
        {
            "fingerprint": "agent-a",
            "compliance": "DRIFTED",
            "drift_count": 2,
            "last_checked": "2026-06-20T10:00:00Z",
        }
    )
    service.update_agent_compliance(
        {
            "fingerprint": "agent-b",
            "compliance": "FAILED",
            "drift_count": 4,
            "last_checked": "2026-06-20T10:05:00Z",
        }
    )

    report = service.build_agent_compliance_report()

    assert report["schema"] == "dnsforge.manager-compliance-report.v1"
    assert report["aggregate"]["status"] == "FAILED"
    assert report["risk"]["drifted_agents"] == 2
    assert report["risk"]["failed_agents"] == 1
    assert report["risk"]["total_drift_count"] == 6
    assert report["trends"]["summary"]["agents"] == 2


def test_manager_exposes_filtered_compliance_report():
    app = create_app()
    app.update_inventory_agent_compliance(
        {
            "fingerprint": "agent-a",
            "compliance": "DRIFTED",
            "drift_count": 3,
            "last_checked": "2026-06-20T10:00:00Z",
        }
    )
    app.update_inventory_agent_compliance(
        {
            "fingerprint": "agent-b",
            "compliance": "COMPLIANT",
            "drift_count": 0,
            "last_checked": "2026-06-20T10:05:00Z",
        }
    )

    report = app.inventory_agent_compliance_report("agent-a")

    assert report["risk"]["drifted_agents"] == 1
    assert report["risk"]["total_drift_count"] == 3
    assert report["trends"]["summary"]["agents"] == 1


def test_manager_compliance_report_route_is_exposed_without_fastapi_dependency():
    api = create_fastapi_app(create_app())
    routes = set()
    for route in getattr(api, "routes", []):
        if hasattr(route, "method"):
            routes.add((route.method, route.path))
        else:
            for method in getattr(route, "methods", set()):
                routes.add((method, getattr(route, "path", "")))

    assert ("GET", "/inventory/agent-compliance/report") in routes
