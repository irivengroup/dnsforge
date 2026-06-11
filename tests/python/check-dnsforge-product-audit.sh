#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

PYTHONPATH="${PROJECT_ROOT}/src" python3 - <<'PY'
from pathlib import Path
from dnsforge.application.audit.product_auditor import ProductAuditor
from dnsforge.interfaces.cli.main import build_parser

parser = build_parser()
parser.parse_args(["audit"])
parser.parse_args(["audit", "--strict"])

report = ProductAuditor().audit(Path.cwd())
assert report.ok, report.render()
assert "Product audit OK" in report.render()
PY

PYTHONPATH="${PROJECT_ROOT}/src" python3 -m dnsforge.interfaces.cli.main \
  --project-root "${PROJECT_ROOT}" audit | grep -q 'Product audit OK'

echo "dnsforge product audit validation OK"
