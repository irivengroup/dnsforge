#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

test ! -d "${PROJECT_ROOT}/src/build"
test -d "${PROJECT_ROOT}/src/dnsforge/infrastructure/build"
test -f "${PROJECT_ROOT}/src/dnsforge/infrastructure/build/catalog/zones.yml"

PYTHONPATH="${PROJECT_ROOT}/src" python3 - <<'PY'
from pathlib import Path
from dnsforge.infrastructure.filesystem.paths import ProjectPaths

paths = ProjectPaths(Path.cwd())
assert str(paths.build_root).endswith("src/dnsforge/infrastructure/build")
assert str(paths.catalog_file).endswith("src/dnsforge/infrastructure/build/catalog/zones.yml")
assert paths.catalog_file.exists()
PY

echo "dnsforge build context validation OK"
