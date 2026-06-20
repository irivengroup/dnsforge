from pathlib import Path

from dnsforge.application.compliance import ComplianceService
from dnsforge.infrastructure.filesystem.paths import ProjectPaths


def test_compliance_reports_compliant_when_render_matches_target(tmp_path: Path) -> None:
    paths = ProjectPaths(tmp_path)
    rendered = paths.render_root / "etc" / "named.conf"
    rendered.parent.mkdir(parents=True)
    rendered.write_text("options {};\n", encoding="utf-8")
    target = tmp_path / "target"
    deployed = target / "etc" / "named.conf"
    deployed.parent.mkdir(parents=True)
    deployed.write_text("options {};\n", encoding="utf-8")

    report = ComplianceService(paths).verify(target_root=target)

    assert report.is_compliant
    assert report.status.value == "COMPLIANT"


def test_compliance_detects_changed_file(tmp_path: Path) -> None:
    paths = ProjectPaths(tmp_path)
    rendered = paths.render_root / "etc" / "named.conf"
    rendered.parent.mkdir(parents=True)
    rendered.write_text("expected\n", encoding="utf-8")
    target = tmp_path / "target"
    deployed = target / "etc" / "named.conf"
    deployed.parent.mkdir(parents=True)
    deployed.write_text("actual\n", encoding="utf-8")

    output = ComplianceService(paths).render_drift(target_root=target)

    assert "Detected configuration drift" in output
    assert "etc/named.conf" in output


def test_compliance_repair_preview_lists_restore_candidates(tmp_path: Path) -> None:
    paths = ProjectPaths(tmp_path)
    rendered = paths.render_root / "etc" / "named.conf"
    rendered.parent.mkdir(parents=True)
    rendered.write_text("expected\n", encoding="utf-8")

    output = ComplianceService(paths).render_repair(target_root=tmp_path / "missing", preview=True)

    assert "Configuration repair plan" in output
    assert "Would restore: etc/named.conf" in output


def test_fingerprint_is_stable_for_same_tree(tmp_path: Path) -> None:
    paths = ProjectPaths(tmp_path)
    rendered = paths.render_root / "etc" / "named.conf"
    rendered.parent.mkdir(parents=True)
    rendered.write_text("options {};\n", encoding="utf-8")

    service = ComplianceService(paths)

    assert service.fingerprint().sha256 == service.fingerprint().sha256
