#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "${PROJECT_ROOT}/tests/lib-test.sh"

require_command bash
require_command grep
require_command find
require_command sed

if command -v named-checkconf >/dev/null 2>&1
then
    test_pass "named-checkconf available"
else
    test_warn "named-checkconf missing - install bind-utils for runtime validation"
fi

if command -v named-checkzone >/dev/null 2>&1
then
    test_pass "named-checkzone available"
else
    test_warn "named-checkzone missing - install bind-utils for zone validation"
fi

print_summary
