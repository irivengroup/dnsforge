#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

bash "${PROJECT_ROOT}/tests/project/check-template-usage.sh"
bash "${PROJECT_ROOT}/tests/project/check-rpz-coherence.sh"

echo "Project coherence validation OK"
