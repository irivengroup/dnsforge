from __future__ import annotations

import sys

from dnsforge.application.readiness import ReadinessService
from dnsforge.application.readiness.checks.initialization import InitializationCheck
from dnsforge.application.readiness.checks.platform_support import PlatformSupportCheck
from dnsforge.application.readiness.checks.python_version import PythonVersionCheck
from dnsforge.application.readiness.checks.repositories import BackupRepositoryCheck, HistoryRepositoryCheck
from dnsforge.domain.readiness import ReadinessReport, ReadinessResult, ReadinessStatus
from dnsforge.infrastructure.filesystem.paths import ProjectPaths


class ExplodingCheck:
    name = "Exploding"
    critical = False

    def run(self) -> ReadinessResult:
        raise RuntimeError("boom")


class CriticalWarningCheck:
    name = "Warning"
    critical = True

    def run(self) -> ReadinessResult:
        return ReadinessResult(self.name, ReadinessStatus.WARNING, "warn", critical=True)


def test_readiness_service_isolates_check_exceptions(tmp_path) -> None:
    report = ReadinessService(ProjectPaths(tmp_path), checks=[ExplodingCheck()]).run()

    assert report.overall_label == "WARNING"
    assert report.checks[0].status is ReadinessStatus.FAILED
    assert report.checks[0].critical is False
    assert "boom" in report.checks[0].message


def test_readiness_report_warning_and_empty_score() -> None:
    warning_report = ReadinessReport([ReadinessResult("optional", ReadinessStatus.WARNING, "warn")])
    assert warning_report.overall_status is ReadinessStatus.WARNING
    assert warning_report.overall_label == "WARNING"
    assert warning_report.score == 50
    assert warning_report.as_dict()["overall_status"] == "WARNING"

    empty_report = ReadinessReport([])
    assert empty_report.overall_label == "READY"
    assert empty_report.score == 0


def test_initialization_check_pass_warn_and_fail(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("DNSFORGE_CONFIG_ROOT", str(tmp_path / "etc" / "dnsforge"))
    monkeypatch.setenv("DNSFORGE_SETUP_FILE", str(tmp_path / "etc" / "dnsforge" / "setup.conf"))
    paths = ProjectPaths(tmp_path)
    paths.settings_root.mkdir(parents=True)

    result = InitializationCheck(paths).run()
    assert result.status is ReadinessStatus.FAILED

    paths.setup_file.write_text("PROFILE=authoritative\n", encoding="utf-8")
    result = InitializationCheck(paths).run()
    assert result.status is ReadinessStatus.WARNING
    assert result.critical is False

    (paths.settings_root / ".initialized.conf.lock").write_text("initialized\n", encoding="utf-8")
    result = InitializationCheck(paths).run()
    assert result.status is ReadinessStatus.PASS


def test_repository_checks_handle_directory_file_and_missing_parent(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("DNSFORGE_BACKUP_ROOT", str(tmp_path / "backups"))
    monkeypatch.setenv("DNSFORGE_HISTORY_ROOT", str(tmp_path / "backups" / "history"))
    paths = ProjectPaths(tmp_path)
    result = BackupRepositoryCheck(paths).run()
    assert result.status is ReadinessStatus.PASS

    paths.backup_root.write_text("not a directory", encoding="utf-8")
    result = BackupRepositoryCheck(paths).run()
    assert result.status is ReadinessStatus.FAILED

    monkeypatch.setenv("DNSFORGE_HISTORY_ROOT", str(tmp_path / "missing" / "history"))
    missing_paths = ProjectPaths(tmp_path / "missing")
    result = HistoryRepositoryCheck(missing_paths).run()
    assert result.status is ReadinessStatus.FAILED

    missing_paths.history_root.mkdir(parents=True)
    result = HistoryRepositoryCheck(missing_paths).run()
    assert result.status is ReadinessStatus.PASS


def test_python_version_check_failure_and_pass(monkeypatch) -> None:
    monkeypatch.setattr(sys, "version_info", (3, 8, 20, "final", 0))
    result = PythonVersionCheck((3, 9)).run()
    assert result.status is ReadinessStatus.FAILED
    assert "below supported minimum" in result.message

    monkeypatch.setattr(sys, "version_info", (3, 11, 15, "final", 0))
    result = PythonVersionCheck((3, 9)).run()
    assert result.status is ReadinessStatus.PASS


def test_platform_support_unknown_missing_and_bad_version(tmp_path) -> None:
    missing = tmp_path / "missing-os-release"
    result = PlatformSupportCheck(missing).run()
    assert result.status is ReadinessStatus.FAILED
    assert "unsupported platform" in result.message

    os_release = tmp_path / "os-release"
    os_release.write_text('ID="ubuntu"\nVERSION_ID="jammy"\n', encoding="utf-8")
    result = PlatformSupportCheck(os_release).run()
    assert result.status is ReadinessStatus.WARNING

    os_release.write_text('# comment\nID="oracle"\nID_LIKE="rhel fedora"\nVERSION_ID="8.8"\n', encoding="utf-8")
    result = PlatformSupportCheck(os_release).run()
    assert result.status is ReadinessStatus.PASS
