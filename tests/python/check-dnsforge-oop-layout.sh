#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

test -f "${PROJECT_ROOT}/pyproject.toml"
test -d "${PROJECT_ROOT}/src/dnsforge/domain"
test -d "${PROJECT_ROOT}/src/dnsforge/application"
test -d "${PROJECT_ROOT}/src/dnsforge/infrastructure"
test -d "${PROJECT_ROOT}/src/dnsforge/interfaces/cli"

PYTHONPATH="${PROJECT_ROOT}/src" python3 - <<'PY'
from dnsforge.application.initialize.initialize_proxy import InitializeProxy
from dnsforge.application.validate.validate_proxy import ValidateProxy
from dnsforge.domain.model.proxy_type import ProxyType
from dnsforge.infrastructure.settings.env_loader import EnvSettingsLoader

assert InitializeProxy is not None
assert ValidateProxy is not None
assert EnvSettingsLoader is not None
assert ProxyType.from_value("forwarder") is ProxyType.FORWARDER
PY

echo "dnsforge OOP layout validation OK"
