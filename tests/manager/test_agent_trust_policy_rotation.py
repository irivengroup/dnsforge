from dnsforge_manager.application.core.manager_application import create_app
from dnsforge_manager.domain.security import AgentTrustState, certificate_fingerprint
from dnsforge_manager.infrastructure.security import JsonAgentTrustRepository
from dnsforge_manager.interfaces.api.fastapi_app import create_fastapi_app
from dnsforge_manager.interfaces.cli.main import main as manager_main
from dnsforge_manager.application.security.agent_trust_service import AgentTrustService


def test_trust_policy_evaluates_enrollment_constraints() -> None:
    app = create_app()
    enrollment = app.enroll_agent(
        {
            "hostname": "dns-pol-01",
            "version": "14.4.0",
            "profile": "authoritative",
            "site": "emea",
            "public_key": "ssh-ed25519 AAAAPOLICY dns-pol-01",
        }
    )["enrollment"]
    policy = app.create_trust_policy(
        {
            "policy_id": "authoritative-emea",
            "name": "Authoritative EMEA agents",
            "allowed_profiles": ["authoritative"],
            "allowed_sites": ["emea"],
            "require_public_key": True,
        }
    )["policy"]

    decision = app.evaluate_trust_policy(str(enrollment["request_id"]), str(policy["policy_id"]))

    assert decision["allowed"] is True
    assert app.trust_policies()["policies"][0]["policy_id"] == "authoritative-emea"


def test_trust_policy_rejects_missing_public_key() -> None:
    service = AgentTrustService()
    request = service.enroll(
        {
            "hostname": "dns-no-key",
            "version": "14.4.0",
            "profile": "proxy-forwarder",
        }
    )
    service.create_policy({"policy_id": "strict", "name": "Strict", "require_public_key": True})

    decision = service.evaluate_enrollment(request.request_id, "strict")

    assert decision["allowed"] is False


def test_token_and_certificate_rotation_history_is_persisted(tmp_path) -> None:
    repository = JsonAgentTrustRepository(tmp_path / "trust.json")
    service = AgentTrustService(trust_repository=repository)
    request = service.enroll(
        {
            "hostname": "dns-rotate",
            "version": "14.4.0",
            "profile": "authoritative",
            "public_key": "ssh-ed25519 AAAAOLD dns-rotate",
        }
    )
    approved = service.approve_enrollment(request.request_id)
    rotated = service.rotate_trusted_agent_token(approved.fingerprint, reason="scheduled")
    new_key = "ssh-ed25519 AAAANEW dns-rotate"
    cert_rotated = service.rotate_trusted_agent_certificate(rotated.fingerprint, public_key=new_key)

    records = JsonAgentTrustRepository(tmp_path / "trust.json").list_rotations()

    assert len(records) == 2
    assert all(record.previous_token_digest for record in records)
    assert any(record.certificate_rotated for record in records)
    assert cert_rotated.fingerprint == certificate_fingerprint(new_key)
    assert cert_rotated.state == AgentTrustState.APPROVED


def test_agent_trust_policy_routes_are_exposed_without_fastapi_dependency() -> None:
    api = create_fastapi_app(create_app())
    routes = set()
    for route in getattr(api, "routes", []):
        if hasattr(route, "method"):
            routes.add((route.method, route.path))
        else:
            for method in getattr(route, "methods", set()):
                routes.add((method, getattr(route, "path", "")))

    assert ("GET", "/trust/policies") in routes
    assert ("POST", "/trust/policies") in routes
    assert ("POST", "/trust/policies/evaluate") in routes
    assert ("GET", "/trust/rotations") in routes
    assert ("POST", "/trust/rotate-certificate") in routes


def test_manager_trust_policy_cli_commands_are_exposed(capsys) -> None:
    assert manager_main(["trust", "policies"]) == 0
    assert "policies" in capsys.readouterr().out

    assert manager_main(["trust", "rotations"]) == 0
    assert "rotations" in capsys.readouterr().out
