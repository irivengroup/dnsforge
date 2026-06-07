#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CATALOG="${1:-${PROJECT_ROOT}/src/build/catalog/zones.yml}"
OUT="${PROJECT_ROOT}/src/build/dns-proxy/zones/generated"

if [[ ! -f "${CATALOG}" ]]
then
    echo "Catalog not found: ${CATALOG}" >&2
    exit 1
fi

rm -f "${OUT}"/*/*/*.conf "${OUT}"/*/*/*.zone 2>/dev/null || true

mkdir -p \
    "${OUT}/external/master" \
    "${OUT}/internal/master" \
    "${OUT}/partner/master" \
    "${OUT}/external/secondary" \
    "${OUT}/internal/secondary" \
    "${OUT}/internal/forward" \
    "${OUT}/partner/forward"

write_master_zone_conf() {
    local view="$1"
    local zone="$2"
    local acl="$3"
    local file="${OUT}/${view}/master/${zone}.conf"

    cat > "${file}" <<EOF
zone "${zone}" {

        type master;

        file "/var/named/master/${view}/${zone}.zone";

        allow-query {
                ${acl}
        };

        dnssec-policy "{{ DNSSEC_POLICY_NAME }}";

        inline-signing yes;

        allow-transfer {
                none;
        };

        allow-update {
                none;
        };

        notify no;
};
EOF
}

write_master_zone_data() {
    local view="$1"
    local zone="$2"
    local file="${OUT}/${view}/master/${zone}.zone"

    cat > "${file}" <<EOF
\$TTL 3600

@       IN SOA  ns.${zone}. hostmaster.${zone}. (

                2026060601 ; serial
                3600       ; refresh
                900        ; retry
                1209600    ; expire
                300        ; negative cache ttl
)

        IN NS   ns.${zone}.

ns      IN A    192.0.2.53
app     IN A    192.0.2.80
EOF
}

write_secondary_zone_conf() {
    local view="$1"
    local zone="$2"
    local cluster="$3"
    local acl="$4"
    local file="${OUT}/${view}/secondary/${zone}.conf"

    cat > "${file}" <<EOF
zone "${zone}" {

        type secondary;

        file "/var/named/secondary/${view}/${zone}.zone";

        primaries {
                {{ AUTH_CLUSTER_${cluster}_PRIMARIES_BIND }}
        };

        allow-notify {
                {{ AUTH_CLUSTER_${cluster}_ALLOW_NOTIFY_BIND }}
        };

        allow-query {
                ${acl}
        };

        allow-transfer {
                none;
        };
};
EOF
}

write_forward_zone_conf() {
    local view="$1"
    local zone="$2"
    local cluster="$3"
    local acl="$4"
    local file="${OUT}/${view}/forward/${zone}.conf"

    cat > "${file}" <<EOF
zone "${zone}" {

        type forward;

        forward {{ DNS_FORWARD_POLICY }};

        forwarders {
                {{ AUTH_CLUSTER_${cluster}_BIND_LIST }}
        };

        allow-query {
                ${acl}
        };
};
EOF
}

# Generated from src/build/catalog/zones.yml examples.
write_master_zone_conf external split-example.invalid "any;"
write_master_zone_conf internal split-example.invalid "recursive_clients;"
write_master_zone_conf partner split-example.invalid "partner_clients;"
write_master_zone_data external split-example.invalid
write_master_zone_data internal split-example.invalid
write_master_zone_data partner split-example.invalid

write_secondary_zone_conf external catalog-secondary-a.invalid A "any;"
write_secondary_zone_conf internal catalog-secondary-a.invalid A "recursive_clients;"

write_forward_zone_conf internal catalog-forward-b.invalid B "recursive_clients;"
write_forward_zone_conf partner catalog-forward-b.invalid B "partner_clients;"

echo "Zone catalog generated from ${CATALOG}"
