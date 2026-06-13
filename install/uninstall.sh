#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

INSTALL_ROOT="/opt/dnsforge"
CONFIG_ROOT="/etc/dnsforge"
BACKUP_ROOT="/var/backups/dnsforge"
BIN_LINK="/usr/local/bin/dnsforge"
PURGE="no"
REMOVE_BIND="no"
DRY_RUN="no"

usage() {
  cat <<'USAGE'
Usage:
  sudo ./install/uninstall.sh
  sudo ./install/uninstall.sh --purge
  sudo ./install/uninstall.sh --purge --remove-bind

Options:
  --install-root <path>   Default: /opt/dnsforge
  --config-root <path>    Default: /etc/dnsforge
  --backup-root <path>    Default: /var/backups/dnsforge
  --bin-link <path>       Default: /usr/local/bin/dnsforge
  --purge                 Remove DNSForge configuration after a final backup.
  --remove-bind           Remove BIND packages. Requires --purge.
  --dry-run               Print actions without changing the system.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --install-root) INSTALL_ROOT="${2:-}"; shift 2 ;;
    --config-root) CONFIG_ROOT="${2:-}"; shift 2 ;;
    --backup-root) BACKUP_ROOT="${2:-}"; shift 2 ;;
    --bin-link) BIN_LINK="${2:-}"; shift 2 ;;
    --purge) PURGE="yes"; shift ;;
    --remove-bind) REMOVE_BIND="yes"; shift ;;
    --dry-run) DRY_RUN="yes"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "ERROR: unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ "${EUID}" -ne 0 ]]; then
  echo "ERROR: run as root." >&2
  exit 1
fi

if [[ "${REMOVE_BIND}" == "yes" && "${PURGE}" != "yes" ]]; then
  echo "ERROR: --remove-bind requires --purge." >&2
  exit 2
fi

run() {
  if [[ "${DRY_RUN}" == "yes" ]]; then
    printf 'DRY-RUN: '
    printf '%q ' "$@"
    printf '\n'
  else
    "$@"
  fi
}

backup_before_uninstall() {
  local stamp archive items=()
  stamp="$(date -u +%Y%m%d%H%M%S)"
  archive="${BACKUP_ROOT}/uninstall/dnsforge-uninstall-${stamp}.tar.gz"
  [[ -e "${INSTALL_ROOT}" ]] && items+=("${INSTALL_ROOT}")
  [[ -e "${CONFIG_ROOT}" ]] && items+=("${CONFIG_ROOT}")
  [[ -e "${BIN_LINK}" || -L "${BIN_LINK}" ]] && items+=("${BIN_LINK}")
  if [[ "${#items[@]}" -eq 0 ]]; then
    echo "No DNSForge files found to backup."
    return
  fi
  run mkdir -p "$(dirname "${archive}")"
  run tar -czf "${archive}" "${items[@]}"
  echo "Final backup created: ${archive}"
}

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

remove_bind_packages() {
  local family
  family="$(detect_os_family)"
  case "${family}" in
    redhat) run dnf remove -y bind bind-utils ;;
    debian) run apt-get remove -y bind9 bind9-utils dnsutils ;;
    suse) run zypper --non-interactive remove bind bind-utils ;;
    *) echo "ERROR: unsupported Linux distribution for BIND package removal." >&2; exit 1 ;;
  esac
}

backup_before_uninstall

run rm -f "${BIN_LINK}"
run rm -rf "${INSTALL_ROOT}"

if [[ "${PURGE}" == "yes" ]]; then
  run rm -rf "${CONFIG_ROOT}"
else
  echo "Keeping DNSForge configuration: ${CONFIG_ROOT}"
fi

if [[ "${REMOVE_BIND}" == "yes" ]]; then
  remove_bind_packages
else
  echo "Keeping BIND packages and native BIND configuration."
fi

echo "DNSForge uninstall complete."
