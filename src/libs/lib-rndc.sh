#!/usr/bin/env bash

rndc_default_key_name() {
    RNDC_KEY_NAME="${RNDC_KEY_NAME:-rndc-key}"
    export RNDC_KEY_NAME
}

generate_rndc_secret_value() {
    if command -v openssl >/dev/null 2>&1
    then
        openssl rand -base64 32
        return 0
    fi
    if [[ -r /dev/urandom ]]
    then
        head -c 32 /dev/urandom | base64
        return 0
    fi
    date +%s%N | sha256sum | awk '{print $1}' | base64
}

rndc_secret_file_for_node() {
    local node_name="${NODE_NAME:-${1:-default}}"
    local role="${ROLE:-common}"
    printf '%s/src/settings/.generated/%s/%s/rndc.secret' "${PROJECT_ROOT}" "${role}" "${node_name}"
}

ensure_rndc_secret() {
    rndc_default_key_name
    if [[ -n "${RNDC_SECRET:-}" ]]
    then
        export RNDC_SECRET
        return 0
    fi
    local secret_file
    secret_file="$(rndc_secret_file_for_node "${NODE_NAME:-default}")"
    mkdir -p "$(dirname "${secret_file}")"
    chmod 0700 "$(dirname "${secret_file}")"
    if [[ ! -s "${secret_file}" ]]
    then
        generate_rndc_secret_value > "${secret_file}"
        chmod 0600 "${secret_file}"
    fi
    RNDC_SECRET="$(cat "${secret_file}")"
    export RNDC_SECRET
}

rotate_rndc_secret() {
    rndc_default_key_name
    local secret_file
    secret_file="$(rndc_secret_file_for_node "${NODE_NAME:-default}")"
    mkdir -p "$(dirname "${secret_file}")"
    chmod 0700 "$(dirname "${secret_file}")"
    generate_rndc_secret_value > "${secret_file}"
    chmod 0600 "${secret_file}"
    RNDC_SECRET="$(cat "${secret_file}")"
    export RNDC_SECRET
    printf '%s\n' "${secret_file}"
}
