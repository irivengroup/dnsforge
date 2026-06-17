from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from dnsforge.application.cluster.cluster_service import ClusterService
from dnsforge.interfaces.cli.main import build_parser
from dnsforge.shared.errors import SettingsError

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _write_cluster_setup(path: Path, peers: str = "10.10.10.11,10.10.10.12") -> None:
    path.write_text(
        "\n".join(
            [
                'ROLE="dns-authoritative"',
                'NODE_NAME="auth01"',
                'ENABLE_CLUSTER="yes"',
                'CLUSTER_ROLE="authoritative"',
                'CLUSTER_NAME="dns-prod"',
                f'CLUSTER_PEERS="{peers}"',
                'CLUSTER_VIP="10.10.10.100"',
                'CLUSTER_INTERFACE="eth1"',
                'CLUSTER_PRIORITY="150"',
                'CLUSTER_VRID="53"',
                'CLUSTER_AUTH_PASS="secret"',
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def test_cluster_parser_and_service_supports_two_or_more_nodes(tmp_path: Path) -> None:
    setup_file = tmp_path / "setup.conf"
    _write_cluster_setup(setup_file)
    parser = build_parser()
    for command in (
        ["cluster", "status", "--setup-file", str(setup_file)],
        ["cluster", "validate", "--setup-file", str(setup_file)],
        ["cluster", "init", "--setup-file", str(setup_file), "--dry-run"],
        ["cluster", "render", "--setup-file", str(setup_file), "--reason", "Render HA cluster", "--dry-run"],
        ["cluster", "apply", "--setup-file", str(setup_file), "--reason", "Apply HA cluster", "--dry-run"],
        ["cluster", "sync", "--setup-file", str(setup_file), "--reason", "Sync HA cluster", "--dry-run"],
    ):
        parser.parse_args(command)
    service = ClusterService()
    status = service.status(setup_file)
    assert "Mode: authoritative-ha" in status
    assert "Nodes: 3" in status
    assert service.validate(setup_file) == "Cluster validation OK"


def test_cluster_keepalived_render_contains_all_peers(tmp_path: Path) -> None:
    setup_file = tmp_path / "setup.conf"
    _write_cluster_setup(setup_file, peers="10.10.10.11,10.10.10.12,10.10.10.13")
    rendered = ClusterService().render(setup_file, "Render cluster with four nodes", dry_run=True)
    assert "vrrp_instance DNSFORGE_AUTHORITATIVE" in rendered
    assert "virtual_router_id 53" in rendered
    assert "10.10.10.100" in rendered
    assert "10.10.10.11" in rendered
    assert "10.10.10.12" in rendered
    assert "10.10.10.13" in rendered


def test_cluster_cli(tmp_path: Path) -> None:
    setup_file = tmp_path / "setup.conf"
    _write_cluster_setup(setup_file)
    status = subprocess.run(
        [sys.executable, "-m", "dnsforge.interfaces.cli.main", "cluster", "status", "--setup-file", str(setup_file)],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=True,
        env={**os.environ, "PYTHONPATH": str(PROJECT_ROOT / "src")},
    )
    assert "Mode: authoritative-ha" in status.stdout
    validate = subprocess.run(
        [sys.executable, "-m", "dnsforge.interfaces.cli.main", "cluster", "validate", "--setup-file", str(setup_file)],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=True,
        env={**os.environ, "PYTHONPATH": str(PROJECT_ROOT / "src")},
    )
    assert "Cluster validation OK" in validate.stdout


def test_proxy_cluster_is_rejected(tmp_path: Path) -> None:
    setup_file = tmp_path / "setup.conf"
    setup_file.write_text(
        "\n".join(
            [
                'ROLE="dns-proxy"',
                'PROXY_TYPE="hybrid"',
                'NODE_NAME="proxy01"',
                'ENABLE_CLUSTER="yes"',
                'CLUSTER_ROLE="authoritative"',
                'CLUSTER_PEERS="proxy02"',
                'CLUSTER_VIP="10.10.10.100"',
                'CLUSTER_INTERFACE="eth1"',
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    with pytest.raises(SettingsError):
        ClusterService().validate(setup_file)


def test_cluster_requires_vip_interface_and_peer(tmp_path: Path) -> None:
    setup_file = tmp_path / "setup.conf"
    setup_file.write_text(
        "\n".join(
            [
                'ROLE="dns-authoritative"',
                'NODE_NAME="auth01"',
                'ENABLE_CLUSTER="yes"',
                'CLUSTER_ROLE="authoritative"',
                'CLUSTER_PEERS=""',
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    with pytest.raises(SettingsError):
        ClusterService().validate(setup_file)


def test_cluster_peers_diff_and_sync_plan(tmp_path: Path) -> None:
    setup_file = tmp_path / "setup.conf"
    _write_cluster_setup(setup_file, peers="10.10.10.11,10.10.10.12")
    (tmp_path / "zones.yml").write_text(
        """
zones:

  - name: example.com
    type: master
    managed_reverse: no
    description: Public zone
    business_owner: Network
    technical_owner: DNS
    environment: prod
    classification: public
    lifecycle: active
    enabled: yes
    views:
      - external
    acl:
      external: any;
    records:
""".strip()
        + "\n",
        encoding="utf-8",
    )
    service = ClusterService()

    peers = service.peers(setup_file)
    assert "10.10.10.11" in peers
    assert "unknown" in peers

    diff = service.diff(setup_file)
    assert "reachability" in diff

    dry_run = service.sync(setup_file, "Dry run authoritative sync", dry_run=True)
    assert "Authoritative HA cluster sync dry-run" in dry_run
    assert "Zones: 1" in dry_run

    result = service.sync(setup_file, "Apply authoritative sync", dry_run=False)
    assert "Authoritative HA cluster sync completed" in result
    assert (tmp_path / "cluster-sync" / "outbox" / "auth01.manifest").exists()


def test_cluster_known_peer_manifest_diff_ok(tmp_path: Path) -> None:
    setup_file = tmp_path / "setup.conf"
    _write_cluster_setup(setup_file, peers="10.10.10.11")
    (tmp_path / "zones.yml").write_text("zones:\n", encoding="utf-8")
    peer_dir = tmp_path / "cluster-sync" / "peers"
    peer_dir.mkdir(parents=True)
    (peer_dir / "10.10.10.11.manifest").write_text(
        "zone_count=0\ncatalog_serial=local\ndnssec_state=aligned\n",
        encoding="utf-8",
    )

    service = ClusterService()
    assert "known" in service.peers(setup_file)
    assert service.diff(setup_file) == "Cluster diff OK"
