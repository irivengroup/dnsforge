from __future__ import annotations

from pathlib import Path

from dnsforge.application.cluster.cluster_service import ClusterService
from dnsforge.application.sync.sync_service import SyncService
from dnsforge.domain.sync.model import ClusterSyncPlan


def _write_setup(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                'ROLE="dns-authoritative"',
                'NODE_NAME="auth01"',
                'ENABLE_CLUSTER="yes"',
                'CLUSTER_ROLE="authoritative"',
                'CLUSTER_NAME="dns-prod"',
                'PEER_AUTHORITATIVE_ADDRESSES="10.10.10.11,10.10.10.12"',
                'CLUSTER_VIP="10.10.10.100"',
                'CLUSTER_INTERFACE="eth1"',
                'CLUSTER_PRIORITY="150"',
                'CLUSTER_VRID="53"',
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def test_cluster_delegates_sync_to_sync_boundary(tmp_path: Path) -> None:
    setup_file = tmp_path / "setup.conf"
    _write_setup(setup_file)
    (tmp_path / "zones.yml").write_text("zones:\n", encoding="utf-8")

    cluster_plan = ClusterService().sync_plan(setup_file)
    sync_plan = SyncService().sync_plan(setup_file)

    assert isinstance(cluster_plan, ClusterSyncPlan)
    assert cluster_plan == sync_plan
    assert cluster_plan.peers == ["10.10.10.11", "10.10.10.12"]
