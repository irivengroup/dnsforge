#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

: "${FRONT_IP:?FRONT_IP is required}"
: "${BACK_IP:?BACK_IP is required}"

dig @"${FRONT_IP}" SOA . +time=2 +tries=1 || true
dig @"${BACK_IP}" SOA . +time=2 +tries=1 || true
