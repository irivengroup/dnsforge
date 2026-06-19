from __future__ import annotations

from typing import Any

from dnsforge_manager.application.core.manager_application import ManagerApplication, create_app as create_core_app


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
            RouteSpec("POST", "/nodes/{node_id}/approve"),
            RouteSpec("POST", "/nodes/{node_id}/revoke"),
            RouteSpec("POST", "/nodes/{node_id}/rotate-token"),
            RouteSpec("GET", "/nodes/{node_id}"),
            RouteSpec("GET", "/nodes/{node_id}/status"),
            RouteSpec("GET", "/audit"),
            RouteSpec("GET", "/changes"),
            RouteSpec("POST", "/changes"),
            RouteSpec("GET", "/changes/{change_id}"),
            RouteSpec("POST", "/changes/{change_id}/dry-run"),
            RouteSpec("POST", "/changes/{change_id}/approve"),
            RouteSpec("POST", "/changes/{change_id}/reject"),
            RouteSpec("POST", "/changes/{change_id}/apply"),
            RouteSpec("POST", "/changes/{change_id}/rollback"),
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

    @app.post("/nodes/{node_id}/approve")
    def approve_node(node_id: str) -> dict[str, Any]:
        return manager.approve_node(node_id)

    @app.post("/nodes/{node_id}/revoke")
    def revoke_node(node_id: str) -> dict[str, Any]:
        return manager.revoke_node(node_id)

    @app.post("/nodes/{node_id}/rotate-token")
    def rotate_node_token(node_id: str) -> dict[str, Any]:
        return manager.rotate_node_token(node_id)

    @app.get("/nodes/{node_id}")
    def get_node(node_id: str) -> dict[str, Any]:
        return manager.node(node_id)

    @app.get("/nodes/{node_id}/status")
    def get_node_status(node_id: str) -> dict[str, Any]:
        return manager.node_status(node_id)

    @app.get("/audit")
    def audit_events() -> dict[str, Any]:
        return manager.audit_events()

    @app.get("/changes")
    def list_changes() -> dict[str, Any]:
        return manager.changes()

    @app.post("/changes")
    def create_change(payload: dict[str, Any]) -> dict[str, Any]:
        return manager.create_change(payload)

    @app.get("/changes/{change_id}")
    def get_change(change_id: str) -> dict[str, Any]:
        return manager.change(change_id)

    @app.post("/changes/{change_id}/dry-run")
    def dry_run_change(change_id: str) -> dict[str, Any]:
        return manager.dry_run_change(change_id)

    @app.post("/changes/{change_id}/approve")
    def approve_change(change_id: str) -> dict[str, Any]:
        return manager.approve_change(change_id)

    @app.post("/changes/{change_id}/reject")
    def reject_change(change_id: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        return manager.reject_change(change_id, reason=None if payload is None else str(payload.get("reason", "")))

    @app.post("/changes/{change_id}/apply")
    def apply_change(change_id: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        return manager.apply_change(
            change_id,
            approved_plan_hash=None if payload is None else str(payload.get("approved_plan_hash", "")),
        )

    @app.post("/changes/{change_id}/rollback")
    def rollback_change(change_id: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        return manager.rollback_change(
            change_id,
            approved_plan_hash=None if payload is None else str(payload.get("approved_plan_hash", "")),
        )

    return app
