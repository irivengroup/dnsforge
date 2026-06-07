#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

CONFIG_ROOT="${1:-/etc}"

grep -RniE 'response-policy|rate-limit|minimal-any|minimal-responses|dnssec-validation|allow-transfer|allow-recursion|allow-query-cache' "${CONFIG_ROOT}/named.conf" "${CONFIG_ROOT}/named" || true
