#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "${TMP}"' EXIT
SETUP="${TMP}/setup.conf"
cat > "${SETUP}" <<'EOF'
ROLE="dns-proxy"
PROXY_TYPE="forwarder"
ENABLE_DNSSEC="yes"
ENABLE_RPZ="yes"
SECURITY_PROFILE="enterprise"
NODE_NAME="proxy01"
ENABLE_CLUSTER="yes"
CLUSTER_ROLE="proxy"
CLUSTER_PEERS="proxy01,proxy02"
CLUSTER_VIP="10.10.10.53"
CLUSTER_INTERFACE="eth0"
EOF
PYTHONPATH="${PROJECT_ROOT}/src" python3 - <<PY
from dnsforge.interfaces.cli.main import build_parser
p=build_parser()
for cmd in [
['security','history'],['security','rollback','--version','1'],
['acl','--state-file','$TMP/acls.json','list'],['acl','--state-file','$TMP/acls.json','create','internal'],['acl','--state-file','$TMP/acls.json','add-network','internal','10.0.0.0/8'],
['view','--state-file','$TMP/views.json','list'],['view','--state-file','$TMP/views.json','create','internal'],['view','--state-file','$TMP/views.json','attach-zone','internal','example.com'],
['dnssec','--setup-file','$SETUP','status'],['dnssec','--setup-file','$SETUP','validate'],['dnssec','rotate-ksk'],['dnssec','rotate-zsk'],['dnssec','check-expiry'],
['rpz','--setup-file','$SETUP','status'],['rpz','enable'],['rpz','update'],['rpz','test','bad-domain.test'],
['cluster','validate-security','--setup-file','$SETUP'],
]:
    p.parse_args(cmd)
PY
PYTHONPATH="${PROJECT_ROOT}/src" python3 -m dnsforge.interfaces.cli.main acl --state-file "${TMP}/acls.json" create internal | grep -q 'ACL created'
PYTHONPATH="${PROJECT_ROOT}/src" python3 -m dnsforge.interfaces.cli.main acl --state-file "${TMP}/acls.json" add-network internal 10.0.0.0/8 | grep -q 'Network added'
PYTHONPATH="${PROJECT_ROOT}/src" python3 -m dnsforge.interfaces.cli.main view --state-file "${TMP}/views.json" create internal | grep -q 'View created'
PYTHONPATH="${PROJECT_ROOT}/src" python3 -m dnsforge.interfaces.cli.main dnssec --setup-file "${SETUP}" status | grep -q 'DNSSEC'
PYTHONPATH="${PROJECT_ROOT}/src" python3 -m dnsforge.interfaces.cli.main rpz --setup-file "${SETUP}" status | grep -q 'RPZ'
PYTHONPATH="${PROJECT_ROOT}/src" python3 -m dnsforge.interfaces.cli.main cluster validate-security --setup-file "${SETUP}" | grep -q 'Cluster security'
echo "dnsforge security commands validation OK"
