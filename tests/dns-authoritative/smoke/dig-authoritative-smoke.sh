#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

: "${BACK_IP:?BACK_IP is required}"

dig @"${BACK_IP}" SOA . +time=2 +tries=1 || true
