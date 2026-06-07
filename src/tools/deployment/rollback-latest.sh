#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

BACKUP_ROOT="${BACKUP_ROOT:-/var/backups/binddns}"

latest="$(find "${BACKUP_ROOT}" -maxdepth 1 -type f -name '*.tar.gz' -printf '%T@ %p\n' 2>/dev/null | sort -nr | awk 'NR==1 {print $2}')"

if [[ -z "${latest}" ]]
then
    echo "No backup archive found under ${BACKUP_ROOT}" >&2
    exit 1
fi

echo "Rolling back from ${latest}"
"$(dirname "${BASH_SOURCE[0]}")/../restore-binddns.sh" "${latest}"
