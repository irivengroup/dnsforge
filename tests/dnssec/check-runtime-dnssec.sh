#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

ZONE="${1:-}"

if [[ -z "${ZONE}" ]]
then
    echo "Usage: $0 <zone>" >&2
    exit 1
fi

if command -v rndc >/dev/null 2>&1
then
    rndc signing -list "${ZONE}" || true
    rndc dnssec -status "${ZONE}" || true
fi

if command -v dig >/dev/null 2>&1
then
    dig "${ZONE}" SOA +dnssec
fi

if command -v delv >/dev/null 2>&1
then
    delv "${ZONE}" SOA || true
fi
