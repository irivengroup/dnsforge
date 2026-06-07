#!/usr/bin/env bash

normalize_list() {
    local raw="${1:-}"
    printf '%s\n' "${raw}" | tr ',;' '  ' | xargs -n1 2>/dev/null || true
}

is_ipv4() {
    local ip="${1:-}" octet
    [[ "${ip}" =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}$ ]] || return 1
    IFS='.' read -r -a octets <<< "${ip}"
    for octet in "${octets[@]}"; do
        [[ "${octet}" -ge 0 && "${octet}" -le 255 ]] || return 1
    done
}

validate_ip_list() {
    local raw="${1:-}" ip
    while IFS= read -r ip; do
        [[ -z "${ip}" ]] && continue
        is_ipv4 "${ip}" || { log_error "Invalid IPv4 address in list: ${ip}"; return 1; }
    done < <(normalize_list "${raw}")
}

build_bind_ip_list() {
    local raw="${1:-}" ip
    while IFS= read -r ip; do
        [[ -z "${ip}" ]] && continue
        printf '%s;\n                ' "${ip}"
    done < <(normalize_list "${raw}")
}

build_bind_tsig_list() {
    local raw="${1:-}" key="${2:-}" ip
    while IFS= read -r ip; do
        [[ -z "${ip}" ]] && continue
        printf '%s key "%s";\n                ' "${ip}" "${key}"
    done < <(normalize_list "${raw}")
}
