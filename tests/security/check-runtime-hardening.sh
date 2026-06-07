#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

if ! command -v systemctl >/dev/null 2>&1
then
    echo "systemctl unavailable - skipping runtime hardening check"
    exit 0
fi

if ! systemctl list-unit-files named.service >/dev/null 2>&1
then
    echo "named.service unavailable - skipping runtime hardening check"
    exit 0
fi

systemctl show named \
    -p NoNewPrivileges \
    -p PrivateTmp \
    -p ProtectHome \
    -p ProtectSystem \
    -p CapabilityBoundingSet \
    -p ReadWritePaths

echo "Review output and compare with docs/HARDENING.md"
