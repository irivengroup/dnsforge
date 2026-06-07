#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

if command -v rndc >/dev/null 2>&1
then
    rndc status || {
        echo "rndc status failed. Check RNDC key, controls and ADM binding." >&2
        exit 1
    }
else
    echo "rndc unavailable - skipping"
fi
