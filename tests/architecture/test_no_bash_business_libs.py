from __future__ import annotations

import re
from pathlib import Path

from dnsforge.domain.settings.boolean import BooleanSetting
from dnsforge.infrastructure.bind.bind_tools import BindTools
from dnsforge.infrastructure.network.address_parser import AddressListParser
from dnsforge.infrastructure.runtime.command_runner import CommandRunner
from dnsforge.infrastructure.runtime.file_ops import AtomicFileWriter, BackupFile
from dnsforge.infrastructure.system.service_manager import ServiceManager

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_no_src_libs_directory() -> None:
    assert not (PROJECT_ROOT / "src/libs").exists()


def test_python_replacements_for_legacy_bash_libs_are_importable() -> None:
    assert BooleanSetting.parse("yes") is True
    assert BooleanSetting.parse("no") is False
    assert AddressListParser().parse("10.0.0.1; 10.0.0.2,10.0.0.3 10.0.0.4") == [
        "10.0.0.1",
        "10.0.0.2",
        "10.0.0.3",
        "10.0.0.4",
    ]
    assert CommandRunner is not None
    assert AtomicFileWriter is not None
    assert BackupFile is not None
    assert ServiceManager is not None
    assert BindTools is not None


def test_product_code_does_not_reference_legacy_shell_libs() -> None:
    pattern = re.compile(r"src/libs|source .*lib-.*\.sh|lib-[a-zA-Z0-9_-]+\.sh", re.IGNORECASE)
    offenders = []
    for path in (PROJECT_ROOT / "src/dnsforge").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if pattern.search(text):
            offenders.append(str(path.relative_to(PROJECT_ROOT)))
    assert offenders == []
