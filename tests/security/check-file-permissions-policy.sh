#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

grep -Rni 'chmod 0640 /etc/named.conf' "${PROJECT_ROOT}/src/libs" >/dev/null
grep -Rni 'chown root:named /etc/named.conf' "${PROJECT_ROOT}/src/libs" >/dev/null
grep -Rni 'chown -R named:named /var/named' "${PROJECT_ROOT}/src/libs" >/dev/null
grep -Rni 'restorecon -Rv' "${PROJECT_ROOT}/src/libs" >/dev/null

echo "File permission policy validation OK"
