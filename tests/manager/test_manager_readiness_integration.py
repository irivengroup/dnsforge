from __future__ import annotations

from dnsforge_manager.application.core.manager_application import ManagerApplication
from dnsforge_manager.domain.inventory.models import NodeRole


def _node_payload() -> dict[str, object]:
    return {
        "node_id": "dns01",
        "name": "dns01",
        "api_endpoint": "https://dns01.local:1073",
        "role": NodeRole.AUTHORITATIVE.value,
        "site": "primary",
    }


def test_manager_exposes_agent_readiness_in_status_and_endpoint() -> None:
    app = ManagerApplication()
    app.register_node(_node_payload())
    app.approve_node("dns01")

    status = app.node_status("dns01")
    readiness = app.node_readiness("dns01")

    assert status["readiness"]["status"] == "READY"
    assert readiness["readiness"]["score"] == 100


def test_fastapi_fallback_lists_readiness_route() -> None:
    from dnsforge_manager.interfaces.api.fastapi_app import FastAPIUnavailableApp

    routes = {route.path for route in FastAPIUnavailableApp(ManagerApplication()).routes}

    assert "/nodes/{node_id}/readiness" in routes
