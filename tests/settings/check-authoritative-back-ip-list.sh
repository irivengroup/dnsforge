#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"




TSIG_KEY_NAME="xfr-shared-key"
AUTHORITATIVE_BACK_IP="192.0.2.10 ; 192.0.2.20,192.0.2.30"
normalize_authoritative_back_ips

grep -q '192.0.2.10;' <<< "${AUTHORITATIVE_BACK_IP_BIND_LIST}"
grep -q '192.0.2.20;' <<< "${AUTHORITATIVE_BACK_IP_BIND_LIST}"
grep -q '192.0.2.30;' <<< "${AUTHORITATIVE_BACK_IP_BIND_LIST}"
grep -q '192.0.2.10 key "xfr-shared-key";' <<< "${AUTHORITATIVE_BACK_IP_PRIMARIES_BIND}"

AUTH_CLUSTER_A_BACK_IP="192.0.2.10"
AUTH_CLUSTER_B_BACK_IP="192.0.2.20, 192.0.2.21"
normalize_authoritative_clusters

grep -q '192.0.2.10 key "xfr-shared-key";' <<< "${AUTH_CLUSTER_A_PRIMARIES_BIND}"
grep -q '192.0.2.20 key "xfr-shared-key";' <<< "${AUTH_CLUSTER_B_PRIMARIES_BIND}"
grep -q '192.0.2.21 key "xfr-shared-key";' <<< "${AUTH_CLUSTER_B_PRIMARIES_BIND}"

echo "AUTHORITATIVE_BACK_IP list support validation OK"
