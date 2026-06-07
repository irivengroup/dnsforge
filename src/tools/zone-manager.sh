#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CATALOG="${CATALOG:-${PROJECT_ROOT}/src/build/catalog/zones.yml}"

usage() {
    cat <<'EOF'
Usage:
  zone-manager.sh list
  zone-manager.sh read --name <zone>
  zone-manager.sh create --name <zone> --type <master|secondary|forward> --views <v1,v2> [--cluster <A>] [--dnssec <required|optional|disabled>] [--acl-external <acl>] [--acl-internal <acl>] [--acl-partner <acl>]
  zone-manager.sh update --name <zone> [--type <master|secondary|forward>] [--views <v1,v2>] [--cluster <A>] [--dnssec <required|optional|disabled>] [--acl-external <acl>] [--acl-internal <acl>] [--acl-partner <acl>]
  zone-manager.sh disable --name <zone>
  zone-manager.sh enable --name <zone>
  zone-manager.sh delete --name <zone> --force
EOF
}

fatal(){ echo "ERROR: $*" >&2; exit 1; }
require_catalog(){ [[ -f "${CATALOG}" ]] || fatal "Catalog not found: ${CATALOG}"; }
validate_zone_name(){ [[ "$1" =~ ^[A-Za-z0-9._-]+$ ]] || fatal "Invalid zone name: $1"; }
validate_type(){ [[ "$1" == "master" || "$1" == "secondary" || "$1" == "forward" ]] || fatal "Invalid zone type: $1"; }
normalize_views(){ printf '%s\n' "${1:-}" | tr ',;' '  ' | xargs -n1 2>/dev/null || true; }
validate_views(){ local v; [[ -n "$1" ]] || fatal "Views must not be empty"; while IFS= read -r v; do [[ -z "$v" ]] && continue; [[ "$v" == external || "$v" == internal || "$v" == partner ]] || fatal "Invalid view: $v"; done < <(normalize_views "$1"); }
validate_dnssec(){ [[ -z "$1" || "$1" == required || "$1" == optional || "$1" == disabled ]] || fatal "Invalid dnssec value: $1"; }
tmp_file(){ mktemp /tmp/binddns-zone-manager.XXXXXX; }

zone_exists_in_section(){
    local section="$1" name="$2"
    awk -v section="$section" -v name="$name" '
        /^zones:/ {current="zones"; next}
        /^disabled_zones:/ {current="disabled_zones"; next}
        /^[^[:space:]]/ {if ($0 !~ /^zones:/ && $0 !~ /^disabled_zones:/) current=""}
        current == section && $0 ~ "^[[:space:]]*-[[:space:]]name:[[:space:]]*" name "$" {found=1}
        END {exit found ? 0 : 1}
    ' "$CATALOG"
}
zone_exists_anywhere(){ zone_exists_in_section zones "$1" || zone_exists_in_section disabled_zones "$1"; }

read_zone_block_from_section(){
    local section="$1" name="$2"
    awk -v section="$section" -v name="$name" '
        /^zones:/ {current="zones"; next}
        /^disabled_zones:/ {current="disabled_zones"; next}
        current == section && $0 ~ "^[[:space:]]*-[[:space:]]name:[[:space:]]*" name "$" {found=1; print; next}
        found && $0 ~ "^[[:space:]]*-[[:space:]]name:" {exit}
        found && $0 ~ "^[^[:space:]]" {exit}
        found {print}
    ' "$CATALOG"
}
read_zone_block_anywhere(){ local b; b="$(read_zone_block_from_section zones "$1")"; [[ -n "$b" ]] && { printf '%s\n' "$b"; return 0; }; b="$(read_zone_block_from_section disabled_zones "$1")"; [[ -n "$b" ]] && { printf '%s\n' "$b"; return 0; }; return 1; }

