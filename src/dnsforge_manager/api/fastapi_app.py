from __future__ import annotations

from typing import Any

from dnsforge_manager.api.app import ManagerApplication, create_app as create_core_app


class RouteSpec:
    def __init__(self, method: str, path: str) -> None:
        self.method = method
        self.path = path


class FastAPIUnavailableApp:
    """Dependency-light stand-in used when FastAPI is not installed in the local environment."""

    def __init__(self, core: ManagerApplication) -> None:
        self.core = core
        self.routes = [
            RouteSpec("GET", "/health"),
            RouteSpec("GET", "/version"),
            RouteSpec("GET", "/nodes"),
            RouteSpec("POST", "/nodes"),
            RouteSpec("GET", "/nodes/{node_id}"),
            RouteSpec("GET", "/nodes/{node_id}/status"),
        ]


def create_fastapi_app(core: ManagerApplication | None = None) -> Any:
    manager = core or create_core_app()
    try:
        from fastapi import FastAPI
    except Exception:
        return FastAPIUnavailableApp(manager)

    app = FastAPI(title="DNSForge Manager", version=manager.version()["version"])

    @app.get("/health")
    def health() -> dict[str, Any]:
        return manager.health()

    @app.get("/version")
    def version() -> dict[str, Any]:
        return manager.version()

    @app.get("/nodes")
    def list_nodes() -> dict[str, Any]:
        return manager.nodes()

    @app.post("/nodes")
    def register_node(payload: dict[str, Any]) -> dict[str, Any]:
        return manager.register_node(payload)

    @app.get("/nodes/{node_id}")
    def get_node(node_id: str) -> dict[str, Any]:
        return manager.node(node_id)

    @app.get("/nodes/{node_id}/status")
    def get_node_status(node_id: str) -> dict[str, Any]:
        return manager.node_status(node_id)

    return app
