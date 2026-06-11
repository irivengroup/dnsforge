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
NODE_NAME="proxy01"
ENABLE_CLUSTER="yes"
CLUSTER_ROLE="proxy"
CLUSTER_NAME="dns-prod"
CLUSTER_PEERS="proxy01,proxy02"
CLUSTER_VIP="10.10.10.53"
CLUSTER_INTERFACE="eth0"
CLUSTER_PRIORITY="150"
CLUSTER_AUTH_PASS="secret"
EOF

PYTHONPATH="${PROJECT_ROOT}/src" python3 - <<PY
from pathlib import Path
from dnsforge.interfaces.cli.main import build_parser
from dnsforge.application.cluster.cluster_service import ClusterService
p=build_parser()
p.parse_args(["cluster","status","--setup-file","$TMP"])
p.parse_args(["cluster","validate","--setup-file","$TMP"])
p.parse_args(["cluster","init","--setup-file","$TMP","--dry-run"])
p.parse_args(["cluster","sync","--setup-file","$TMP","--dry-run"])
service=ClusterService()
assert "Mode: proxy-vip" in service.status(Path("$TMP"))
assert service.validate(Path("$TMP")) == "Cluster validation OK"
PY

PYTHONPATH="${PROJECT_ROOT}/src" python3 -m dnsforge.interfaces.cli.main cluster status --setup-file "${TMP}" | grep -q 'Mode: proxy-vip'
PYTHONPATH="${PROJECT_ROOT}/src" python3 -m dnsforge.interfaces.cli.main cluster validate --setup-file "${TMP}" | grep -q 'Cluster validation OK'
echo "dnsforge cluster validation OK"
