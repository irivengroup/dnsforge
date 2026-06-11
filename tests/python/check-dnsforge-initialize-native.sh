#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

if grep -RniE 'LegacyShellRunner|dnsProxyDeploy\.sh|dnsAuthoritativeDeploy\.sh' \
  "${PROJECT_ROOT}/src/dnsforge/application/initialize" >/dev/null
then
  echo "initialize application must not call legacy bash" >&2
  exit 1
fi

PYTHONPATH="${PROJECT_ROOT}/src" python3 - <<'PY'
from pathlib import Path
import tempfile

from dnsforge.application.initialize.initialize_service import InitializeService
from dnsforge.application.initialize.initialize_planner import InitializePlanner
from dnsforge.infrastructure.install.file_installer import FileInstaller

with tempfile.TemporaryDirectory() as tmp:
    render = Path(tmp) / "render"
    target = Path(tmp) / "target"
    (render / "etc/named").mkdir(parents=True)
    (render / "etc/named.conf").write_text("// named\\n", encoding="utf-8")

    mappings = FileInstaller().install_tree(render, target_root=target, dry_run=True)
    assert mappings

    plan = InitializePlanner().build_proxy_plan("proxy01", "forwarder", render, dry_run=True, backup_before_apply=True)
    setup_file = Path(tmp) / "etc/dnsforge/setup.conf"
    InitializeService().apply(plan, setup_file=setup_file)
    assert "Initialize plan" in plan.summary()
PY

echo "dnsforge native initialize validation OK"
