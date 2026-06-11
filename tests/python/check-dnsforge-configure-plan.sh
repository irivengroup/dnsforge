#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

PYTHONPATH="${PROJECT_ROOT}/src" python3 - <<'PY'
from pathlib import Path

from dnsforge.application.configure.configure_planner import ConfigurePlanner
from dnsforge.domain.configure.plan import ConfigurePlan
from dnsforge.interfaces.cli.main import build_parser

parser = build_parser()
parser.parse_args(["configure", "proxy", "proxy01", "--type", "forwarder", "--dry-run"])
parser.parse_args(["configure", "authoritative", "auth01", "--dry-run"])

planner = ConfigurePlanner()
plan = planner.build_proxy_plan("proxy01", "forwarder", Path("/tmp/render"), dry_run=True, skip_install=False)
assert isinstance(plan, ConfigurePlan)
assert plan.dry_run is True
assert "Configure plan" in plan.summary()
assert any(step.name == "configure firewall" for step in plan.steps)
PY

echo "dnsforge configure plan validation OK"
