#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"






ROLE="dns-proxy"
NODE_NAME="bad"
FRONT_IP="999.0.2.53"
BACK_IP="198.51.100.53"
ADM_IP="203.0.113.53"
AUTHORITATIVE_BACK_IP="192.0.2.10"
DNS_FORWARD_POLICY="first"
TSIG_KEY_NAME="xfr-shared-key"
TSIG_SECRET="dGVzdC10c2lnLXNlY3JldA=="
ENABLE_RPZ="no"
ENABLE_RRL="yes"
ENABLE_DNSSEC="no"
ENABLE_PROXY_HA="no"

if validate_dns_proxy_settings_strict >/dev/null 2>&1
then
    echo "Negative settings validation should have failed" >&2
    exit 1
fi

echo "Strict negative settings validation OK"
