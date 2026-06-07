#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

DNS1="${DNS1:-}"
DNS2="${DNS2:-}"
TEST_ZONE="${TEST_ZONE:-.}"

if [[ -z "${DNS1}" || -z "${DNS2}" ]]
then
    echo "Usage: DNS1=<ip> DNS2=<ip> TEST_ZONE=<zone> $0" >&2
    exit 1
fi

dig @"${DNS1}" "${TEST_ZONE}" SOA +time=2 +tries=1
dig @"${DNS2}" "${TEST_ZONE}" SOA +time=2 +tries=1

echo "DNS Proxy pair smoke test OK"
