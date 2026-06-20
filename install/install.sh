#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

INSTALL_ROOT="/opt/dnsforge"
CONFIG_ROOT="/etc/dnsforge"
BIN_LINK="/usr/local/bin/dnsforge"
PROFILE=""
FORCE="no"

detect_os_family() {
  if [[ ! -f /etc/os-release ]]; then echo "unknown"; return; fi
  . /etc/os-release
  local values="${ID:-} ${ID_LIKE:-}"
  case "${values,,}" in
    *rhel*|*fedora*|*rocky*|*almalinux*|*centos*) echo "redhat" ;;
    *debian*|*ubuntu*) echo "debian" ;;
    *suse*|*sles*|*opensuse*) echo "suse" ;;
    *) echo "unknown" ;;
  esac
}
bind_is_installed() {
  command -v named >/dev/null 2>&1 &&
  command -v named-checkconf >/dev/null 2>&1 &&
  command -v named-checkzone >/dev/null 2>&1 &&
  command -v rndc >/dev/null 2>&1
}
install_bind_if_missing() {
  if bind_is_installed; then echo "BIND already installed."; return; fi
  local family; family="$(detect_os_family)"
  echo "BIND not found. Installing BIND for OS family: ${family}"
  case "${family}" in
    redhat) dnf install -y bind bind-utils ;;
    debian) apt-get update; apt-get install -y bind9 bind9-utils dnsutils ;;
    suse) zypper --non-interactive install bind bind-utils ;;
    *) echo "ERROR: unsupported Linux distribution for automatic BIND installation." >&2; exit 1 ;;
  esac
  bind_is_installed || { echo "ERROR: BIND installation validation failed." >&2; exit 1; }
}


usage() {
  cat <<'EOF'
Usage:
  sudo ./install/install.sh --profile authoritative
  sudo ./install/install.sh --profile proxy-forwarder
  sudo ./install/install.sh --profile proxy-hybrid

Options:
  --profile <authoritative|proxy-forwarder|proxy-hybrid>
  --install-root <path>    Default: /opt/dnsforge
  --config-root <path>     Default: /etc/dnsforge
  --bin-link <path>        Default: /usr/local/bin/dnsforge
  --force
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile) PROFILE="${2:-}"; shift 2 ;;
    --install-root) INSTALL_ROOT="${2:-}"; shift 2 ;;
    --config-root) CONFIG_ROOT="${2:-}"; shift 2 ;;
    --bin-link) BIN_LINK="${2:-}"; shift 2 ;;
    --force) FORCE="yes"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "ERROR: unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ "${EUID}" -ne 0 ]]; then
  echo "ERROR: run as root." >&2
  exit 1
fi

case "${PROFILE}" in
  authoritative|proxy-forwarder|proxy-hybrid) ;;
  "") echo "ERROR: --profile is mandatory." >&2; usage >&2; exit 2 ;;
  *) echo "ERROR: invalid profile: ${PROFILE}" >&2; usage >&2; exit 2 ;;
esac

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

install_bind_if_missing

mkdir -p "${INSTALL_ROOT}/bin" "${CONFIG_ROOT}/dns-proxy" "${CONFIG_ROOT}/dns-authoritative" "$(dirname "${BIN_LINK}")"

if command -v rsync >/dev/null 2>&1; then
  rsync -a --delete --exclude '__pycache__/' --exclude '*.pyc' --exclude '.git/' "${SOURCE_ROOT}/" "${INSTALL_ROOT}/"
else
  rm -rf "${INSTALL_ROOT:?}/"*
  cp -a "${SOURCE_ROOT}/." "${INSTALL_ROOT}/"
  find "${INSTALL_ROOT}" -name '__pycache__' -type d -prune -exec rm -rf {} + || true
  find "${INSTALL_ROOT}" -name '*.pyc' -type f -delete || true
fi

if [[ -e "${INSTALL_ROOT}/settings" || -L "${INSTALL_ROOT}/settings" ]]; then
  [[ -L "${INSTALL_ROOT}/settings" ]] && rm -f "${INSTALL_ROOT}/settings" || mv "${INSTALL_ROOT}/settings" "${INSTALL_ROOT}/settings.backup.$(date -u +%Y%m%d%H%M%S)"
fi
ln -s "${CONFIG_ROOT}" "${INSTALL_ROOT}/settings"


SETUP_CONF="${CONFIG_ROOT}/setup.conf"
if [[ -f "${SETUP_CONF}" && "${FORCE}" != "yes" ]]; then
  echo "Keeping existing ${SETUP_CONF}; use --force to replace it."
else
  PYTHONPATH="${SOURCE_ROOT}/src${PYTHONPATH:+:${PYTHONPATH}}" PROFILE="${PROFILE}" python3 - <<'DNSFORGE_GENERATE_SETUP' > "${SETUP_CONF}"
import os
from dnsforge.domain.profile.model import ConfigurationProfile
from dnsforge.infrastructure.profile.setup_template_service import ProfileSetupTemplateService

profile = ConfigurationProfile.from_value(os.environ["PROFILE"])
node = "srv01" if profile is ConfigurationProfile.AUTHORITATIVE else "srv02"
print(ProfileSetupTemplateService().render(profile, node=node), end="")
DNSFORGE_GENERATE_SETUP
  chmod 0640 "${SETUP_CONF}"
fi

mkdir -p "${INSTALL_ROOT}/bin" "$(dirname "${BIN_LINK}")"
cat > "${INSTALL_ROOT}/bin/dnsforge-system" <<EOF
#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail
PROJECT_ROOT="${INSTALL_ROOT}"
PYTHONPATH="\${PROJECT_ROOT}/src\${PYTHONPATH:+:\${PYTHONPATH}}" exec python3 -m dnsforge.interfaces.cli.main --project-root "\${PROJECT_ROOT}" "\$@"
EOF
chmod 0755 "${INSTALL_ROOT}/bin/dnsforge-system"
ln -sfn "${INSTALL_ROOT}/bin/dnsforge-system" "${BIN_LINK}"

cat <<EOF

Installation complete.

Edit:
  ${CONFIG_ROOT}/setup.conf

Then edit the generated setup.conf to match this node:
  ${CONFIG_ROOT}/setup.conf

Then run:
  sudo dnsforge profile audit
  sudo dnsforge initialize --render-only
  sudo dnsforge initialize --apply
EOF
