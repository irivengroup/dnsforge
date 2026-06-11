#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

INSTALL_ROOT="/opt/dnsforge"
CONFIG_ROOT="/etc/dnsforge"
BIN_LINK="/usr/local/bin/dnsforge"
PROFILE=""
FORCE="no"

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
TEMPLATE="${SCRIPT_DIR}/templates/${PROFILE}/setup.conf"

if [[ ! -f "${TEMPLATE}" ]]; then
  echo "ERROR: template not found: ${TEMPLATE}" >&2
  exit 1
fi

mkdir -p "${INSTALL_ROOT}" "${CONFIG_ROOT}/dns-proxy" "${CONFIG_ROOT}/dns-authoritative"

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
  install -m 0640 "${TEMPLATE}" "${SETUP_CONF}"
fi

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

Then create the node settings file:
  sudo ${INSTALL_ROOT}/install/create-node-settings.sh --role proxy --node <node>
  sudo ${INSTALL_ROOT}/install/create-node-settings.sh --role authoritative --node <node>

Then run:
  dnsforge profile audit
  dnsforge validate/render/configure.
EOF
