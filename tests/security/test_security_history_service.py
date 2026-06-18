from __future__ import annotations

from pathlib import Path

import pytest

from dnsforge.application.security.security_history_service import SecurityHistoryService
from dnsforge.shared.errors import SettingsError


def test_security_history_lists_indexed_entries(tmp_path: Path) -> None:
    service = SecurityHistoryService(tmp_path)
    first = service.record("audit", "initial baseline")

    output = service.history()

    assert "Security history" in output
    assert "1\t" in output
    assert first.name in output


def test_security_rollback_requires_existing_history(tmp_path: Path) -> None:
    service = SecurityHistoryService(tmp_path)

    with pytest.raises(SettingsError, match="requires at least one"):
        service.rollback()


def test_security_rollback_creates_auditable_marker(tmp_path: Path) -> None:
    service = SecurityHistoryService(tmp_path)
    selected = service.record("audit", "baseline")

    output = service.rollback("1")

    assert "Security rollback marker created" in output
    assert selected.name in output
    assert len(list(tmp_path.glob("*.log"))) == 2


def test_security_rollback_rejects_unknown_version(tmp_path: Path) -> None:
    service = SecurityHistoryService(tmp_path)
    service.record("audit", "baseline")

    with pytest.raises(SettingsError, match="entry not found"):
        service.rollback("999")
