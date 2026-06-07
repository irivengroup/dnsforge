#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

DNS_SERVER="${DNS_SERVER:-127.0.0.1}"
ADM_SERVER="${ADM_SERVER:-127.0.0.1}"
TEST_ZONE="${TEST_ZONE:-.}"
STATS_PORT="${STATS_PORT:-8053}"

named_up=0
rndc_up=0
dns_query_ok=0
stats_up=0

systemctl is-active named >/dev/null 2>&1 && named_up=1
command -v rndc >/dev/null 2>&1 && rndc status >/dev/null 2>&1 && rndc_up=1
command -v dig >/dev/null 2>&1 && dig @"${DNS_SERVER}" "${TEST_ZONE}" SOA +time=2 +tries=1 >/dev/null 2>&1 && dns_query_ok=1
command -v curl >/dev/null 2>&1 && curl -fsS "http://${ADM_SERVER}:${STATS_PORT}/json/v1/server" >/dev/null 2>&1 && stats_up=1

cat <<EOF
# HELP binddns_named_up Whether named service is active.
# TYPE binddns_named_up gauge
binddns_named_up ${named_up}
# HELP binddns_rndc_up Whether rndc status works.
# TYPE binddns_rndc_up gauge
binddns_rndc_up ${rndc_up}
# HELP binddns_dns_query_ok Whether a SOA query succeeds.
# TYPE binddns_dns_query_ok gauge
binddns_dns_query_ok ${dns_query_ok}
# HELP binddns_statistics_channel_up Whether BIND statistics channel responds.
# TYPE binddns_statistics_channel_up gauge
binddns_statistics_channel_up ${stats_up}
EOF
