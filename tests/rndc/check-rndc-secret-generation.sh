#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"


ROLE="dns-proxy"; NODE_NAME="rndc-test"
unset RNDC_KEY_NAME || true
unset RNDC_SECRET || true
export PROJECT_ROOT ROLE NODE_NAME
secret_file="$(rndc_secret_file_for_node "${NODE_NAME}")"
rm -f "${secret_file}"
ensure_rndc_secret
[[ "${RNDC_KEY_NAME}" == "rndc-key" ]]
[[ -n "${RNDC_SECRET}" ]]
test -s "${secret_file}"
old_secret="${RNDC_SECRET}"
rotate_rndc_secret >/dev/null
[[ -n "${RNDC_SECRET}" ]]
[[ "${RNDC_SECRET}" != "${old_secret}" ]]
echo "RNDC secret generation and rotation validation OK"
