#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

PYTHONPATH="${PROJECT_ROOT}/src" python3 - <<'PY'
from dnsforge.interfaces.cli.main import build_parser
from dnsforge.domain.model.proxy_type import ProxyType

parser = build_parser()

parser.parse_args(["validate", "proxy", "proxy01", "--type", "forwarder"])
parser.parse_args(["validate", "proxy", "proxy01", "--type", "hybrid"])
parser.parse_args(["validate", "authoritative", "auth01"])
parser.parse_args(["render", "proxy", "proxy01", "--type", "forwarder"])
parser.parse_args(["render", "authoritative", "auth01"])
parser.parse_args(["configure", "proxy", "proxy01", "--type", "forwarder", "--render-only"])
parser.parse_args(["configure", "proxy", "proxy01", "--type", "forwarder", "--dry-run"])
parser.parse_args(["configure", "authoritative", "auth01", "--render-only"])
parser.parse_args(["configure", "authoritative", "auth01", "--dry-run"])
parser.parse_args(["zone", "list"])
parser.parse_args(["zone", "get", "--name", "example.com"])
parser.parse_args(["zone", "create", "--name", "example.com", "--type", "master", "--views", "external,internal"])
parser.parse_args(["zone", "disable", "--name", "example.com"])
parser.parse_args(["zone", "enable", "--name", "example.com"])
parser.parse_args(["zone", "delete", "--name", "example.com"])

try:
    parser.parse_args(["configure", "proxy", "proxy01"])
except SystemExit as exc:
    assert exc.code != 0
else:
    raise SystemExit("proxy type must be mandatory")

assert ProxyType.choices() == ["forwarder", "hybrid"]
PY

test -x "${PROJECT_ROOT}/bin/dnsforge"

echo "dnsforge CLI validation OK"
