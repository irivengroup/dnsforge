#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"






set -o allexport
source "${PROJECT_ROOT}/tests/fixtures/settings/dns-proxy/strict-valid.env"
set +o allexport
validate_dns_proxy_settings_strict
normalize_authoritative_back_ips
normalize_authoritative_clusters

unset ENABLE_RPZ ENABLE_PROXY_HA PROXY_VIP_FRONT_IP PROXY_KEEPALIVED_INTERFACE PROXY_KEEPALIVED_STATE PROXY_KEEPALIVED_PRIORITY PROXY_KEEPALIVED_VRID PROXY_KEEPALIVED_AUTH_PASS PROXY_HA_HEALTHCHECK_ZONE || true

set -o allexport
source "${PROJECT_ROOT}/tests/fixtures/settings/dns-authoritative/strict-valid.env"
set +o allexport
ENABLE_RPZ="no"
validate_dns_authoritative_settings_strict

echo "Strict settings validation OK"
