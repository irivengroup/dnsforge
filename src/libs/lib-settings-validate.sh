#!/usr/bin/env bash

settings_fatal() {
    log_error "Settings validation failed: $*"
    return 1
}

require_setting() {
    local name="$1"
    [[ -n "${!name:-}" ]] || settings_fatal "missing required setting: ${name}"
}

reject_placeholder_setting() {
    local name="$1"
    local value="${!name:-}"
    [[ "${value}" != *CHANGE_ME* ]] || settings_fatal "${name} contains CHANGE_ME placeholder"
    [[ "${value}" != *REPLACE_* ]] || settings_fatal "${name} contains REPLACE_ placeholder"
}

require_ipv4_setting() {
    local name="$1"
    local value="${!name:-}"
    require_setting "${name}" || return 1
    reject_placeholder_setting "${name}" || return 1
    is_ipv4 "${value}" || settings_fatal "${name} must be a valid IPv4 address: ${value}"
}

require_ipv4_cidr_or_ipv4_setting() {
    local name="$1"
    local value="${!name:-}"
    local ip cidr
    require_setting "${name}" || return 1
    reject_placeholder_setting "${name}" || return 1
    ip="${value%%/*}"
    cidr="${value#*/}"
    is_ipv4 "${ip}" || settings_fatal "${name} must start with a valid IPv4 address: ${value}"
    if [[ "${value}" == */* ]]
    then
        [[ "${cidr}" =~ ^[0-9]+$ ]] || settings_fatal "${name} CIDR must be numeric: ${value}"
        [[ "${cidr}" -ge 0 && "${cidr}" -le 32 ]] || settings_fatal "${name} CIDR must be between 0 and 32: ${value}"
    fi
}

require_ip_list_setting() {
    local name="$1"
    local value="${!name:-}"
    require_setting "${name}" || return 1
    reject_placeholder_setting "${name}" || return 1
    validate_ip_list "${value}" || settings_fatal "${name} contains invalid IPv4 entries"
}

require_secret_setting() {
    local name="$1"
    local min_len="${2:-12}"
    local value="${!name:-}"
    require_setting "${name}" || return 1
    reject_placeholder_setting "${name}" || return 1
    [[ "${#value}" -ge "${min_len}" ]] || settings_fatal "${name} is too short"
}

validate_boolean_setting() {
    local name="$1"
    local value="${!name:-}"
    [[ "${value}" == "yes" || "${value}" == "no" ]] || settings_fatal "${name} must be yes or no"
}

validate_role_setting() {
    local expected="$1"
    require_setting ROLE || return 1
    [[ "${ROLE}" == "${expected}" ]] || settings_fatal "ROLE must be ${expected}, got ${ROLE}"
}

validate_dns_proxy_settings_strict() {
    validate_role_setting "dns-proxy" || return 1
    require_setting NODE_NAME || return 1
    require_ipv4_setting FRONT_IP || return 1
    require_ipv4_setting BACK_IP || return 1
    require_ipv4_setting ADM_IP || return 1
    require_ip_list_setting AUTHORITATIVE_BACK_IP || return 1

    require_setting DNS_FORWARD_POLICY || return 1
    [[ "${DNS_FORWARD_POLICY}" == "first" || "${DNS_FORWARD_POLICY}" == "only" ]] || settings_fatal "DNS_FORWARD_POLICY must be first or only"

    require_setting TSIG_KEY_NAME || return 1
    require_secret_setting TSIG_SECRET 12 || return 1
    RNDC_KEY_NAME="${RNDC_KEY_NAME:-rndc-key}"
    export RNDC_KEY_NAME
    ensure_rndc_secret || return 1

    validate_boolean_setting ENABLE_RPZ || return 1
    validate_boolean_setting ENABLE_RRL || return 1
    validate_boolean_setting ENABLE_DNSSEC || return 1

    if [[ "${ENABLE_RPZ}" == "yes" ]]
    then
        require_setting RPZ_ZONE_NAME || return 1
    fi

    if [[ "${ENABLE_DNSSEC}" == "yes" ]]
    then
        require_setting DNSSEC_POLICY_NAME || return 1
        require_setting DNSSEC_KEY_DIRECTORY || return 1
    fi

    if [[ -n "${ENABLE_PROXY_HA:-}" ]]
    then
        validate_boolean_setting ENABLE_PROXY_HA || return 1
        if [[ "${ENABLE_PROXY_HA}" == "yes" ]]
        then
            require_ipv4_cidr_or_ipv4_setting PROXY_VIP_FRONT_IP || return 1
            require_setting PROXY_KEEPALIVED_INTERFACE || return 1
            require_secret_setting PROXY_KEEPALIVED_AUTH_PASS 6 || return 1
            require_setting PROXY_KEEPALIVED_STATE || return 1
            [[ "${PROXY_KEEPALIVED_STATE}" == "MASTER" || "${PROXY_KEEPALIVED_STATE}" == "BACKUP" ]] || settings_fatal "PROXY_KEEPALIVED_STATE must be MASTER or BACKUP"
            require_setting PROXY_KEEPALIVED_PRIORITY || return 1
            require_setting PROXY_KEEPALIVED_VRID || return 1
        fi
    fi

    local cluster_var
    while IFS= read -r cluster_var
    do
        [[ "${cluster_var}" =~ ^AUTH_CLUSTER_[A-Z0-9_]+_BACK_IP$ ]] || continue
        require_ip_list_setting "${cluster_var}" || return 1
    done < <(compgen -v)
}

validate_dns_authoritative_settings_strict() {
    validate_role_setting "dns-authoritative" || return 1
    require_setting NODE_NAME || return 1
    require_ipv4_setting BACK_IP || return 1
    require_ipv4_setting ADM_IP || return 1
    require_ipv4_setting VIP_BACK_IP || return 1
    require_ipv4_setting PEER_BACK_IP || return 1

    require_setting PROXY_TRANSFER_CLIENTS || return 1
    reject_placeholder_setting PROXY_TRANSFER_CLIENTS || return 1

    require_setting KEEPALIVED_INTERFACE || return 1
    require_setting KEEPALIVED_STATE || return 1
    [[ "${KEEPALIVED_STATE}" == "MASTER" || "${KEEPALIVED_STATE}" == "BACKUP" ]] || settings_fatal "KEEPALIVED_STATE must be MASTER or BACKUP"

    require_setting KEEPALIVED_PRIORITY || return 1
    require_setting KEEPALIVED_VRID || return 1
    require_secret_setting KEEPALIVED_AUTH_PASS 6 || return 1

    require_setting TSIG_KEY_NAME || return 1
    require_secret_setting TSIG_SECRET 12 || return 1
    RNDC_KEY_NAME="${RNDC_KEY_NAME:-rndc-key}"
    export RNDC_KEY_NAME
    ensure_rndc_secret || return 1

    if [[ "${ENABLE_RPZ:-no}" == "yes" ]]
    then
        settings_fatal "RPZ is not supported on authoritative servers"
        return 1
    fi

    validate_boolean_setting ENABLE_RRL || return 1
    validate_boolean_setting ENABLE_DNSSEC || return 1

    if [[ "${ENABLE_DNSSEC}" == "yes" ]]
    then
        require_setting DNSSEC_POLICY_NAME || return 1
        require_setting DNSSEC_KEY_DIRECTORY || return 1
    fi
}


# Legacy validation functions merged for compatibility.

require_var() {

    local name="$1"

    if [[ -z "${!name:-}" ]]
    then
        log_error "Required variable missing: ${name}"
        exit 1
    fi
}

validate_common_inventory() {

    require_var NODE_NAME
    require_var ROLE
    require_var RNDC_SECRET
    require_var TSIG_SECRET
    require_var RNDC_KEY_NAME
    require_var TSIG_KEY_NAME
}

validate_proxy_inventory() {

    validate_common_inventory

    [[ "${ROLE}" == "dns-proxy" ]] || {
        log_error "Inventory role mismatch: expected dns-proxy"
        exit 1
    }

    require_var FRONT_IP
    require_var BACK_IP
    require_var ADM_IP
    require_var AUTHORITATIVE_BACK_IP
    require_var AUTHORITATIVE_BACK_IP_BIND_LIST
    require_var AUTHORITATIVE_BACK_IP_PRIMARIES_BIND
    require_var AUTHORITATIVE_BACK_IP_ALLOW_NOTIFY_BIND
    require_var ENABLE_RPZ
    require_var RPZ_ZONE_NAME
    require_var RPZ_POLICY
    require_var RRL_RESPONSES_PER_SECOND
    require_var RRL_REFERRALS_PER_SECOND
    require_var RRL_NXDOMAINS_PER_SECOND
    require_var RRL_ERRORS_PER_SECOND
    require_var RRL_WINDOW
}

validate_authoritative_inventory() {

    validate_common_inventory

    [[ "${ROLE}" == "dns-authoritative" ]] || {
        log_error "Inventory role mismatch: expected dns-authoritative"
        exit 1
    }

    require_var BACK_IP
    require_var ADM_IP
    require_var VIP_BACK_IP
    require_var PROXY_TRANSFER_CLIENTS
    require_var KEEPALIVED_INTERFACE
    require_var RRL_RESPONSES_PER_SECOND
    require_var RRL_REFERRALS_PER_SECOND
    require_var RRL_NXDOMAINS_PER_SECOND
    require_var RRL_ERRORS_PER_SECOND
    require_var RRL_WINDOW
}

validate_rendered_config() {

    local rendered_root="$1"

    if [[ ! -f "${rendered_root}/etc/named.conf" ]]
    then
        log_error "Rendered named.conf missing"
        exit 1
    fi

    log_ok "Rendered configuration exists"
}
