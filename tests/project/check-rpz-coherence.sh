#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

template="${PROJECT_ROOT}/src/build/dns-proxy/templates/50-rpz.conf.j2"
views_template="${PROJECT_ROOT}/src/build/dns-proxy/templates/60-views.conf.j2"
render_lib="${PROJECT_ROOT}/src/libs/lib-render.sh"

test -f "${template}"

grep -q 'response-policy' "${template}"
grep -q '/etc/named/rpz/50-rpz.conf' "${views_template}"
grep -q '50-rpz.conf.j2' "${render_lib}"
grep -q '/etc/named/rpz/50-rpz.conf' "${render_lib}"

if grep -q '/etc/named/conf.d/50-rpz.conf' "${PROJECT_ROOT}/src/build/dns-proxy/templates/named.conf.j2"
then
    echo "RPZ must not be included globally from named.conf; it belongs to the recursive view." >&2
    exit 1
fi

echo "RPZ coherence validation OK"
