#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

PYTHONPATH="${PROJECT_ROOT}/src" python3 - <<'PY'
from pathlib import Path

from dnsforge.application.initialize.initialize_planner import InitializePlanner
from dnsforge.domain.initialize.plan import InitializePlan
from dnsforge.interfaces.cli.main import build_parser

parser = build_parser()
parser.parse_args(["initialize", "proxy", "proxy01", "--type", "forwarder", "--dry-run"])
parser.parse_args(["initialize", "authoritative", "auth01", "--dry-run"])

planner = InitializePlanner()
plan = planner.build_proxy_plan("proxy01", "forwarder", Path("/tmp/render"), dry_run=True, backup_before_apply=True)
assert isinstance(plan, InitializePlan)
assert plan.dry_run is True
assert "Initialize plan" in plan.summary()
assert any(step.name == "configure firewall" for step in plan.steps)
PY

echo "dnsforge initialize plan validation OK"
