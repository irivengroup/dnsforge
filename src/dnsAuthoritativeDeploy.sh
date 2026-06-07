#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LIB_DIR="${PROJECT_ROOT}/src/libs"

source "${LIB_DIR}/lib-logging.sh"
source "${LIB_DIR}/lib-bind.sh"
source "${LIB_DIR}/lib-firewall.sh"
source "${LIB_DIR}/lib-render.sh"
source "${LIB_DIR}/lib-settings-validate.sh"
source "${LIB_DIR}/lib-network.sh"
source "${LIB_DIR}/lib-inventory.sh"
source "${LIB_DIR}/lib-rndc.sh"
source "${LIB_DIR}/lib-settings-validate.sh"
source "${LIB_DIR}/lib-zone-index.sh"
source "${LIB_DIR}/lib-permissions.sh"
source "${LIB_DIR}/lib-selinux.sh"

NODE="${1:-}"
shift || true

DRY_RUN=false
RENDER_ONLY=false
VALIDATE_ONLY=false
AUDIT=false
SKIP_INSTALL=false
ROLLBACK=""

while [[ $# -gt 0 ]]
do
    case "$1" in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --render-only)
            RENDER_ONLY=true
            shift
            ;;
        --validate-only)
            VALIDATE_ONLY=true
            SKIP_INSTALL=true
            shift
            ;;
        --audit)
            AUDIT=true
            SKIP_INSTALL=true
            shift
            ;;
        --skip-install)
            SKIP_INSTALL=true
            shift
            ;;
        --rollback)
            ROLLBACK="${2:-}"
            shift 2
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

if [[ -z "${NODE}" ]]
then
    log_error "Node argument is required"
    exit 1
fi

SETTINGS_FILE="${PROJECT_ROOT}/src/settings/dns-authoritative/${NODE}.env"
RENDER_ROOT="${PROJECT_ROOT}/src/render/dns-authoritative/${NODE}"

if [[ ! -f "${SETTINGS_FILE}" ]]
then
    log_error "Inventory not found: ${SETTINGS_FILE}"
    exit 1
fi

set -o allexport
source "${SETTINGS_FILE}"
set +o allexport

ensure_rndc_secret
validate_dns_authoritative_settings_strict
validate_authoritative_inventory

log_info "Rendering authoritative DNS configuration for ${NODE}"

rm -rf "${RENDER_ROOT}"
render_common_authoritative "${RENDER_ROOT}"
generate_authoritative_zone_indexes
validate_rendered_config "${RENDER_ROOT}"

if [[ "${RENDER_ONLY}" == "true" || "${DRY_RUN}" == "true" || "${VALIDATE_ONLY}" == "true" || "${AUDIT}" == "true" ]]
then
    log_ok "Non-deploy mode completed"
    exit 0
fi

install_bind_packages
install_keepalived_package

log_info "Deploying rendered configuration to system root"

mkdir -p /var/backups/binddns
backup_dir="/var/backups/binddns/$(date +%Y%m%d-%H%M%S)"
mkdir -p "${backup_dir}"
cp -a /etc/named.conf /etc/named /var/named /etc/keepalived "${backup_dir}/" 2>/dev/null || true

cp -a "${RENDER_ROOT}/." /

apply_bind_permissions
apply_selinux_contexts
configure_authoritative_firewall

systemctl enable named
systemctl restart named

systemctl enable keepalived
systemctl restart keepalived

rndc reconfig || true
rndc status || true

cat > /etc/binddns-release <<EOF
role=dns-authoritative
node=${NODE_NAME}
version=${BINDDNS_VERSION}
deployed_at=$(date --iso-8601=seconds)
EOF

log_ok "Authoritative DNS deployment completed"
