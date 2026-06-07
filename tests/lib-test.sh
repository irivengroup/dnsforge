#!/usr/bin/env bash

set -o nounset
set -o pipefail

TESTS_PASSED=0
TESTS_FAILED=0
TESTS_WARNED=0

test_info() {
    printf '[INFO ] %s\n' "$*"
}

test_pass() {
    TESTS_PASSED=$((TESTS_PASSED + 1))
    printf '[ PASS] %s\n' "$*"
}

test_warn() {
    TESTS_WARNED=$((TESTS_WARNED + 1))
    printf '[ WARN] %s\n' "$*" >&2
}

test_fail() {
    TESTS_FAILED=$((TESTS_FAILED + 1))
    printf '[ FAIL] %s\n' "$*" >&2
}

require_command() {
    local command_name="$1"

    if command -v "${command_name}" >/dev/null 2>&1
    then
        test_pass "Command available: ${command_name}"
        return 0
    fi

    test_fail "Command missing: ${command_name}"
    return 1
}

print_summary() {
    printf '\nValidation summary\n'
    printf '  passed : %s\n' "${TESTS_PASSED}"
    printf '  warned : %s\n' "${TESTS_WARNED}"
    printf '  failed : %s\n' "${TESTS_FAILED}"

    [[ "${TESTS_FAILED}" -eq 0 ]]
}
