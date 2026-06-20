from dnsforge_manager.application.core.manager_application import create_app
from dnsforge_manager.domain.security import AgentTrustState, certificate_fingerprint
from dnsforge_manager.infrastructure.security import JsonAgentTrustRepository
from dnsforge_manager.interfaces.api.fastapi_app import create_fastapi_app
from dnsforge_manager.interfaces.cli.main import main as manager_main
from dnsforge_manager.application.security.agent_trust_service import AgentTrustService


def test_agent_trust_enrollment_approval_rotation_and_revoke() -> None:
    app = create_app()
    public_key = "ssh-ed25519 AAAATEST dns01"
    enrolled = app.enroll_agent(
        {
            "hostname": "dns01",
            "version": "14.3.0",
            "profile": "authoritative",
            "site": "emea",
            "cluster": "c1",
            "public_key": public_key,
        }
    )

    request = enrolled["enrollment"]
    assert request["status"] == AgentTrustState.PENDING.value
    assert request["fingerprint"] == certificate_fingerprint(public_key)

    approved = app.approve_agent_enrollment(str(request["request_id"]))
    assert approved["agent_token"]
    assert approved["trusted_agent"]["state"] == AgentTrustState.APPROVED.value
    assert "token" not in approved["trusted_agent"]

    fingerprint = str(approved["trusted_agent"]["fingerprint"])
    listed = app.trusted_agents()
    assert listed["trusted_agents"][0]["fingerprint"] == fingerprint
    assert "token" not in listed["trusted_agents"][0]

    rotated = app.rotate_trusted_agent_token(fingerprint)
    assert rotated["agent_token"] != approved["agent_token"]

    revoked = app.revoke_trusted_agent(fingerprint)
    assert revoked["trusted_agent"]["state"] == AgentTrustState.REVOKED.value
    assert revoked["trusted_agent"]["certificate"]["revoked_at"]


def test_agent_trust_json_repository_persists_without_exposing_tokens(tmp_path) -> None:
    repository = JsonAgentTrustRepository(tmp_path / "trust.json")
    service = AgentTrustService(trust_repository=repository)
    request = service.enroll(
        {
            "hostname": "dns02",
            "version": "14.3.0",
            "profile": "proxy-forwarder",
            "public_key": "ssh-ed25519 AAAATEST dns02",
        }
    )
    approved = service.approve_enrollment(request.request_id)

    reloaded = JsonAgentTrustRepository(tmp_path / "trust.json").get_agent(approved.fingerprint)
    assert reloaded.token == approved.token
    assert "token" not in reloaded.to_dict()


def test_agent_trust_routes_are_exposed_without_fastapi_dependency() -> None:
    api = create_fastapi_app(create_app())
    routes = set()
    for route in getattr(api, "routes", []):
        if hasattr(route, "method"):
            routes.add((route.method, route.path))
        else:
            for method in getattr(route, "methods", set()):
                routes.add((method, getattr(route, "path", "")))

    assert ("GET", "/trust/enrollments") in routes
    assert ("GET", "/trust/agents") in routes
    assert ("POST", "/trust/enroll") in routes
    assert ("POST", "/trust/approve") in routes
    assert ("POST", "/trust/revoke") in routes
    assert ("POST", "/trust/rotate-token") in routes


def test_manager_trust_cli_commands_are_exposed(capsys) -> None:
    assert manager_main(["trust", "enrollments"]) == 0
    out = capsys.readouterr().out
    assert "enrollments" in out
