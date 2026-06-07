#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
HARDENING_FILE="${PROJECT_ROOT}/src/build/common/systemd/named.service.d-hardening.conf.tpl"

test -f "${HARDENING_FILE}"

grep -q 'NoNewPrivileges=true' "${HARDENING_FILE}"
grep -q 'PrivateTmp=true' "${HARDENING_FILE}"
grep -q 'ProtectSystem=full' "${HARDENING_FILE}"
grep -q 'ReadWritePaths=' "${HARDENING_FILE}"
grep -q 'CapabilityBoundingSet=' "${HARDENING_FILE}"

echo "Hardening source validation OK"
