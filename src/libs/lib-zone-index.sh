#!/usr/bin/env bash

generate_zone_index() {

    local source_dir="$1"
    local render_index_file="$2"
    local render_zone_dir="$3"

    mkdir -p "$(dirname "${render_index_file}")"
    mkdir -p "${render_zone_dir}"

    : > "${render_index_file}"

    if [[ ! -d "${source_dir}" ]]
    then
        return 0
    fi

    while IFS= read -r source_file
    do
        local rendered_file="${render_zone_dir}/$(basename "${source_file}")"

        render_file "${source_file}" "${rendered_file}"

        printf 'include "%s";\n\n' "${rendered_file#${RENDER_ROOT}}" >> "${render_index_file}"

    done < <(find "${source_dir}" -type f -name '*.conf' | sort)
}


copy_zone_data_files() {

    local source_dir="$1"
    local target_dir="$2"

    mkdir -p "${target_dir}"

    if [[ ! -d "${source_dir}" ]]
    then
        return 0
    fi

    while IFS= read -r zone_file
    do
        cp "${zone_file}" "${target_dir}/$(basename "${zone_file}")"
    done < <(find "${source_dir}" -type f \( -name '*.zone' -o -name '*.db' \) | sort)
}


generate_proxy_zone_indexes() {

    generate_zone_index \
        "${PROJECT_ROOT}/src/build/dns-proxy/zones/generated/external/master" \
        "${RENDER_ROOT}/etc/named/views/external/master/zones.index.conf" \
        "${RENDER_ROOT}/etc/named/views/external/master"

    generate_zone_index \
        "${PROJECT_ROOT}/src/build/dns-proxy/zones/generated/internal/master" \
        "${RENDER_ROOT}/etc/named/views/internal/master/zones.index.conf" \
        "${RENDER_ROOT}/etc/named/views/internal/master"

    generate_zone_index \
        "${PROJECT_ROOT}/src/build/dns-proxy/zones/generated/partner/master" \
        "${RENDER_ROOT}/etc/named/views/partner/master/zones.index.conf" \
        "${RENDER_ROOT}/etc/named/views/partner/master"

    generate_zone_index \
        "${PROJECT_ROOT}/src/build/dns-proxy/zones/generated/external/secondary" \
        "${RENDER_ROOT}/etc/named/views/external/secondary/zones.index.conf" \
        "${RENDER_ROOT}/etc/named/views/external/secondary"

    generate_zone_index \
        "${PROJECT_ROOT}/src/build/dns-proxy/zones/generated/internal/secondary" \
        "${RENDER_ROOT}/etc/named/views/internal/secondary/zones.index.conf" \
        "${RENDER_ROOT}/etc/named/views/internal/secondary"

    generate_zone_index \
        "${PROJECT_ROOT}/src/build/dns-proxy/zones/generated/internal/forward" \
        "${RENDER_ROOT}/etc/named/views/internal/forward/zones.index.conf" \
        "${RENDER_ROOT}/etc/named/views/internal/forward"

    generate_zone_index \
        "${PROJECT_ROOT}/src/build/dns-proxy/zones/generated/partner/forward" \
        "${RENDER_ROOT}/etc/named/views/partner/forward/zones.index.conf" \
        "${RENDER_ROOT}/etc/named/views/partner/forward"

    generate_zone_index \
        "${PROJECT_ROOT}/src/build/dns-proxy/zones/partner/master" \
        "${RENDER_ROOT}/etc/named/views/partner/master/zones.index.conf" \
        "${RENDER_ROOT}/etc/named/views/partner/master"

    generate_zone_index \
        "${PROJECT_ROOT}/src/build/dns-proxy/zones/partner/secondary" \
        "${RENDER_ROOT}/etc/named/views/partner/secondary/zones.index.conf" \
        "${RENDER_ROOT}/etc/named/views/partner/secondary"

    generate_zone_index \
        "${PROJECT_ROOT}/src/build/dns-proxy/zones/partner/forward" \
        "${RENDER_ROOT}/etc/named/views/partner/forward/zones.index.conf" \
        "${RENDER_ROOT}/etc/named/views/partner/forward"

    generate_zone_index \
        "${PROJECT_ROOT}/src/build/dns-proxy/zones/external/master" \
        "${RENDER_ROOT}/etc/named/views/external/master/zones.index.conf" \
        "${RENDER_ROOT}/etc/named/views/external/master"

    generate_zone_index \
        "${PROJECT_ROOT}/src/build/dns-proxy/zones/internal/master" \
        "${RENDER_ROOT}/etc/named/views/internal/master/zones.index.conf" \
        "${RENDER_ROOT}/etc/named/views/internal/master"

    copy_zone_data_files \
        "${PROJECT_ROOT}/src/build/dns-proxy/zones/external/master" \
        "${RENDER_ROOT}/var/named/master/external"

    copy_zone_data_files \
        "${PROJECT_ROOT}/src/build/dns-proxy/zones/internal/master" \
        "${RENDER_ROOT}/var/named/master/internal"

    generate_zone_index \
        "${PROJECT_ROOT}/src/build/dns-proxy/zones/external/secondary" \
        "${RENDER_ROOT}/etc/named/views/external/secondary/zones.index.conf" \
        "${RENDER_ROOT}/etc/named/views/external/secondary"

    generate_zone_index \
        "${PROJECT_ROOT}/src/build/dns-proxy/zones/external/forward" \
        "${RENDER_ROOT}/etc/named/views/external/forward/zones.index.conf" \
        "${RENDER_ROOT}/etc/named/views/external/forward"

    generate_zone_index \
        "${PROJECT_ROOT}/src/build/dns-proxy/zones/internal/secondary" \
        "${RENDER_ROOT}/etc/named/views/internal/secondary/zones.index.conf" \
        "${RENDER_ROOT}/etc/named/views/internal/secondary"

    generate_zone_index \
        "${PROJECT_ROOT}/src/build/dns-proxy/zones/internal/forward" \
        "${RENDER_ROOT}/etc/named/views/internal/forward/zones.index.conf" \
        "${RENDER_ROOT}/etc/named/views/internal/forward"

    generate_zone_index \
        "${PROJECT_ROOT}/src/build/dns-proxy/zones/internal/reverse" \
        "${RENDER_ROOT}/etc/named/views/internal/reverse/zones.index.conf" \
        "${RENDER_ROOT}/etc/named/views/internal/reverse"
}


