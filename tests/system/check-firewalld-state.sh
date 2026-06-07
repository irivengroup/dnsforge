#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

if ! command -v systemctl >/dev/null 2>&1
then
    echo "systemctl unavailable - skipping firewalld state check"
    exit 0
fi

if systemctl is-active firewalld >/dev/null 2>&1
then
    firewall-cmd --list-all
else
    echo "firewalld inactive - OK if another firewall is used"
fi
