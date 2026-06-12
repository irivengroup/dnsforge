from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from dnsforge.application.cluster.cluster_service import ClusterService
from dnsforge.interfaces.cli.main import build_parser

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _write_cluster_setup(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                'ROLE="dns-proxy"',
                'PROXY_TYPE="forwarder"',
                'NODE_NAME="proxy01"',
                'ENABLE_CLUSTER="yes"',
                'CLUSTER_ROLE="proxy"',
                'CLUSTER_NAME="dns-prod"',
                'CLUSTER_PEERS="proxy01,proxy02"',
                'CLUSTER_VIP="10.10.10.53"',
                'CLUSTER_INTERFACE="eth0"',
                'CLUSTER_PRIORITY="150"',
                'CLUSTER_AUTH_PASS="secret"',
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def test_cluster_parser_and_service(tmp_path: Path) -> None:
    setup_file = tmp_path / "setup.conf"
    _write_cluster_setup(setup_file)
    parser = build_parser()
    for command in (
        ["cluster", "status", "--setup-file", str(setup_file)],
        ["cluster", "validate", "--setup-file", str(setup_file)],
        ["cluster", "init", "--setup-file", str(setup_file), "--dry-run"],
        ["cluster", "sync", "--setup-file", str(setup_file), "--dry-run"],
    ):
        parser.parse_args(command)
    service = ClusterService()
    assert "Mode: proxy-vip" in service.status(setup_file)
    assert service.validate(setup_file) == "Cluster validation OK"


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
    assert "Mode: proxy-vip" in status.stdout
    validate = subprocess.run(
        [sys.executable, "-m", "dnsforge.interfaces.cli.main", "cluster", "validate", "--setup-file", str(setup_file)],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=True,
        env={**os.environ, "PYTHONPATH": str(PROJECT_ROOT / "src")},
    )
    assert "Cluster validation OK" in validate.stdout
