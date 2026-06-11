#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

test -f "${PROJECT_ROOT}/pyproject.toml"
test -x "${PROJECT_ROOT}/bin/dnsforge"

find "${PROJECT_ROOT}/src/dnsforge" -name '__pycache__' -type d -prune -exec rm -rf {} +
find "${PROJECT_ROOT}/src/dnsforge" -name '*.pyc' -type f -delete

# Product Python code must not depend on legacy shell runners or shell entrypoints.
if grep -RniE 'LegacyShellRunner|dnsProxyDeploy\.sh|dnsAuthoritativeDeploy\.sh|zone-manager\.sh' \
  "${PROJECT_ROOT}/src/dnsforge" >/dev/null
then
  echo "dnsforge Python product still references legacy shell code" >&2
  exit 1
fi

PYTHONPATH="${PROJECT_ROOT}/src" python3 - <<'PY'
from pathlib import Path
import tempfile

from dnsforge.interfaces.cli.main import build_parser
from dnsforge.application.initialize.initialize_planner import InitializePlanner
from dnsforge.application.initialize.initialize_service import InitializeService
from dnsforge.infrastructure.install.file_installer import FileInstaller

parser = build_parser()
parser.parse_args(["validate", "proxy", "proxy01", "--type", "forwarder"])
parser.parse_args(["render", "proxy", "proxy01", "--type", "hybrid"])
parser.parse_args(["initialize", "proxy", "proxy01", "--type", "forwarder", "--dry-run"])
parser.parse_args(["zone", "list"])

with tempfile.TemporaryDirectory() as tmp:
    render = Path(tmp) / "render"
    (render / "etc/named").mkdir(parents=True)
    (render / "etc/named.conf").write_text("// named\\n", encoding="utf-8")
    assert FileInstaller().install_tree(render, target_root=Path(tmp) / "target", dry_run=True)
    plan = InitializePlanner().build_proxy_plan("proxy01", "forwarder", render, dry_run=True, backup_before_apply=True)
    setup_file = Path(tmp) / "etc/dnsforge/setup.conf"
    InitializeService().apply(plan, setup_file=setup_file)
PY

echo "dnsforge product Python validation OK"
