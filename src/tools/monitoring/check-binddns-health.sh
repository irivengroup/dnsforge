#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

DNS_SERVER="${DNS_SERVER:-127.0.0.1}"
ADM_SERVER="${ADM_SERVER:-127.0.0.1}"
TEST_ZONE="${TEST_ZONE:-.}"
STATS_PORT="${STATS_PORT:-8053}"

status=0

check_named() {
    if systemctl is-active named >/dev/null 2>&1
    then
        echo "OK named service is active"
    else
        echo "CRITICAL named service is not active" >&2
        status=2
    fi
}

check_rndc() {
    if command -v rndc >/dev/null 2>&1 && rndc status >/dev/null 2>&1
    then
        echo "OK rndc status"
    else
        echo "WARNING rndc status failed" >&2
        [[ "${status}" -lt 1 ]] && status=1
    fi
}

check_dns() {
    if command -v dig >/dev/null 2>&1 && dig @"${DNS_SERVER}" "${TEST_ZONE}" SOA +time=2 +tries=1 >/dev/null 2>&1
    then
        echo "OK DNS query ${TEST_ZONE} via ${DNS_SERVER}"
    else
        echo "CRITICAL DNS query failed: ${TEST_ZONE} via ${DNS_SERVER}" >&2
        status=2
    fi
}

check_stats() {
    if command -v curl >/dev/null 2>&1 && curl -fsS "http://${ADM_SERVER}:${STATS_PORT}/json/v1/server" >/dev/null 2>&1
    then
        echo "OK statistics-channel"
    else
        echo "WARNING statistics-channel unavailable" >&2
        [[ "${status}" -lt 1 ]] && status=1
    fi
}

check_named
check_rndc
check_dns
check_stats

exit "${status}"
