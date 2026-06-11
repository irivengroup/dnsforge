#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TMP="$(mktemp)"
trap 'rm -f "${TMP}"' EXIT
cat > "${TMP}" <<'EOF'
ROLE="dns-proxy"
PROXY_TYPE="forwarder"
SECURITY_PROFILE="enterprise"
ENABLE_RPZ="yes"
ENABLE_RRL="yes"
ENABLE_DNSSEC="yes"
BACK_RECURSIVE_CLIENTS="localnets;"
EOF

PYTHONPATH="${PROJECT_ROOT}/src" python3 - <<PY
from dnsforge.interfaces.cli.main import build_parser
p=build_parser()
p.parse_args(["status","--setup-file","$TMP"])
p.parse_args(["health","--setup-file","$TMP"])
p.parse_args(["doctor","--setup-file","$TMP"])
p.parse_args(["backup","create","--setup-file","$TMP","--dry-run"])
p.parse_args(["backup","list"])
p.parse_args(["restore","--backup","$TMP","--dry-run"])
p.parse_args(["migrate","--to","proxy-hybrid","--setup-file","$TMP","--dry-run"])
PY

PYTHONPATH="${PROJECT_ROOT}/src" python3 -m dnsforge.interfaces.cli.main status --setup-file "${TMP}" | grep -q 'Profile: proxy-forwarder'
PYTHONPATH="${PROJECT_ROOT}/src" python3 -m dnsforge.interfaces.cli.main migrate --to proxy-hybrid --setup-file "${TMP}" --dry-run | grep -q 'Would migrate'

echo "dnsforge operations validation OK"
