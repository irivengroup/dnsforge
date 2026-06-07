#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

for inventory in "${PROJECT_ROOT}"/src/settings/dns-proxy/*.env
do
    grep -q '^ROLE="dns-proxy"' "${inventory}"
    grep -q '^NODE_NAME=' "${inventory}"
    grep -q '^FRONT_IP=' "${inventory}"
    grep -q '^BACK_IP=' "${inventory}"
    grep -q '^ADM_IP=' "${inventory}"
    grep -q '^AUTHORITATIVE_BACK_IP=' "${inventory}"
    grep -q '^DNS_FORWARD_POLICY=' "${inventory}"
    grep -q '^TSIG_KEY_NAME=' "${inventory}"
    grep -q '^TSIG_SECRET=' "${inventory}"
    grep -q '^RNDC_KEY_NAME=' "${inventory}"
    grep -q '^RNDC_SECRET=' "${inventory}"
    grep -q '^RPZ_ZONE_NAME=' "${inventory}"
    grep -q '^RRL_RESPONSES_PER_SECOND=' "${inventory}"
done

for inventory in "${PROJECT_ROOT}"/src/settings/dns-authoritative/*.env
do
    grep -q '^ROLE="dns-authoritative"' "${inventory}"
    grep -q '^NODE_NAME=' "${inventory}"
    grep -q '^BACK_IP=' "${inventory}"
    grep -q '^ADM_IP=' "${inventory}"
    grep -q '^VIP_BACK_IP=' "${inventory}"
    grep -q '^PROXY_TRANSFER_CLIENTS=' "${inventory}"
    grep -q '^KEEPALIVED_INTERFACE=' "${inventory}"
    grep -q '^TSIG_KEY_NAME=' "${inventory}"
    grep -q '^TSIG_SECRET=' "${inventory}"
    grep -q '^RNDC_KEY_NAME=' "${inventory}"
    grep -q '^RNDC_SECRET=' "${inventory}"
done

echo "Settings variable alignment validation OK"
