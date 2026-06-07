#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LIB_DIR="${PROJECT_ROOT}/src/libs"
source "${LIB_DIR}/lib-logging.sh"
source "${LIB_DIR}/lib-rndc.sh"
usage(){ cat <<'EOF'
Usage:
  rndc-secret.sh show   --role <dns-proxy|dns-authoritative> --node <node>
  rndc-secret.sh ensure --role <dns-proxy|dns-authoritative> --node <node>
  rndc-secret.sh rotate --role <dns-proxy|dns-authoritative> --node <node>
EOF
}
cmd="${1:-}"; shift || true
ROLE=""; NODE_NAME=""
while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --role) ROLE="$2"; shift 2 ;;
    --node) NODE_NAME="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 1 ;;
  esac
done
[[ -n "${ROLE}" ]] || { echo "--role is required" >&2; exit 1; }
[[ -n "${NODE_NAME}" ]] || { echo "--node is required" >&2; exit 1; }
export PROJECT_ROOT ROLE NODE_NAME
case "${cmd}" in
  ensure) ensure_rndc_secret; rndc_secret_file_for_node "${NODE_NAME}" ;;
  show) ensure_rndc_secret >/dev/null; rndc_secret_file_for_node "${NODE_NAME}" ;;
  rotate) rotate_rndc_secret ;;
  *) usage; exit 1 ;;
esac
