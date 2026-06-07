#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

source "${PROJECT_ROOT}/src/libs/lib-logging.sh" 2>/dev/null || true
source "${PROJECT_ROOT}/src/libs/lib-network.sh" 2>/dev/null || true
source "${PROJECT_ROOT}/src/libs/lib-rndc.sh" 2>/dev/null || true
source "${PROJECT_ROOT}/src/libs/lib-settings-validate.sh"

ROLE="dns-authoritative"
NODE_NAME="rpz-negative"
BACK_IP="192.0.2.11"
ADM_IP="203.0.113.11"
VIP_BACK_IP="192.0.2.10"
PEER_BACK_IP="192.0.2.12"
PROXY_TRANSFER_CLIENTS="198.51.100.53;"
KEEPALIVED_INTERFACE="eth1"
KEEPALIVED_STATE="MASTER"
KEEPALIVED_PRIORITY="110"
KEEPALIVED_VRID="51"
KEEPALIVED_AUTH_PASS="testpass"
TSIG_KEY_NAME="xfr-shared-key"
TSIG_SECRET="dGVzdC10c2lnLXNlY3JldA=="
ENABLE_RRL="yes"
ENABLE_DNSSEC="no"
ENABLE_RPZ="yes"

if validate_dns_authoritative_settings_strict >/dev/null 2>&1
then
    echo "RPZ must be rejected on authoritative servers" >&2
    exit 1
fi

echo "RPZ authoritative forbidden validation OK"
