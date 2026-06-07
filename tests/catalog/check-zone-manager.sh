#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TMP_DIR="$(mktemp -d /tmp/binddns-zone-manager.XXXXXX)"
trap 'rm -rf "${TMP_DIR}"' EXIT
cp "${PROJECT_ROOT}/src/build/catalog/zones.yml" "${TMP_DIR}/zones.yml"
export CATALOG="${TMP_DIR}/zones.yml"
"${PROJECT_ROOT}/src/tools/zone-manager.sh" create --name lifecycle-test.invalid --type secondary --views "external, internal" --cluster A --acl-external "any;" --acl-internal "recursive_clients;" >/dev/null
"${PROJECT_ROOT}/src/tools/zone-manager.sh" list | grep -q 'enabled lifecycle-test.invalid'
"${PROJECT_ROOT}/src/tools/zone-manager.sh" read --name lifecycle-test.invalid | grep -q 'type: secondary'
"${PROJECT_ROOT}/src/tools/zone-manager.sh" update --name lifecycle-test.invalid --type forward --views internal --cluster B --acl-internal "recursive_clients;" >/dev/null
"${PROJECT_ROOT}/src/tools/zone-manager.sh" read --name lifecycle-test.invalid | grep -q 'type: forward'
"${PROJECT_ROOT}/src/tools/zone-manager.sh" disable --name lifecycle-test.invalid >/dev/null
"${PROJECT_ROOT}/src/tools/zone-manager.sh" list | grep -q 'disabled lifecycle-test.invalid'
"${PROJECT_ROOT}/src/tools/zone-manager.sh" enable --name lifecycle-test.invalid >/dev/null
"${PROJECT_ROOT}/src/tools/zone-manager.sh" list | grep -q 'enabled lifecycle-test.invalid'
"${PROJECT_ROOT}/src/tools/zone-manager.sh" delete --name lifecycle-test.invalid --force >/dev/null
if "${PROJECT_ROOT}/src/tools/zone-manager.sh" list | grep -q 'lifecycle-test.invalid'; then echo "Zone should have been deleted" >&2; exit 1; fi
echo "Zone lifecycle CRUD validation OK"
