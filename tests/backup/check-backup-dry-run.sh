#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SANDBOX="$(mktemp -d /tmp/binddns-backup-test.XXXXXX)"
trap 'rm -rf "${SANDBOX}"' EXIT

mkdir -p "${SANDBOX}/backups"

# This test validates the script syntax without touching /etc.
bash -n "${PROJECT_ROOT}/src/tools/backup-binddns.sh"
bash -n "${PROJECT_ROOT}/src/tools/restore-binddns.sh"
bash -n "${PROJECT_ROOT}/src/tools/list-backups.sh"

echo "Backup script syntax validation OK"
