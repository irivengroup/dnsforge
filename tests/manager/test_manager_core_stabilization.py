from __future__ import annotations

from dnsforge_manager.application.core.manager_application import create_app
from dnsforge_manager.domain.inventory import INVENTORY_ROLES, Agent, NodeRole
from dnsforge_manager.domain.rbac import MANAGER_APPROVER_ROLE, MANAGER_AUDITOR_ROLE, MANAGER_ROLES
from dnsforge_manager.interfaces.cli.main import main


def test_inventory_roles_cover_enterprise_bind_topologies() -> None:
    role_ids = {role.role_id for role in INVENTORY_ROLES}

    assert role_ids == {
        "authoritative",
        "proxy-forwarder",
        "proxy-hybrid",
        "catalog-publisher",
        "catalog-subscriber",
        "hidden-master",
        "stealth-secondary",
    }


def test_agent_role_round_trip_and_profile_default() -> None:
    agent = Agent.from_dict(
        {
            "fingerprint": "fp-1",
            "hostname": "ns01",
            "version": "14.9.0",
            "profile": "catalog-publisher",
            "status": "READY",
        }
    )

    assert agent.role == NodeRole.CATALOG_PUBLISHER
    assert agent.to_dict()["role"] == "catalog-publisher"


def test_manager_inventory_roles_api_shape() -> None:
    app = create_app()

    response = app.inventory_roles()

    assert response["roles"]
    assert any(role["role_id"] == "hidden-master" for role in response["roles"])


def test_manager_inventory_agent_register_accepts_explicit_role() -> None:
    app = create_app()

    response = app.register_inventory_agent(
        {
            "fingerprint": "fp-2",
            "hostname": "hidden-master-01",
            "version": "14.9.0",
            "profile": "authoritative",
            "role": "hidden-master",
            "status": "READY",
        }
    )

    assert response["agent"]["role"] == "hidden-master"


def test_manager_rbac_includes_approver_and_auditor_roles() -> None:
    roles = {role.name: role for role in MANAGER_ROLES}

    assert "approver" in roles
    assert "auditor" in roles
    assert MANAGER_APPROVER_ROLE.allows("manager:trust:approve")
    assert MANAGER_APPROVER_ROLE.allows("manager:sync:admin")
    assert MANAGER_AUDITOR_ROLE.allows("manager:audit:read")
    assert not MANAGER_AUDITOR_ROLE.allows("manager:nodes:operate")


def test_manager_inventory_role_cli_lists_roles(capsys) -> None:  # type: ignore[no-untyped-def]
    assert main(["inventory", "role", "list"]) == 0

    output = capsys.readouterr().out
    assert "catalog-subscriber" in output
    assert "stealth-secondary" in output
