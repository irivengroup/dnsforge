#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
grep -q 'install_bind_if_missing' "${PROJECT_ROOT}/install/install.sh"
! grep -Rni -- '--skip-install' "${PROJECT_ROOT}/src/dnsforge" >/tmp/dnsforge-skip-install.txt || { cat /tmp/dnsforge-skip-install.txt; exit 1; }
PYTHONPATH="${PROJECT_ROOT}/src" python3 - <<'PY'
from dnsforge.interfaces.cli.main import build_parser
from dnsforge.infrastructure.system.distribution import LinuxDistribution
from dnsforge.infrastructure.system.package_manager import PackageManager
parser=build_parser()
parser.parse_args(["initialize"])
parser.parse_args(["initialize","--render-only"])
parser.parse_args(["initialize","--dry-run"])
parser.parse_args(["initialize","proxy","--type","forwarder","--render-only"])
parser.parse_args(["initialize","authoritative","--dry-run"])
try:
    parser.parse_args(["configure"])
except SystemExit:
    pass
else:
    raise SystemExit("configure command must not be accepted")
assert LinuxDistribution("ubuntu","debian","24.04").family=="debian"
assert LinuxDistribution("rocky","rhel fedora","9").family=="redhat"
assert LinuxDistribution("sles","suse","15").family=="suse"
assert PackageManager is not None
PY
bash "${PROJECT_ROOT}/install/install.sh" --help >/dev/null
echo "dnsforge initialize/bind install validation OK"
