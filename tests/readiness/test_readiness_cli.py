from __future__ import annotations

from dnsforge.domain.readiness import ReadinessReport, ReadinessResult, ReadinessStatus
from dnsforge.interfaces.cli.application import DnsForgeCli


class NoRootGuard:
    def require_root(self) -> None:
        return None


def test_readiness_cli_renders_text(monkeypatch, capsys, tmp_path) -> None:
    report = ReadinessReport([ReadinessResult("Platform Support", ReadinessStatus.PASS, "ok", True)])
    monkeypatch.setattr("dnsforge.interfaces.cli.application.ReadinessService.run", lambda self: report)

    code = DnsForgeCli(privilege_guard=NoRootGuard()).run(["--project-root", str(tmp_path), "readiness"])

    assert code == 0
    assert "OVERALL STATUS : READY" in capsys.readouterr().out


def test_readiness_cli_returns_non_zero_on_failed_critical_check(monkeypatch, tmp_path) -> None:
    report = ReadinessReport([ReadinessResult("Platform Support", ReadinessStatus.FAILED, "bad", True)])
    monkeypatch.setattr("dnsforge.interfaces.cli.application.ReadinessService.run", lambda self: report)

    code = DnsForgeCli(privilege_guard=NoRootGuard()).run(["--project-root", str(tmp_path), "readiness"])

    assert code == 1