generate_authoritative_zone_indexes() {

    generate_zone_index \
        "${PROJECT_ROOT}/src/build/dns-authoritative/zones/external/master" \
        "${RENDER_ROOT}/etc/named/zones/external/master/zones.index.conf" \
        "${RENDER_ROOT}/etc/named/zones/external/master"

    generate_zone_index \
        "${PROJECT_ROOT}/src/build/dns-authoritative/zones/internal/master" \
        "${RENDER_ROOT}/etc/named/zones/internal/master/zones.index.conf" \
        "${RENDER_ROOT}/etc/named/zones/internal/master"

    generate_zone_index \
        "${PROJECT_ROOT}/src/build/dns-authoritative/zones/reverse/master" \
        "${RENDER_ROOT}/etc/named/zones/reverse/master/zones.index.conf" \
        "${RENDER_ROOT}/etc/named/zones/reverse/master"

    copy_zone_data_files \
        "${PROJECT_ROOT}/src/build/dns-authoritative/zones/external/master" \
        "${RENDER_ROOT}/var/named/master/external"

    copy_zone_data_files \
        "${PROJECT_ROOT}/src/build/dns-authoritative/zones/internal/master" \
        "${RENDER_ROOT}/var/named/master/internal"

    copy_zone_data_files \
        "${PROJECT_ROOT}/src/build/dns-authoritative/zones/reverse/master" \
        "${RENDER_ROOT}/var/named/master/reverse"
}
