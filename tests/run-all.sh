#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

run_test() {

    local test_script="$1"

    printf '\n===== %s =====\n' "${test_script}"

    bash "${PROJECT_ROOT}/${test_script}"
}

run_test "tests/documentation/check-doc-navigation.sh"
run_test "tests/settings/check-settings-variables.sh"
run_test "tests/settings/check-settings-layout.sh"
run_test "tests/settings/check-validation-library-consolidation.sh"
run_test "tests/settings/check-list-normalization.sh"
run_test "tests/rndc/check-rndc-secret-generation.sh"
run_test "tests/rndc/check-rndc-settings-optional.sh"
run_test "tests/settings/check-settings-strict-validation.sh"
run_test "tests/settings/check-settings-strict-negative.sh"
run_test "tests/settings/check-authoritative-back-ip-list.sh"
run_test "tests/project/check-project-coherence.sh"
run_test "tests/monitoring/check-monitoring-templates.sh"
run_test "tests/monitoring/check-native-monitoring-tools.sh"
run_test "tests/monitoring/check-native-monitoring-render.sh"
run_test "tests/proxy-ha/check-proxy-ha-design.sh"
run_test "tests/proxy-ha/check-proxy-ha-optional-default.sh"
run_test "tests/proxy-ha/check-proxy-ha-syntax.sh"
run_test "tests/proxy-ha/check-proxy-ha-render.sh"
run_test "tests/render/check-render-inventories.sh"
run_test "tests/monitoring/check-rendered-monitoring.sh"
run_test "tests/style/check-bind-template-format.sh"
run_test "tests/dns-validation/check-prerequisites.sh"
run_test "tests/dns-validation/check-zone-sources.sh"
run_test "tests/dns-validation/check-proxy-master-zones.sh"

if find "${PROJECT_ROOT}/src/render" -type f -name 'zones.index.conf' | grep -q .
then
    run_test "tests/dns-validation/check-zone-indexes.sh"
else
    echo "Skipping zone index check: no rendered indexes found"
fi

if find "${PROJECT_ROOT}/src/render" -type f -name 'named.conf' | grep -q .
then
    run_test "tests/dns-validation/check-rendered-bind-config.sh"
    run_test "tests/dns-validation/check-rendered-zone-files.sh"
else
    echo "Skipping rendered BIND checks: run --render-only first"
fi

run_test "tests/security/check-security-baseline.sh"
run_test "tests/backup/check-backup-tools.sh"
run_test "tests/deployment/check-production-gate-tools.sh"
run_test "tests/deployment/check-production-gate-render.sh"
run_test "tests/backup/check-backup-dry-run.sh"
run_test "tests/dnssec/check-dnssec-templates.sh"
run_test "tests/dnssec/check-dnssec-enterprise-templates.sh"
run_test "tests/dnssec/check-catalog-public-dnssec.sh"
run_test "tests/dnssec/check-dnssec-enterprise-render.sh"
run_test "tests/security/check-hardening-source.sh"
run_test "tests/security/check-file-permissions-policy.sh"
run_test "tests/security/check-tsig-tooling.sh"
run_test "tests/security/check-no-hardcoded-hostnames.sh"
run_test "tests/system/check-firewalld-state.sh"
run_test "tests/system/check-selinux-state.sh"

echo
echo "All available validations completed"

run_test "tests/integration/check-zone-acl-render.sh"
run_test "tests/catalog/check-zone-catalog-generate.sh"
run_test "tests/catalog/check-zone-catalog-render.sh"
run_test "tests/catalog/check-zone-manager.sh"
run_test "tests/catalog/check-zone-manager-negative.sh"

run_test "tests/security/check-rpz-authoritative-forbidden.sh"
run_test "tests/security/check-rpz-authoritative-render-clean.sh"

run_test "tests/documentation/check-doc-links.sh"

run_test "tests/documentation/check-doc-headers-footers.sh"

run_test "tests/documentation/check-readme-product-scope.sh"

run_test "tests/documentation/check-docs-index-contexts.sh"

run_test "tests/python/check-dnsforge-cli.sh"

run_test "tests/python/check-dnsforge-oop-layout.sh"

run_test "tests/python/check-dnsforge-render.sh"

run_test "tests/python/check-dnsforge-zone-manager.sh"

run_test "tests/python/check-dnsforge-initialize-plan.sh"

run_test "tests/python/check-dnsforge-initialize-native.sh"

run_test "tests/python/check-dnsforge-product-python.sh"

run_test "tests/python/check-dnsforge-product-audit.sh"

run_test "tests/python/check-dnsforge-build-context.sh"

run_test "tests/python/check-dnsforge-install-layout.sh"

run_test "tests/python/check-dnsforge-setup-template-coverage.sh"

run_test "tests/python/check-dnsforge-profile-best-practices.sh"

run_test "tests/python/check-dnsforge-zone-records.sh"

run_test "tests/python/check-dnsforge-security.sh"

run_test "tests/python/check-dnsforge-operations.sh"

run_test "tests/python/check-dnsforge-cluster.sh"

run_test "tests/python/check-dnsforge-zone-show-and-settings.sh"

run_test "tests/python/check-dnsforge-enterprise-bind-rendering.sh"
