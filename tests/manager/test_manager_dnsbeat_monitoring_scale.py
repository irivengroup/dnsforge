from __future__ import annotations

from dnsforge_manager.application.core.manager_application import create_app
from dnsforge_manager.application.dnssync.dnssync_service import DNSSyncService
from dnsforge_manager.domain.dnssync.models import DNSForgeOperation, SyncMode
from dnsforge_manager.domain.inventory.models import ManagedNode, NodeRole, NodeStatus
from dnsforge_manager.infrastructure.concurrency import ParallelExecutor, WorkerSizing
from dnsforge_manager.infrastructure.dnssync.client import RecordingDNSForgeNodeClient
from dnsforge_manager.infrastructure.persistence.postgresql.scale import MANAGER_SCALE_SQL, batched


def _node(node_id: str, *, cluster: str = "c1", status: NodeStatus = NodeStatus.ACTIVE) -> ManagedNode:
    return ManagedNode(
        node_id=node_id,
        name=node_id,
        api_endpoint=f"https://{node_id}:1073",
        role=NodeRole.AUTHORITATIVE,
        cluster_id=cluster,
        status=status,
        trust_state="approved",
    )


def test_worker_sizing_is_bounded_by_items_and_server_characteristics() -> None:
    sizing = WorkerSizing(cpu_count=8, memory_bytes=512 * 1024 * 1024, max_workers=32)

    assert sizing.for_items(0) == 0
    assert sizing.for_items(2) == 2
    assert sizing.for_items(100) == 8


def test_parallel_executor_preserves_result_order() -> None:
    executor = ParallelExecutor(WorkerSizing(cpu_count=4, max_workers=4))

    assert executor.map_ordered((1, 2, 3), lambda item: item * 10) == (10, 20, 30)


def test_dnssync_execute_fans_out_with_bounded_executor() -> None:
    service = DNSSyncService(ParallelExecutor(WorkerSizing(cpu_count=8, max_workers=8)))
    nodes = tuple(_node(f"dns{i}") for i in range(6))
    plan = service.build_cluster_plan(
        cluster_id="c1",
        operation=DNSForgeOperation("zone.sync", {"zone": "example.com"}),
        nodes=nodes,
        mode=SyncMode.APPLY,
    )
    client = RecordingDNSForgeNodeClient()

    execution = service.execute(plan, client, approved_plan_hash=plan.plan_hash)

    assert execution.accepted is True
    assert [result.node_id for result in execution.results] == [f"dns{i}" for i in range(6)]
    assert sorted(node_id for node_id, _operation in client.operations) == [f"dns{i}" for i in range(6)]


def test_manager_dnsbeat_monitoring_reports_components_and_alerts() -> None:
    app = create_app()
    app.registration_service.register_node(_node("dns01", cluster="c1", status=NodeStatus.ACTIVE))
    registered = app.registration_service.register_node(_node("dns02", cluster="c1", status=NodeStatus.UNREACHABLE))
    app.registration_service.set_status(registered.node_id, NodeStatus.UNREACHABLE)

    status = app.monitor_status()
    clusters = app.monitor_clusters()
    alerts = app.monitor_alerts()

    assert status["status"] == "FAILED"
    assert clusters["clusters"][0]["status"] == "FAILED"
    assert alerts["alerts"]
    assert {alert["component"] for alert in alerts["alerts"]} >= {"BIND", "RNDC", "DNSSEC", "Catalog"}


def test_postgresql_scale_policy_contains_large_dataset_indexes() -> None:
    joined = "\n".join(MANAGER_SCALE_SQL)

    assert "idx_agents_payload_cluster" in joined
    assert "idx_dnssync_executions_payload_plan_hash" in joined
    assert "idx_manager_audit_events_payload_target" in joined
    assert batched(tuple(range(5)), 2) == ((0, 1), (2, 3), (4,))

import asyncio
import pytest


def test_dnssync_execute_dry_run_branch_and_async_rollback() -> None:
    service = DNSSyncService(ParallelExecutor(WorkerSizing(cpu_count=4, max_workers=4)))
    nodes = (_node("dns-a"),)
    dry_plan = service.build_cluster_plan(
        cluster_id="c1",
        operation=DNSForgeOperation("zone.sync", {"zone": "example.com"}),
        nodes=nodes,
        mode=SyncMode.DRY_RUN,
    )
    dry_execution = service.execute(dry_plan, RecordingDNSForgeNodeClient())
    assert dry_execution.mode == SyncMode.DRY_RUN

    rollback_plan = service.build_cluster_plan(
        cluster_id="c1",
        operation=DNSForgeOperation("zone.sync", {"zone": "example.com"}),
        nodes=nodes,
        mode=SyncMode.ROLLBACK,
    )
    client = RecordingDNSForgeNodeClient()
    execution = asyncio.run(service.execute_async(rollback_plan, client, approved_plan_hash=rollback_plan.plan_hash))

    assert execution.accepted is True
    assert client.operations[0][1].operation == "rollback.zone.sync"


def test_dnssync_async_requires_approved_hash() -> None:
    service = DNSSyncService(ParallelExecutor(WorkerSizing(cpu_count=4, max_workers=4)))
    plan = service.build_cluster_plan(
        cluster_id="c1",
        operation=DNSForgeOperation("zone.sync", {}),
        nodes=(_node("dns-a"),),
        mode=SyncMode.APPLY,
    )

    with pytest.raises(PermissionError):
        asyncio.run(service.execute_async(plan, RecordingDNSForgeNodeClient(), approved_plan_hash="wrong"))


def test_manager_monitor_agents_and_ready_status() -> None:
    app = create_app()
    app.registration_service.register_node(_node("dns01", cluster="c1", status=NodeStatus.ACTIVE))

    agents = app.monitor_agents()
    status = app.monitor_status()
    alerts = app.monitor_alerts()

    assert status["status"] == "READY"
    assert agents["agents"][0]["components"]
    assert alerts["alerts"] == []
