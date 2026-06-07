#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

BACKUP_ROOT="${BACKUP_ROOT:-/var/backups/binddns}"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_DIR="${BACKUP_ROOT}/${TIMESTAMP}"

mkdir -p "${BACKUP_DIR}"
chmod 0700 "${BACKUP_ROOT}"

copy_if_exists() {
    local source_path="$1"
    local target_dir="$2"

    if [[ -e "${source_path}" ]]
    then
        mkdir -p "${target_dir}"
        cp -a "${source_path}" "${target_dir}/"
    fi
}

copy_if_exists /etc/named.conf "${BACKUP_DIR}/etc"
copy_if_exists /etc/named "${BACKUP_DIR}/etc"
copy_if_exists /var/named "${BACKUP_DIR}/var"
copy_if_exists /var/log/named "${BACKUP_DIR}/var/log"
copy_if_exists /etc/keepalived "${BACKUP_DIR}/etc"
copy_if_exists /etc/binddns-release "${BACKUP_DIR}/etc"

find "${BACKUP_DIR}" -type d -exec chmod 0750 {} \;
find "${BACKUP_DIR}" -type f -exec chmod 0640 {} \;

tar -C "${BACKUP_ROOT}" -czf "${BACKUP_DIR}.tar.gz" "${TIMESTAMP}"
chmod 0600 "${BACKUP_DIR}.tar.gz"

printf '%s\n' "${BACKUP_DIR}.tar.gz"
