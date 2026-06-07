#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

test -x "${PROJECT_ROOT}/src/tools/backup-binddns.sh"
test -x "${PROJECT_ROOT}/src/tools/restore-binddns.sh"
test -x "${PROJECT_ROOT}/src/tools/list-backups.sh"

grep -q '/etc/named.conf' "${PROJECT_ROOT}/src/tools/backup-binddns.sh"
grep -q '/var/named' "${PROJECT_ROOT}/src/tools/backup-binddns.sh"
grep -q 'named-checkconf' "${PROJECT_ROOT}/src/tools/restore-binddns.sh"
grep -q 'systemctl restart named' "${PROJECT_ROOT}/src/tools/restore-binddns.sh"

echo "Backup tooling validation OK"
