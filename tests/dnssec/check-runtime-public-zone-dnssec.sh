#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

ZONE="${1:-}"
SERVER="${2:-127.0.0.1}"

if [[ -z "${ZONE}" ]]
then
    echo "Usage: $0 <zone> [server]" >&2
    exit 1
fi

dig @"${SERVER}" "${ZONE}" SOA +dnssec
dig @"${SERVER}" "${ZONE}" DNSKEY +dnssec

if command -v delv >/dev/null 2>&1
then
    delv @"${SERVER}" "${ZONE}" SOA || true
fi

if command -v rndc >/dev/null 2>&1
then
    rndc dnssec -status "${ZONE}" || true
    rndc signing -list "${ZONE}" || true
fi
