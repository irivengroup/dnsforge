#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

: "${BACK_IP:?BACK_IP is required}"
: "${RPZ_TEST_DOMAIN:=malware.example.invalid}"

dig @"${BACK_IP}" "${RPZ_TEST_DOMAIN}" A +time=2 +tries=1

echo "Review the answer section: RPZ policy should apply to ${RPZ_TEST_DOMAIN}"
