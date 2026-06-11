#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail
"$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/check-dnsforge-enterprise-bind-layout.sh"
