#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

test ! -d "${PROJECT_ROOT}/src/libs"

PYTHONPATH="${PROJECT_ROOT}/src" python3 - <<'PY'
from dnsforge.domain.settings.boolean import BooleanSetting
from dnsforge.infrastructure.network.address_parser import AddressListParser
from dnsforge.infrastructure.runtime.command_runner import CommandRunner
from dnsforge.infrastructure.runtime.file_ops import AtomicFileWriter, BackupFile
from dnsforge.infrastructure.system.service_manager import ServiceManager
from dnsforge.infrastructure.bind.bind_tools import BindTools

assert BooleanSetting.parse("yes") is True
assert BooleanSetting.parse("no") is False
assert AddressListParser().parse('10.0.0.1; 10.0.0.2,10.0.0.3 10.0.0.4') == ["10.0.0.1","10.0.0.2","10.0.0.3","10.0.0.4"]
assert CommandRunner is not None
assert AtomicFileWriter is not None
assert BackupFile is not None
assert ServiceManager is not None
assert BindTools is not None
PY

if grep -RniE 'src/libs|source .*lib-.*\.sh|lib-[a-zA-Z0-9_-]+\.sh' "${PROJECT_ROOT}/src/dnsforge" >/tmp/dnsforge-lib-grep.txt; then
  cat /tmp/dnsforge-lib-grep.txt
  exit 1
fi

echo "dnsforge no bash libs validation OK"
