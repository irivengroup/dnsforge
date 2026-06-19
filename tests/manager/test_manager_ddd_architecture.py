from __future__ import annotations

from dnsforge_manager.application.core.manager_application import create_app as legacy_create_app
from dnsforge_manager.application.core.manager_application import ManagerApplication, create_app
from dnsforge_manager.application.dnssync.dnssync_service import DNSSyncService
from dnsforge_manager.application.inventory.node_registration_service import NodeRegistrationService
from dnsforge_manager.domain.core import DNSFORGE_MANAGER_BOUNDARY
from dnsforge_manager.domain.dnssync import DNSForgeOperation, SyncMode
from dnsforge_manager.domain.inventory import ManagedNode, NodeRole
from dnsforge_manager.infrastructure.dnssync import RecordingDNSForgeNodeClient


def test_manager_public_app_is_now_application_layer() -> None:
    app = create_app()
    assert isinstance(app, ManagerApplication)
    assert app.health()["component"] == "dnsforge-manager"


def test_legacy_manager_import_paths_are_removed_after_ddd_cleanup() -> None:
    from pathlib import Path

    manager_root = Path("src/dnsforge_manager")
    legacy_roots = {"api", "audit", "core", "dnsbeat", "dnssync", "inventory", "rbac", "security", "workflows"}
    present = {path.name for path in manager_root.iterdir() if path.is_dir()}
    assert legacy_roots.isdisjoint(present)


def test_manager_domain_boundary_still_forbids_direct_bind_modification() -> None:
    assert DNSFORGE_MANAGER_BOUNDARY.requires_bind is False
    assert DNSFORGE_MANAGER_BOUNDARY.may_modify_bind_files is False


def test_dnssync_ddd_path_still_requires_approved_dry_run_hash() -> None:
    node = ManagedNode(
        "dns01",
        "dns01",
        "https://dns01.example.net:1073",
        NodeRole.AUTHORITATIVE,
        cluster_id="cluster-a",
        trust_state="approved",
    )
    plan = DNSSyncService().build_cluster_plan(
        cluster_id="cluster-a",
        operation=DNSForgeOperation(operation="zone.create", payload={"zone": "example.com"}),
        nodes=(node,),
        mode=SyncMode.APPLY,
    )
    client = RecordingDNSForgeNodeClient()
    dry_run = DNSSyncService().dry_run(plan)
    result = DNSSyncService().execute(plan, client, approved_plan_hash=dry_run.plan_hash)
    assert result.accepted is True
    assert client.operations[0][0] == "dns01"
