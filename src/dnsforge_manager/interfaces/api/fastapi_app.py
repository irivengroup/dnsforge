from __future__ import annotations

from typing import Any, cast

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
            RouteSpec("GET", "/nodes/{node_id}/readiness"),
            RouteSpec("GET", "/audit"),
            RouteSpec("GET", "/dnssync/plans"),
            RouteSpec("POST", "/dnssync/plans"),
            RouteSpec("POST", "/dnssync/validate"),
            RouteSpec("POST", "/dnssync/dry-run"),
            RouteSpec("POST", "/dnssync/apply"),
            RouteSpec("POST", "/dnssync/rollback"),
            RouteSpec("GET", "/dnssync/status"),
            RouteSpec("GET", "/monitor/status"),
            RouteSpec("GET", "/monitor/agents"),
            RouteSpec("GET", "/monitor/clusters"),
            RouteSpec("GET", "/monitor/alerts"),
            RouteSpec("GET", "/inventory/sites"),
            RouteSpec("POST", "/inventory/sites"),
            RouteSpec("GET", "/inventory/clusters"),
            RouteSpec("POST", "/inventory/clusters"),
            RouteSpec("GET", "/inventory/agents"),
            RouteSpec("POST", "/inventory/agents"),
            RouteSpec("GET", "/inventory/environments"),
            RouteSpec("GET", "/inventory/agent-status"),
            RouteSpec("POST", "/inventory/agent-status"),
            RouteSpec("GET", "/inventory/agent-compliance"),
            RouteSpec("POST", "/inventory/agent-compliance"),
            RouteSpec("GET", "/inventory/agent-compliance/history"),
            RouteSpec("GET", "/inventory/agent-compliance/trends"),
            RouteSpec("GET", "/inventory/agent-compliance/report"),
            RouteSpec("GET", "/trust/enrollments"),
            RouteSpec("GET", "/trust/agents"),
            RouteSpec("POST", "/trust/enroll"),
            RouteSpec("POST", "/trust/approve"),
            RouteSpec("POST", "/trust/revoke"),
            RouteSpec("POST", "/trust/rotate-token"),
            RouteSpec("GET", "/trust/policies"),
            RouteSpec("POST", "/trust/policies"),
            RouteSpec("POST", "/trust/policies/evaluate"),
            RouteSpec("GET", "/trust/rotations"),
            RouteSpec("POST", "/trust/rotate-certificate"),
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

    @app.get("/nodes/{node_id}/readiness")
    def get_node_readiness(node_id: str) -> dict[str, Any]:
        return cast(Any, manager).node_readiness(node_id)

    @app.get("/audit")
    def audit_events() -> dict[str, Any]:
        return manager.audit_events()

    @app.get("/dnssync/plans")
    def list_dnssync_plans() -> dict[str, Any]:
        return manager.dnssync_plans()

    @app.post("/dnssync/plans")
    def create_dnssync_plan(payload: dict[str, Any]) -> dict[str, Any]:
        return manager.create_dnssync_plan(payload)

    @app.post("/dnssync/validate")
    def validate_dnssync_plan(payload: dict[str, Any]) -> dict[str, Any]:
        return manager.validate_dnssync_plan(payload)

    @app.post("/dnssync/dry-run")
    def dry_run_dnssync(payload: dict[str, Any]) -> dict[str, Any]:
        return manager.dry_run_dnssync(payload)

    @app.post("/dnssync/apply")
    def apply_dnssync(payload: dict[str, Any]) -> dict[str, Any]:
        return manager.apply_dnssync(payload)

    @app.post("/dnssync/rollback")
    def rollback_dnssync(payload: dict[str, Any]) -> dict[str, Any]:
        return manager.rollback_dnssync(payload)

    @app.get("/dnssync/status")
    def dnssync_status() -> dict[str, Any]:
        return manager.dnssync_status()

    @app.get("/monitor/status")
    def monitor_status() -> dict[str, Any]:
        return manager.monitor_status()

    @app.get("/monitor/agents")
    def monitor_agents() -> dict[str, Any]:
        return manager.monitor_agents()

    @app.get("/monitor/clusters")
    def monitor_clusters() -> dict[str, Any]:
        return manager.monitor_clusters()

    @app.get("/monitor/alerts")
    def monitor_alerts() -> dict[str, Any]:
        return manager.monitor_alerts()

    @app.get("/inventory/sites")
    def list_inventory_sites() -> dict[str, Any]:
        return manager.inventory_sites()

    @app.post("/inventory/sites")
    def create_inventory_site(payload: dict[str, Any]) -> dict[str, Any]:
        return manager.create_inventory_site(payload)

    @app.get("/inventory/clusters")
    def list_inventory_clusters() -> dict[str, Any]:
        return manager.inventory_clusters()

    @app.post("/inventory/clusters")
    def create_inventory_cluster(payload: dict[str, Any]) -> dict[str, Any]:
        return manager.create_inventory_cluster(payload)

    @app.get("/inventory/agents")
    def list_inventory_agents() -> dict[str, Any]:
        return manager.inventory_agents()

    @app.post("/inventory/agents")
    def register_inventory_agent(payload: dict[str, Any]) -> dict[str, Any]:
        return manager.register_inventory_agent(payload)

    @app.get("/inventory/environments")
    def list_inventory_environments() -> dict[str, Any]:
        return manager.inventory_environments()

    @app.get("/inventory/agent-status")
    def inventory_agent_status() -> dict[str, Any]:
        return manager.inventory_agent_status()

    @app.post("/inventory/agent-status")
    def update_inventory_agent_status(payload: dict[str, Any]) -> dict[str, Any]:
        return manager.update_inventory_agent_status(payload)

    @app.get("/inventory/agent-compliance")
    def inventory_agent_compliance() -> dict[str, Any]:
        return manager.inventory_agent_compliance()

    @app.post("/inventory/agent-compliance")
    def update_inventory_agent_compliance(payload: dict[str, Any]) -> dict[str, Any]:
        return manager.update_inventory_agent_compliance(payload)

    @app.get("/inventory/agent-compliance/history")
    def inventory_agent_compliance_history(fingerprint: str | None = None) -> dict[str, Any]:
        return manager.inventory_agent_compliance_history(fingerprint)

    @app.get("/inventory/agent-compliance/trends")
    def inventory_agent_compliance_trends(fingerprint: str | None = None) -> dict[str, Any]:
        return manager.inventory_agent_compliance_trends(fingerprint)

    @app.get("/inventory/agent-compliance/report")
    def inventory_agent_compliance_report(fingerprint: str | None = None) -> dict[str, Any]:
        return manager.inventory_agent_compliance_report(fingerprint)

    @app.get("/trust/enrollments")
    def list_trust_enrollments() -> dict[str, Any]:
        return manager.trust_enrollments()

    @app.get("/trust/agents")
    def list_trusted_agents() -> dict[str, Any]:
        return manager.trusted_agents()

    @app.post("/trust/enroll")
    def enroll_agent(payload: dict[str, Any]) -> dict[str, Any]:
        return manager.enroll_agent(payload)

    @app.post("/trust/approve")
    def approve_agent_enrollment(payload: dict[str, Any]) -> dict[str, Any]:
        return manager.approve_agent_enrollment(str(payload["request_id"]))

    @app.post("/trust/revoke")
    def revoke_trusted_agent(payload: dict[str, Any]) -> dict[str, Any]:
        return manager.revoke_trusted_agent(str(payload["fingerprint"]))

    @app.post("/trust/rotate-token")
    def rotate_trusted_agent_token(payload: dict[str, Any]) -> dict[str, Any]:
        return manager.rotate_trusted_agent_token(str(payload["fingerprint"]))

    @app.get("/trust/policies")
    def list_trust_policies() -> dict[str, Any]:
        return manager.trust_policies()

    @app.post("/trust/policies")
    def create_trust_policy(payload: dict[str, Any]) -> dict[str, Any]:
        return manager.create_trust_policy(payload)

    @app.post("/trust/policies/evaluate")
    def evaluate_trust_policy(payload: dict[str, Any]) -> dict[str, Any]:
        return manager.evaluate_trust_policy(str(payload["request_id"]), str(payload["policy_id"]))

    @app.get("/trust/rotations")
    def list_trust_rotations(fingerprint: str | None = None) -> dict[str, Any]:
        return manager.trust_rotations(fingerprint)

    @app.post("/trust/rotate-certificate")
    def rotate_trusted_agent_certificate(payload: dict[str, Any]) -> dict[str, Any]:
        return manager.rotate_trusted_agent_certificate(
            str(payload["fingerprint"]),
            public_key=None if payload.get("public_key") is None else str(payload.get("public_key")),
            reason=str(payload.get("reason", "certificate-rotation")),
        )

    return app
