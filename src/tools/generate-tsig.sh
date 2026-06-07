#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

KEY_NAME="${1:-xfr-shared-key}"
OUTPUT_DIR="${PROJECT_ROOT}/secrets"

mkdir -p "${OUTPUT_DIR}"
chmod 0700 "${OUTPUT_DIR}"

if ! command -v tsig-keygen >/dev/null 2>&1
then
    echo "tsig-keygen not found. Install bind-utils." >&2
    exit 1
fi

timestamp="$(date +%Y%m%d-%H%M%S)"
output_file="${OUTPUT_DIR}/tsig-${KEY_NAME}-${timestamp}.key"

tsig-keygen -a hmac-sha256 "${KEY_NAME}" > "${output_file}"
chmod 0600 "${output_file}"

secret="$(awk -F '"' '/secret/ { print $2 }' "${output_file}")"

cat <<EOF

TSIG key generated.

Key file:
  ${output_file}

Inventory values to set:

TSIG_KEY_NAME="${KEY_NAME}"
TSIG_SECRET="${secret}"

Security note:
  Apply the same TSIG_SECRET to every DNS node participating
  in the same transfer relationship.

EOF
