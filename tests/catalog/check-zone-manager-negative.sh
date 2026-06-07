#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TMP_DIR="$(mktemp -d /tmp/binddns-zone-manager-negative.XXXXXX)"
trap 'rm -rf "${TMP_DIR}"' EXIT
cp "${PROJECT_ROOT}/src/build/catalog/zones.yml" "${TMP_DIR}/zones.yml"
export CATALOG="${TMP_DIR}/zones.yml"
if "${PROJECT_ROOT}/src/tools/zone-manager.sh" create --name bad.invalid --type invalid --views external >/dev/null 2>&1; then echo "Invalid type should fail" >&2; exit 1; fi
if "${PROJECT_ROOT}/src/tools/zone-manager.sh" delete --name split-example.invalid >/dev/null 2>&1; then echo "Delete without --force should fail" >&2; exit 1; fi
echo "Zone lifecycle negative validation OK"
