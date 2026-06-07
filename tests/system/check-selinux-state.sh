#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

if command -v getenforce >/dev/null 2>&1
then
    getenforce
else
    echo "getenforce unavailable - SELinux tools not installed or non-SELinux system"
fi

if command -v restorecon >/dev/null 2>&1
then
    restorecon -nRv /etc/named.conf /etc/named /var/named /var/log/named 2>/dev/null || true
fi
