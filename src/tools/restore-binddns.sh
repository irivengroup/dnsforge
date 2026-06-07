#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

ARCHIVE="${1:-}"

if [[ -z "${ARCHIVE}" ]]
then
    echo "Usage: $0 <backup-archive.tar.gz>" >&2
    exit 1
fi

if [[ ! -f "${ARCHIVE}" ]]
then
    echo "Backup archive not found: ${ARCHIVE}" >&2
    exit 1
fi

RESTORE_TMP="$(mktemp -d /tmp/binddns-restore.XXXXXX)"
trap 'rm -rf "${RESTORE_TMP}"' EXIT

tar -C "${RESTORE_TMP}" -xzf "${ARCHIVE}"

EXTRACTED_DIR="$(find "${RESTORE_TMP}" -mindepth 1 -maxdepth 1 -type d | head -1)"

if [[ -z "${EXTRACTED_DIR}" ]]
then
    echo "Invalid backup archive: no extracted directory" >&2
    exit 1
fi

restore_if_exists() {
    local source_path="$1"
    local target_path="$2"

    if [[ -e "${source_path}" ]]
    then
        cp -a "${source_path}" "${target_path}"
    fi
}

restore_if_exists "${EXTRACTED_DIR}/etc/named.conf" /etc/named.conf
restore_if_exists "${EXTRACTED_DIR}/etc/named" /etc/
restore_if_exists "${EXTRACTED_DIR}/var/named" /var/
restore_if_exists "${EXTRACTED_DIR}/var/log/named" /var/log/
restore_if_exists "${EXTRACTED_DIR}/etc/keepalived" /etc/
restore_if_exists "${EXTRACTED_DIR}/etc/binddns-release" /etc/binddns-release

if command -v restorecon >/dev/null 2>&1
then
    restorecon -Rv /etc/named.conf /etc/named /var/named /var/log/named /etc/keepalived 2>/dev/null || true
fi

if command -v named-checkconf >/dev/null 2>&1
then
    named-checkconf -z /etc/named.conf
fi

systemctl restart named

if systemctl list-unit-files keepalived.service >/dev/null 2>&1
then
    systemctl restart keepalived || true
fi

if command -v rndc >/dev/null 2>&1
then
    rndc status || true
fi

echo "Restore completed from ${ARCHIVE}"
