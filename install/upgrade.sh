#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

INSTALL_ROOT="/opt/dnsforge"
CONFIG_ROOT="/etc/dnsforge"
BACKUP_ROOT="/var/backups/dnsforge"
BIN_LINK="/usr/local/bin/dnsforge"
WHEEL=""
FORCE="no"
DRY_RUN="no"

usage() {
  cat <<'USAGE'
Usage:
  sudo ./install/upgrade.sh --wheel dist/dnsforge-<version>-py3-none-any.whl
  sudo ./install/upgrade.sh --source

Options:
  --wheel <path>          Upgrade from a built DNSForge wheel.
  --source                Upgrade by copying the current source tree.
  --install-root <path>   Default: /opt/dnsforge
  --config-root <path>    Default: /etc/dnsforge
  --backup-root <path>    Default: /var/backups/dnsforge
  --bin-link <path>       Default: /usr/local/bin/dnsforge
  --force                 Allow reinstall/downgrade when pip would otherwise refuse.
  --dry-run               Print actions without changing the system.
USAGE
}

SOURCE_MODE="no"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --wheel) WHEEL="${2:-}"; shift 2 ;;
    --source) SOURCE_MODE="yes"; shift ;;
    --install-root) INSTALL_ROOT="${2:-}"; shift 2 ;;
    --config-root) CONFIG_ROOT="${2:-}"; shift 2 ;;
    --backup-root) BACKUP_ROOT="${2:-}"; shift 2 ;;
    --bin-link) BIN_LINK="${2:-}"; shift 2 ;;
    --force) FORCE="yes"; shift ;;
    --dry-run) DRY_RUN="yes"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "ERROR: unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ "${EUID}" -ne 0 ]]; then
  echo "ERROR: run as root." >&2
  exit 1
fi

if [[ -n "${WHEEL}" && "${SOURCE_MODE}" == "yes" ]]; then
  echo "ERROR: use either --wheel or --source, not both." >&2
  exit 2
fi

if [[ -z "${WHEEL}" && "${SOURCE_MODE}" != "yes" ]]; then
  echo "ERROR: --wheel or --source is mandatory." >&2
  usage >&2
  exit 2
fi

if [[ -n "${WHEEL}" && ! -f "${WHEEL}" ]]; then
  echo "ERROR: wheel not found: ${WHEEL}" >&2
  exit 1
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

backup_existing_installation() {
  local stamp archive
  stamp="$(date -u +%Y%m%d%H%M%S)"
  archive="${BACKUP_ROOT}/upgrade/dnsforge-upgrade-${stamp}.tar.gz"
  run mkdir -p "$(dirname "${archive}")"
  local items=()
  [[ -e "${INSTALL_ROOT}" ]] && items+=("${INSTALL_ROOT}")
  [[ -e "${CONFIG_ROOT}" ]] && items+=("${CONFIG_ROOT}")
  [[ -e "${BIN_LINK}" || -L "${BIN_LINK}" ]] && items+=("${BIN_LINK}")
  if [[ "${#items[@]}" -gt 0 ]]; then
    run tar -czf "${archive}" "${items[@]}"
    echo "Backup created: ${archive}"
  else
    echo "No existing DNSForge installation detected; skipping backup."
  fi
}

install_from_source() {
  local script_dir source_root
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  source_root="$(cd "${script_dir}/.." && pwd)"
  run mkdir -p "${INSTALL_ROOT}" "$(dirname "${BIN_LINK}")"
  if command -v rsync >/dev/null 2>&1; then
    run rsync -a --delete --exclude '__pycache__/' --exclude '*.pyc' --exclude '.git/' --exclude 'dist/' --exclude 'build/' "${source_root}/" "${INSTALL_ROOT}/"
  else
    run rm -rf "${INSTALL_ROOT:?}/"*
    run cp -a "${source_root}/." "${INSTALL_ROOT}/"
    run find "${INSTALL_ROOT}" -name '__pycache__' -type d -prune -exec rm -rf {} +
    run find "${INSTALL_ROOT}" -name '*.pyc' -type f -delete
  fi
  run mkdir -p "${INSTALL_ROOT}/bin"
  if [[ "${DRY_RUN}" != "yes" ]]; then
    cat > "${INSTALL_ROOT}/bin/dnsforge-system" <<WRAPPER
#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail
PROJECT_ROOT="${INSTALL_ROOT}"
PYTHONPATH="\${PROJECT_ROOT}/src\${PYTHONPATH:+:\${PYTHONPATH}}" exec python3 -m dnsforge.interfaces.cli.main --project-root "\${PROJECT_ROOT}" "\$@"
WRAPPER
    chmod 0755 "${INSTALL_ROOT}/bin/dnsforge-system"
    ln -sfn "${INSTALL_ROOT}/bin/dnsforge-system" "${BIN_LINK}"
  else
    echo "DRY-RUN: create ${INSTALL_ROOT}/bin/dnsforge-system and ${BIN_LINK}"
  fi
}

install_from_wheel() {
  local venv pip_bin dnsforge_bin
  venv="${INSTALL_ROOT}/venv"
  pip_bin="${venv}/bin/pip"
  dnsforge_bin="${venv}/bin/dnsforge"
  run mkdir -p "${INSTALL_ROOT}" "$(dirname "${BIN_LINK}")"
  if [[ "${DRY_RUN}" == "yes" ]]; then
    echo "DRY-RUN: python3 -m venv ${venv}"
    echo "DRY-RUN: ${pip_bin} install --upgrade${FORCE:+ --force-reinstall} ${WHEEL}"
    echo "DRY-RUN: ln -sfn ${dnsforge_bin} ${BIN_LINK}"
    return
  fi
  if [[ ! -x "${venv}/bin/python" ]]; then
    python3 -m venv "${venv}"
  fi
  "${venv}/bin/python" -m pip install --upgrade pip
  if [[ "${FORCE}" == "yes" ]]; then
    "${pip_bin}" install --upgrade --force-reinstall "${WHEEL}"
  else
    "${pip_bin}" install --upgrade "${WHEEL}"
  fi
  ln -sfn "${dnsforge_bin}" "${BIN_LINK}"
}

backup_existing_installation
if [[ -n "${WHEEL}" ]]; then
  install_from_wheel
else
  install_from_source
fi

if [[ "${DRY_RUN}" != "yes" ]]; then
  "${BIN_LINK}" --help >/dev/null
fi

echo "DNSForge upgrade complete."
