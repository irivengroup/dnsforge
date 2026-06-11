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
BACK_RECURSIVE_CLIENTS="localnets;"
EOF
PYTHONPATH="${PROJECT_ROOT}/src" python3 - <<PY
from pathlib import Path
from dnsforge.interfaces.cli.main import build_parser
from dnsforge.application.security.security_service import SecurityService
from dnsforge.domain.security.model import SecurityProfile, SecurityControls
parser=build_parser()
parser.parse_args(['security','show','--setup-file','$TMP'])
parser.parse_args(['security','audit','--setup-file','$TMP'])
assert SecurityProfile.from_value('enterprise') is SecurityProfile.ENTERPRISE
assert SecurityControls.from_profile(SecurityProfile.ENTERPRISE).rrl is True
out=SecurityService().show(Path('$TMP'))
assert 'Profile: enterprise' in out
assert 'dns_cookies: enabled' in out
PY
PYTHONPATH="${PROJECT_ROOT}/src" python3 -m dnsforge.interfaces.cli.main --project-root "${PROJECT_ROOT}" security show --setup-file "${TMP}" | grep -q 'Profile: enterprise'
echo "dnsforge security validation OK"
