#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

CONFIG_ROOT="/etc/dnsforge"
ROLE=""
NODE=""

usage() {
  cat <<'EOF'
Usage:
  sudo ./install/create-node-settings.sh --role proxy --node proxy01
  sudo ./install/create-node-settings.sh --role authoritative --node auth01
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --role) ROLE="${2:-}"; shift 2 ;;
    --node) NODE="${2:-}"; shift 2 ;;
    --config-root) CONFIG_ROOT="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "ERROR: unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ "${EUID}" -ne 0 ]]; then
  echo "ERROR: run as root." >&2
  exit 1
fi

[[ -n "${NODE}" ]] || { echo "ERROR: --node is mandatory." >&2; exit 2; }

case "${ROLE}" in
  proxy) DEST_DIR="${CONFIG_ROOT}/dns-proxy" ;;
  authoritative) DEST_DIR="${CONFIG_ROOT}/dns-authoritative" ;;
  *) echo "ERROR: --role must be proxy or authoritative." >&2; exit 2 ;;
esac

SETUP_CONF="${CONFIG_ROOT}/setup.conf"
[[ -f "${SETUP_CONF}" ]] || { echo "ERROR: ${SETUP_CONF} not found." >&2; exit 1; }

mkdir -p "${DEST_DIR}"
install -m 0640 "${SETUP_CONF}" "${DEST_DIR}/${NODE}.env"
echo "Created ${DEST_DIR}/${NODE}.env"
