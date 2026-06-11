#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export PYTHONPATH="${PROJECT_ROOT}/src"
cd "${PROJECT_ROOT}"
test ! -d "${PROJECT_ROOT}/src/dnsforge/infrastructure/build"
test -d "${PROJECT_ROOT}/src/dnsforge/infrastructure/bind/rendering"
python3 - <<'PY'
from dnsforge.infrastructure.filesystem.paths import ProjectPaths
from dnsforge.infrastructure.bind.rendering import TemplateRegistry
paths = ProjectPaths()
assert str(paths.catalog_file).endswith('/etc/dnsforge/zones.yml'), paths.catalog_file
assert 'named.conf' in TemplateRegistry.keys()
assert 'views' in TemplateRegistry.keys()
PY
