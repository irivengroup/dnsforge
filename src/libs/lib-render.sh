#!/usr/bin/env bash



render_file() {

    local source_file="$1"
    local target_file="$2"

    mkdir -p "$(dirname "${target_file}")"

    perl -pe 's/\{\{\s*([A-Z][A-Z0-9_]*)\s*\}\}/exists $ENV{$1} ? $ENV{$1} : $&/ge' \
        "${source_file}" > "${target_file}"
}


render_common_proxy() {

    local out="$1"

    mkdir -p "${out}/etc/named/conf.d"
    mkdir -p "${out}/etc/named/views/external/master"
    mkdir -p "${out}/etc/named/views/external/secondary"
    mkdir -p "${out}/etc/named/views/external/forward"
    mkdir -p "${out}/etc/named/views/internal/master"
    mkdir -p "${out}/etc/named/views/internal/secondary"
    mkdir -p "${out}/etc/named/views/internal/forward"
    mkdir -p "${out}/etc/named/views/internal/reverse"
    mkdir -p "${out}/etc/named/views/partner/master"
    mkdir -p "${out}/etc/named/views/partner/secondary"
    mkdir -p "${out}/etc/named/views/partner/forward"
    mkdir -p "${out}/var/named/secondary/external"
    mkdir -p "${out}/var/named/secondary/internal"
    mkdir -p "${out}/var/named/secondary/partner"
    mkdir -p "${out}/var/named/dynamic"
    mkdir -p "${out}/var/named/rpz"
    mkdir -p "${out}/etc/named/rpz"
    mkdir -p "${out}/var/named/data"
    mkdir -p "${out}/var/log/named"

    render_file "${PROJECT_ROOT}/src/build/dns-proxy/templates/named.conf.j2" "${out}/etc/named.conf"
    render_file "${PROJECT_ROOT}/src/build/common/conf.d/00-acl.conf.j2" "${out}/etc/named/conf.d/00-acl.conf"
    render_file "${PROJECT_ROOT}/src/build/common/conf.d/10-keys.conf.j2" "${out}/etc/named/conf.d/10-keys.conf"
    render_file "${PROJECT_ROOT}/src/build/common/conf.d/20-options-proxy.conf.j2" "${out}/etc/named/conf.d/20-options.conf"
    render_file "${PROJECT_ROOT}/src/build/common/conf.d/30-logging.conf.j2" "${out}/etc/named/conf.d/30-logging.conf"
    render_file "${PROJECT_ROOT}/src/build/common/conf.d/40-controls.conf.j2" "${out}/etc/named/conf.d/40-controls.conf"
    render_file "${PROJECT_ROOT}/src/build/common/conf.d/45-statistics.conf.j2" "${out}/etc/named/conf.d/45-statistics.conf"

    render_dnssec_assets "${out}"
    render_file "${PROJECT_ROOT}/src/build/dns-proxy/templates/50-rpz.conf.j2" "${out}/etc/named/rpz/50-rpz.conf"
    render_file "${PROJECT_ROOT}/src/build/dns-proxy/templates/rpz-zone.conf.j2" "${out}/etc/named/rpz/rpz-zone.conf"
    render_file "${PROJECT_ROOT}/src/build/dns-proxy/templates/rpz.local.zone.j2" "${out}/var/named/rpz/${RPZ_ZONE_NAME}.zone"
    render_file "${PROJECT_ROOT}/src/build/dns-proxy/templates/60-views.conf.j2" "${out}/etc/named/conf.d/60-views.conf"

    render_monitoring_assets "${out}"

    render_hardening_assets "${out}"

    render_proxy_ha_assets "${out}"

    touch "${out}/etc/named/views/external/secondary/zones.index.conf"
    touch "${out}/etc/named/views/external/forward/zones.index.conf"
    touch "${out}/etc/named/views/internal/secondary/zones.index.conf"
    touch "${out}/etc/named/views/internal/forward/zones.index.conf"
    touch "${out}/etc/named/views/internal/reverse/zones.index.conf"
    touch "${out}/etc/named/views/partner/master/zones.index.conf"
    touch "${out}/etc/named/views/partner/secondary/zones.index.conf"
    touch "${out}/etc/named/views/partner/forward/zones.index.conf"
}


