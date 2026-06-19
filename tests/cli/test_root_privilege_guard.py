from __future__ import annotations

import pytest

from dnsforge.infrastructure.system.privilege_guard import RootPrivilegeGuard
from dnsforge.interfaces.cli.application import DnsForgeCli


class _NonRootGuard(RootPrivilegeGuard):
    def is_root(self) -> bool:
        return False


class _RootGuard(RootPrivilegeGuard):
    def is_root(self) -> bool:
        return True


class _Dispatcher:
    def dispatch(self, _args) -> int:
        return 0


def test_dnsforge_non_version_command_requires_root(capsys: pytest.CaptureFixture[str]) -> None:
    cli = DnsForgeCli(dispatcher=_Dispatcher(), privilege_guard=_NonRootGuard())

    result = cli.run(["status"])

    captured = capsys.readouterr()
    assert result == 1
    assert "require elevated privileges" in captured.err
    assert "sudo" in captured.err


def test_dnsforge_help_remains_available_without_root(capsys: pytest.CaptureFixture[str]) -> None:
    cli = DnsForgeCli(dispatcher=_Dispatcher(), privilege_guard=_NonRootGuard())

    with pytest.raises(SystemExit) as exc:
        cli.run(["--help"])

    captured = capsys.readouterr()
    assert exc.value.code == 0
    assert "DNSForge" in captured.out


def test_dnsforge_version_runs_without_root() -> None:
    cli = DnsForgeCli(dispatcher=_Dispatcher(), privilege_guard=_NonRootGuard())

    assert cli.run(["version"]) == 0


def test_dnsforge_command_runs_when_root() -> None:
    cli = DnsForgeCli(dispatcher=_Dispatcher(), privilege_guard=_RootGuard())

    assert cli.run(["status"]) == 0
