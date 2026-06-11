#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

PYTHONPATH="${PROJECT_ROOT}/src" python3 - <<'PY'
from pathlib import Path
import re
root=Path.cwd()
settings=root/"src/settings"
assign=re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)=")
def vars_in(path):
    if not path.exists(): return set()
    out=set()
    for line in path.read_text(encoding="utf-8").splitlines():
        m=assign.match(line)
        if m: out.add(m.group(1))
    return out
proxy=set(); auth=set(); other=set()
if settings.exists():
    for p in list(settings.rglob("*.env"))+list(settings.rglob("*.conf"))+list(settings.rglob("*.cfg")):
        rel=str(p.relative_to(settings)).lower()
        vals=vars_in(p)
        if "proxy" in rel: proxy |= vals
        elif "authoritative" in rel or "auth" in rel: auth |= vals
        else: other |= vals
proxy |= other; auth |= other
proxy_tpl = vars_in(root/"install/templates/proxy-forwarder/setup.conf") | vars_in(root/"install/templates/proxy-hybrid/setup.conf")
auth_tpl = vars_in(root/"install/templates/authoritative/setup.conf")
missing_proxy=sorted(proxy - proxy_tpl)
missing_auth=sorted(auth - auth_tpl)
assert not missing_proxy, missing_proxy
assert not missing_auth, missing_auth
assert (root/"install/templates/VARIABLE-COVERAGE.md").exists()
PY
echo "dnsforge setup template coverage validation OK"