render_common_authoritative() {

    local out="$1"

    mkdir -p "${out}/etc/named/conf.d"
    mkdir -p "${out}/etc/named/zones/external/master"
    mkdir -p "${out}/etc/named/zones/internal/master"
    mkdir -p "${out}/etc/named/zones/reverse/master"
    mkdir -p "${out}/etc/keepalived"
    mkdir -p "${out}/var/named/master/external"
    mkdir -p "${out}/var/named/master/internal"
    mkdir -p "${out}/var/named/master/reverse"
    mkdir -p "${out}/var/named/dynamic"
    mkdir -p "${out}/var/named/rpz"
    mkdir -p "${out}/etc/named/rpz"
    mkdir -p "${out}/var/named/data"
    mkdir -p "${out}/var/log/named"

    render_file "${PROJECT_ROOT}/src/build/dns-authoritative/templates/named.conf.j2" "${out}/etc/named.conf"
    render_file "${PROJECT_ROOT}/src/build/common/conf.d/00-acl.conf.j2" "${out}/etc/named/conf.d/00-acl.conf"
    render_file "${PROJECT_ROOT}/src/build/common/conf.d/10-keys.conf.j2" "${out}/etc/named/conf.d/10-keys.conf"
    render_file "${PROJECT_ROOT}/src/build/common/conf.d/20-options-authoritative.conf.j2" "${out}/etc/named/conf.d/20-options.conf"
    render_file "${PROJECT_ROOT}/src/build/common/conf.d/30-logging.conf.j2" "${out}/etc/named/conf.d/30-logging.conf"
    render_file "${PROJECT_ROOT}/src/build/common/conf.d/40-controls.conf.j2" "${out}/etc/named/conf.d/40-controls.conf"
    render_file "${PROJECT_ROOT}/src/build/common/conf.d/45-statistics.conf.j2" "${out}/etc/named/conf.d/45-statistics.conf"

    render_dnssec_assets "${out}"
    render_file "${PROJECT_ROOT}/src/build/dns-proxy/templates/50-rpz.conf.j2" "${out}/etc/named/rpz/50-rpz.conf"
    render_file "${PROJECT_ROOT}/src/build/dns-proxy/templates/rpz-zone.conf.j2" "${out}/etc/named/rpz/rpz-zone.conf"
    render_file "${PROJECT_ROOT}/src/build/dns-proxy/templates/rpz.local.zone.j2" "${out}/var/named/rpz/${RPZ_ZONE_NAME}.zone"
    render_file "${PROJECT_ROOT}/src/build/dns-authoritative/templates/60-zones.conf.j2" "${out}/etc/named/conf.d/60-zones.conf"
    render_file "${PROJECT_ROOT}/src/build/dns-authoritative/templates/keepalived.conf.j2" "${out}/etc/keepalived/keepalived.conf"

    render_monitoring_assets "${out}"

    render_hardening_assets "${out}"

    touch "${out}/etc/named/zones/external/master/zones.index.conf"
    touch "${out}/etc/named/zones/internal/master/zones.index.conf"
    touch "${out}/etc/named/zones/reverse/master/zones.index.conf"
}


render_monitoring_assets() {

    local out="$1"

    mkdir -p "${out}/opt/binddns/monitoring/prometheus"
    mkdir -p "${out}/opt/binddns/monitoring/telegraf"
    mkdir -p "${out}/opt/binddns/monitoring/grafana"
    mkdir -p "${out}/opt/binddns/monitoring/systemd"

    render_file \
        "${PROJECT_ROOT}/src/build/common/monitoring/prometheus/bind-exporter.service.tpl" \
        "${out}/opt/binddns/monitoring/prometheus/bind-exporter.service"

    render_file \
        "${PROJECT_ROOT}/src/build/common/monitoring/prometheus/prometheus-scrape-bind.yml.tpl" \
        "${out}/opt/binddns/monitoring/prometheus/prometheus-scrape-bind.yml"

    render_file \
        "${PROJECT_ROOT}/src/build/common/monitoring/telegraf/telegraf-binddns.conf.tpl" \
        "${out}/opt/binddns/monitoring/telegraf/telegraf-binddns.conf"

    cp \
        "${PROJECT_ROOT}/src/build/common/monitoring/grafana/binddns-dashboard-notes.md" \
        "${out}/opt/binddns/monitoring/grafana/binddns-dashboard-notes.md"

    cp "${PROJECT_ROOT}/src/tools/monitoring/check-binddns-health.sh" "${out}/opt/binddns/monitoring/check-binddns-health.sh"
    cp "${PROJECT_ROOT}/src/tools/monitoring/collect-rndc-stats.sh" "${out}/opt/binddns/monitoring/collect-rndc-stats.sh"
    cp "${PROJECT_ROOT}/src/tools/monitoring/export-binddns-metrics-text.sh" "${out}/opt/binddns/monitoring/export-binddns-metrics-text.sh"
    chmod 0755 "${out}/opt/binddns/monitoring/"*.sh

    render_file "${PROJECT_ROOT}/src/build/common/monitoring/systemd/binddns-healthcheck.service.tpl" "${out}/opt/binddns/monitoring/systemd/binddns-healthcheck.service"
    render_file "${PROJECT_ROOT}/src/build/common/monitoring/systemd/binddns-healthcheck.timer.tpl" "${out}/opt/binddns/monitoring/systemd/binddns-healthcheck.timer"
}


render_hardening_assets() {

    local out="$1"

    mkdir -p "${out}/opt/binddns/hardening/systemd"

    cp \
        "${PROJECT_ROOT}/src/build/common/systemd/named.service.d-hardening.conf.tpl" \
        "${out}/opt/binddns/hardening/systemd/named.service.d-hardening.conf"
}


render_dnssec_assets() {

    local out="$1"

    mkdir -p "${out}/etc/named/dnssec"
    mkdir -p "${out}/var/named/dnssec"

    render_file \
        "${PROJECT_ROOT}/src/build/common/dnssec/dnssec-policy.conf.j2" \
        "${out}/etc/named/dnssec/dnssec-policy.conf"

    render_file \
        "${PROJECT_ROOT}/src/build/common/dnssec/dnssec-policy-enterprise.conf.j2" \
        "${out}/etc/named/dnssec/dnssec-policy-enterprise.conf"

    render_file \
        "${PROJECT_ROOT}/src/build/common/dnssec/dnssec-options.conf.j2" \
        "${out}/etc/named/dnssec/dnssec-options.conf"
}


render_proxy_ha_assets() {

    local out="$1"

    mkdir -p "${out}/opt/binddns/proxy-ha"
    mkdir -p "${out}/etc/keepalived"

    render_file \
        "${PROJECT_ROOT}/src/build/dns-proxy/ha/check-proxy-ha.sh.j2" \
        "${out}/opt/binddns/proxy-ha/check-proxy-ha.sh"

    chmod 0755 "${out}/opt/binddns/proxy-ha/check-proxy-ha.sh"

    render_file \
        "${PROJECT_ROOT}/src/build/dns-proxy/keepalived/keepalived-proxy.conf.j2" \
        "${out}/etc/keepalived/keepalived-proxy.conf"
}
