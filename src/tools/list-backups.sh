#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

BACKUP_ROOT="${BACKUP_ROOT:-/var/backups/binddns}"

if [[ ! -d "${BACKUP_ROOT}" ]]
then
    echo "No backup directory found: ${BACKUP_ROOT}"
    exit 0
fi

find "${BACKUP_ROOT}" -maxdepth 1 -type f -name '*.tar.gz' -printf '%TY-%Tm-%Td %TH:%TM %p\n' | sort
