#!/usr/bin/env bash

normalize_authoritative_back_ips() {
    local raw="${AUTHORITATIVE_BACK_IP:-}"
    [[ -n "${raw}" ]] || { log_error "AUTHORITATIVE_BACK_IP must define at least one authoritative VIP/IP"; exit 1; }

    validate_ip_list "${raw}"

    AUTHORITATIVE_BACK_IP_FIRST="$(normalize_list "${raw}" | head -1)"
    AUTHORITATIVE_BACK_IP_BIND_LIST="$(build_bind_ip_list "${raw}")"
    AUTHORITATIVE_BACK_IP_PRIMARIES_BIND="$(build_bind_tsig_list "${raw}" "${TSIG_KEY_NAME}")"
    AUTHORITATIVE_BACK_IP_ALLOW_NOTIFY_BIND="$(build_bind_ip_list "${raw}")"

    export AUTHORITATIVE_BACK_IP_FIRST AUTHORITATIVE_BACK_IP_BIND_LIST
    export AUTHORITATIVE_BACK_IP_PRIMARIES_BIND AUTHORITATIVE_BACK_IP_ALLOW_NOTIFY_BIND
}

normalize_authoritative_clusters() {
    local var_name cluster_name raw bind_list primaries_bind allow_notify_bind

    while IFS= read -r var_name; do
        [[ "${var_name}" =~ ^AUTH_CLUSTER_[A-Z0-9_]+_BACK_IP$ ]] || continue
        cluster_name="${var_name#AUTH_CLUSTER_}"
        cluster_name="${cluster_name%_BACK_IP}"
        raw="${!var_name:-}"
        [[ -z "${raw}" ]] && continue

        validate_ip_list "${raw}"

        bind_list="$(build_bind_ip_list "${raw}")"
        primaries_bind="$(build_bind_tsig_list "${raw}" "${TSIG_KEY_NAME}")"
        allow_notify_bind="$(build_bind_ip_list "${raw}")"

        export "AUTH_CLUSTER_${cluster_name}_BIND_LIST=${bind_list}"
        export "AUTH_CLUSTER_${cluster_name}_PRIMARIES_BIND=${primaries_bind}"
        export "AUTH_CLUSTER_${cluster_name}_ALLOW_NOTIFY_BIND=${allow_notify_bind}"
    done < <(compgen -v)
}

validate_settings_no_legacy_placeholders() {
    if grep -RniE 'REPLACE_|CHANGE_ME' "${SETTINGS_FILE:-${INVENTORY_FILE:-}}"; then
        log_error "Settings contains placeholders: ${SETTINGS_FILE:-${INVENTORY_FILE:-}}"
        exit 1
    fi
}

validate_inventory_no_legacy_placeholders() {
    validate_settings_no_legacy_placeholders "$@"
}