remove_zone_from_section(){
    local section="$1" name="$2" out; out="$(tmp_file)"
    awk -v section="$section" -v name="$name" '
        /^zones:/ {current="zones"; print; next}
        /^disabled_zones:/ {current="disabled_zones"; print; next}
        current == section && $0 ~ "^[[:space:]]*-[[:space:]]name:[[:space:]]*" name "$" {skip=1; next}
        skip && $0 ~ "^[[:space:]]*-[[:space:]]name:" {skip=0}
        skip && $0 ~ "^[^[:space:]]" {skip=0}
        !skip {print}
    ' "$CATALOG" > "$out"
    mv "$out" "$CATALOG"
}
ensure_section(){ grep -q "^$1:" "$CATALOG" || printf '\n%s:\n' "$1" >> "$CATALOG"; }
append_block_to_section(){
    local section="$1" block="$2" out; out="$(tmp_file)"; ensure_section "$section"
    awk -v section="$section" -v block="$block" '
        BEGIN{inserted=0}
        {print; if($0 == section ":" && inserted==0){print ""; print block; inserted=1}}
    ' "$CATALOG" > "$out"
    mv "$out" "$CATALOG"
}
render_zone_block(){
    local name="$1" type="$2" views="$3" cluster="$4" dnssec="$5" acl_external="$6" acl_internal="$7" acl_partner="$8" view
    validate_zone_name "$name"; validate_type "$type"; validate_views "$views"; validate_dnssec "$dnssec"
    echo "  - name: $name"; echo "    type: $type"
    [[ -n "$cluster" ]] && echo "    cluster: $cluster"
    [[ -n "$dnssec" ]] && echo "    dnssec: $dnssec"
    echo "    views:"
    while IFS= read -r view; do [[ -z "$view" ]] && continue; echo "      - $view"; done < <(normalize_views "$views")
    echo "    acl:"
    while IFS= read -r view; do
        [[ -z "$view" ]] && continue
        case "$view" in
            external) echo "      external: ${acl_external:-any;}" ;;
            internal) echo "      internal: ${acl_internal:-recursive_clients;}" ;;
            partner) echo "      partner: ${acl_partner:-partner_clients;}" ;;
        esac
    done < <(normalize_views "$views")
}
regenerate_catalog(){ "$PROJECT_ROOT/src/tools/generate-zone-catalog.sh" "$CATALOG" >/dev/null; }
parse_args(){
    NAME=""; TYPE=""; VIEWS=""; CLUSTER=""; DNSSEC=""; ACL_EXTERNAL=""; ACL_INTERNAL=""; ACL_PARTNER=""; FORCE="no"
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --name) NAME="$2"; shift 2;; --type) TYPE="$2"; shift 2;; --views) VIEWS="$2"; shift 2;; --cluster) CLUSTER="$2"; shift 2;; --dnssec) DNSSEC="$2"; shift 2;; --acl-external) ACL_EXTERNAL="$2"; shift 2;; --acl-internal) ACL_INTERNAL="$2"; shift 2;; --acl-partner) ACL_PARTNER="$2"; shift 2;; --force) FORCE="yes"; shift;; *) fatal "Unknown argument: $1";;
        esac
    done
}
cmd_list(){ require_catalog; awk '/^zones:/ {section="enabled"; next} /^disabled_zones:/ {section="disabled"; next} /^[[:space:]]*-[[:space:]]name:/ {print section " " $3}' "$CATALOG"; }
cmd_read(){ parse_args "$@"; validate_zone_name "$NAME"; read_zone_block_anywhere "$NAME" || fatal "Zone not found: $NAME"; }
cmd_create(){ parse_args "$@"; require_catalog; validate_zone_name "$NAME"; validate_type "$TYPE"; validate_views "$VIEWS"; zone_exists_anywhere "$NAME" && fatal "Zone already exists: $NAME"; local block; block="$(render_zone_block "$NAME" "$TYPE" "$VIEWS" "$CLUSTER" "$DNSSEC" "$ACL_EXTERNAL" "$ACL_INTERNAL" "$ACL_PARTNER")"; append_block_to_section zones "$block"; regenerate_catalog; echo "Zone created: $NAME"; }
cmd_update(){ parse_args "$@"; require_catalog; validate_zone_name "$NAME"; zone_exists_in_section zones "$NAME" || fatal "Enabled zone not found: $NAME"; [[ -n "$TYPE" ]] || TYPE="master"; [[ -n "$VIEWS" ]] || VIEWS="external"; local block; block="$(render_zone_block "$NAME" "$TYPE" "$VIEWS" "$CLUSTER" "$DNSSEC" "$ACL_EXTERNAL" "$ACL_INTERNAL" "$ACL_PARTNER")"; remove_zone_from_section zones "$NAME"; append_block_to_section zones "$block"; regenerate_catalog; echo "Zone updated: $NAME"; }
cmd_disable(){ parse_args "$@"; require_catalog; validate_zone_name "$NAME"; zone_exists_in_section zones "$NAME" || fatal "Enabled zone not found: $NAME"; local block; block="$(read_zone_block_from_section zones "$NAME")"; remove_zone_from_section zones "$NAME"; append_block_to_section disabled_zones "$block"; regenerate_catalog; echo "Zone disabled: $NAME"; }
cmd_enable(){ parse_args "$@"; require_catalog; validate_zone_name "$NAME"; zone_exists_in_section disabled_zones "$NAME" || fatal "Disabled zone not found: $NAME"; local block; block="$(read_zone_block_from_section disabled_zones "$NAME")"; remove_zone_from_section disabled_zones "$NAME"; append_block_to_section zones "$block"; regenerate_catalog; echo "Zone enabled: $NAME"; }
cmd_delete(){ parse_args "$@"; require_catalog; validate_zone_name "$NAME"; [[ "$FORCE" == yes ]] || fatal "Delete requires --force"; remove_zone_from_section zones "$NAME"; remove_zone_from_section disabled_zones "$NAME"; regenerate_catalog; echo "Zone deleted: $NAME"; }
case "${1:-}" in list) shift; cmd_list "$@";; read) shift; cmd_read "$@";; create) shift; cmd_create "$@";; update) shift; cmd_update "$@";; disable) shift; cmd_disable "$@";; enable) shift; cmd_enable "$@";; delete) shift; cmd_delete "$@";; -h|--help|help|"") usage;; *) fatal "Unknown command: $1";; esac
