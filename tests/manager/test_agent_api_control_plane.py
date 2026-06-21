from __future__ import annotations

import json

import pytest

from dnsforge_manager.application.agent_control.agent_api_service import AgentApiControlService
from dnsforge_manager.application.core.manager_application import create_app
from dnsforge_manager.domain.agent_control.models import AgentApiAction, AgentApiCommand
from dnsforge_manager.domain.inventory import ManagedNode, NodeRole
from dnsforge_manager.infrastructure.agent_control.client import RecordingAgentApiClient
from dnsforge_manager.interfaces.cli.main import main
from dnsforge_manager.interfaces.api.fastapi_app import create_fastapi_app


def _register_approved_node(app: object, node_id: str = "dns01", cluster_id: str = "cluster-a") -> None:
    app.register_node(  # type: ignore[attr-defined]
        {
            "node_id": node_id,
            "name": node_id,
            "api_endpoint": f"https://{node_id}:1073",
            "role": "authoritative",
            "cluster_id": cluster_id,
        }
    )
    app.approve_node(node_id)  # type: ignore[attr-defined]
    app.set_node_status(node_id, "active")  # type: ignore[attr-defined]


def test_agent_api_command_preserves_audit_and_idempotency_fields() -> None:
    command = AgentApiCommand.from_payload(
        {
            "action": "zone",
            "operation": "zone.list",
            "payload": {"format": "json"},
            "request_id": "req-1",
            "idempotency_key": "idem-1",
        }
    )
    assert command.action == AgentApiAction.ZONE
    assert command.request_id == "req-1"
    assert command.idempotency_key == "idem-1"
    assert command.payload == {"format": "json"}


def test_agent_control_rejects_unapproved_nodes() -> None:
    service = AgentApiControlService(RecordingAgentApiClient())
    node = ManagedNode("dns01", "dns01", "https://dns01:1073", NodeRole.AUTHORITATIVE, trust_state="pending")
    command = AgentApiCommand.from_payload({"action": "status", "operation": "status"})
    with pytest.raises(PermissionError):
        service.execute(node, command)


def test_manager_executes_agent_api_command_through_registered_agent() -> None:
    client = RecordingAgentApiClient()
    app = create_app()
    app.agent_api_control = AgentApiControlService(client)  # type: ignore[attr-defined]
    _register_approved_node(app)
    response = app.agent_execute(  # type: ignore[attr-defined]
        "dns01",
        {
            "action": "network",
            "operation": "network.preview",
            "payload": {"format": "json"},
            "request_id": "req-network",
            "idempotency_key": "idem-network",
        },
    )
    assert response["result"]["accepted"] is True
    assert client.calls[0][0].node_id == "dns01"
    assert client.calls[0][1].operation == "network.preview"


def test_manager_executes_cluster_agent_api_command_with_bounded_fanout() -> None:
    client = RecordingAgentApiClient()
    app = create_app()
    app.agent_api_control = AgentApiControlService(client)  # type: ignore[attr-defined]
    _register_approved_node(app, "dns01")
    _register_approved_node(app, "dns02")
    response = app.agent_execute_cluster(  # type: ignore[attr-defined]
        "cluster-a",
        {"action": "config", "operation": "config.verify", "payload": {}},
    )
    assert [result["node_id"] for result in response["results"]] == ["dns01", "dns02"]
    assert len(client.calls) == 2


def test_manager_agent_api_routes_exist_without_fastapi() -> None:
    api = create_fastapi_app()
    paths = {getattr(route, "path", "") for route in getattr(api, "routes", [])}
    assert "/agents/{node_id}/execute" in paths
    assert "/agents/clusters/{cluster_id}/execute" in paths


def test_manager_agent_cli_dispatch_executes_command(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    app = create_app()
    _register_approved_node(app)
    monkeypatch.setattr("dnsforge_manager.interfaces.cli.main.create_app", lambda: app)
    rc = main(
        [
            "agent",
            "execute",
            "--node-id",
            "dns01",
            "--action",
            "status",
            "--operation",
            "status",
            "--payload",
            json.dumps({}),
            "--request-id",
            "req-cli",
        ]
    )
    assert rc == 0
    assert json.loads(capsys.readouterr().out)["result"]["request_id"] == "req-cli"
