#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

PYTHONPATH="${PROJECT_ROOT}/src" python3 - <<'PY'
from pathlib import Path
import tempfile

from dnsforge.infrastructure.initialize.state_store import InitializeAlreadyAppliedError, InitializeStateStore
from dnsforge.interfaces.cli.main import build_parser

parser = build_parser()
parser.parse_args(["initialize", "--render-only"])
parser.parse_args(["initialize", "--apply"])
parser.parse_args(["initialize", "authoritative", "local", "--render-only"])
parser.parse_args(["initialize", "authoritative", "local", "--apply"])
parser.parse_args(["initialize", "proxy", "local", "--type", "forwarder", "--render-only"])
parser.parse_args(["initialize", "proxy", "local", "--type", "forwarder", "--apply"])

with tempfile.TemporaryDirectory() as tmp:
    setup_file = Path(tmp) / "etc/dnsforge/setup.conf"
    setup_file.parent.mkdir(parents=True)
    setup_file.write_text("ROLE=authoritative\nNODE_NAME=local\n", encoding="utf-8")

    store = InitializeStateStore()
    assert store.is_initialized(setup_file) is False
    store.mark_initialized(setup_file, role="authoritative", node="local")
    assert store.is_initialized(setup_file) is True

    try:
        store.assert_not_initialized(setup_file)
    except InitializeAlreadyAppliedError as exc:
        assert "already initialized" in str(exc)
    else:
        raise AssertionError("initialize one-shot lock did not block second attempt")

    assert "DNSFORGE_INITIALIZED" not in setup_file.read_text(encoding="utf-8")
    lock_file = setup_file.parent / ".initialized.conf.lock"
    data = lock_file.read_text(encoding="utf-8")
    assert "INITIALIZED=true" in data
    assert "INITIALIZED_AT=" in data
    assert "INITIALIZED_ROLE=authoritative" in data
    assert "INITIALIZED_NODE=local" in data
PY

echo "dnsforge initialize one-shot validation OK"
