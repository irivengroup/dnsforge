#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

if grep -RniE 'LegacyShellRunner|dnsProxyDeploy\.sh|dnsAuthoritativeDeploy\.sh' \
  "${PROJECT_ROOT}/src/dnsforge/application/configure" >/dev/null
then
  echo "configure application must not call legacy bash" >&2
  exit 1
fi

PYTHONPATH="${PROJECT_ROOT}/src" python3 - <<'PY'
from pathlib import Path
import tempfile

from dnsforge.application.configure.configure_service import ConfigureService
from dnsforge.application.configure.configure_planner import ConfigurePlanner
from dnsforge.infrastructure.install.file_installer import FileInstaller

with tempfile.TemporaryDirectory() as tmp:
    render = Path(tmp) / "render"
    target = Path(tmp) / "target"
    (render / "etc/named").mkdir(parents=True)
    (render / "etc/named.conf").write_text("// named\\n", encoding="utf-8")

    mappings = FileInstaller().install_tree(render, target_root=target, dry_run=True)
    assert mappings

    plan = ConfigurePlanner().build_proxy_plan("proxy01", "forwarder", render, dry_run=True, skip_install=False)
    ConfigureService().apply(plan)
    assert "Configure plan" in plan.summary()
PY

echo "dnsforge native configure validation OK"
