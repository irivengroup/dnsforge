from __future__ import annotations

import json
from pathlib import Path

from dnsforge.application.compliance import ComplianceService
from dnsforge.domain.compliance import ComplianceStatus, DriftSeverity
from dnsforge.infrastructure.filesystem.paths import ProjectPaths


def _write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _paths_with_setup(tmp_path: Path, content: str = 'ROLE="proxy"\nPROXY_TYPE="hybrid"\n') -> ProjectPaths:
    setup = tmp_path / "setup.conf"
    setup.write_text(content, encoding="utf-8")
    return ProjectPaths(tmp_path)


def test_compliance_reports_failed_when_render_tree_is_missing(tmp_path: Path) -> None:
    paths = ProjectPaths(tmp_path)

    report = ComplianceService(paths).verify(target_root=tmp_path / "target")

    assert report.status is ComplianceStatus.FAILED
    assert report.fingerprint is None
    assert len(report.drifts) == 1
    assert report.drifts[0].severity is DriftSeverity.CRITICAL
    assert str(paths.render_root) == report.drifts[0].resource


def test_drift_delegates_to_verify_for_missing_render_tree(tmp_path: Path) -> None:
    drifts = ComplianceService(ProjectPaths(tmp_path)).drift(target_root=tmp_path / "target")

    assert len(drifts) == 1
    assert drifts[0].expected_hash is None


def test_repair_plan_regenerates_when_render_tree_is_missing(tmp_path: Path) -> None:
    paths = ProjectPaths(tmp_path)

    plan = ComplianceService(paths).repair_plan(target_root=tmp_path / "target")

    assert plan.resources_to_restore == ()
    assert plan.resources_to_regenerate == (str(paths.render_root),)
    assert plan.requires_reload is True
    assert plan.requires_restart is False
    assert plan.is_empty is False


def test_render_repair_reports_empty_for_compliant_target(tmp_path: Path) -> None:
    paths = ProjectPaths(tmp_path)
    _write(paths.render_root / "etc" / "named.conf", "options {};\n")
    _write(tmp_path / "target" / "etc" / "named.conf", "options {};\n")

    output = ComplianceService(paths).render_repair(target_root=tmp_path / "target")

    assert output == "Configuration repair plan: empty"


def test_compliance_reports_compliant_when_render_matches_target(tmp_path: Path) -> None:
    paths = ProjectPaths(tmp_path)
    _write(paths.render_root / "etc" / "named.conf", "options {};\n")
    _write(tmp_path / "target" / "etc" / "named.conf", "options {};\n")

    report = ComplianceService(paths).verify(target_root=tmp_path / "target")

    assert report.is_compliant
    assert report.status is ComplianceStatus.COMPLIANT
    assert report.fingerprint is not None
    assert report.fingerprint.scope == "bind"


def test_render_verify_text_for_compliant_target(tmp_path: Path) -> None:
    paths = ProjectPaths(tmp_path)
    _write(paths.render_root / "etc" / "named.conf", "options {};\n")
    _write(tmp_path / "target" / "etc" / "named.conf", "options {};\n")

    assert (
        ComplianceService(paths).render_verify(target_root=tmp_path / "target") == "Configuration compliance: COMPLIANT"
    )


def test_render_drift_text_for_compliant_target(tmp_path: Path) -> None:
    paths = ProjectPaths(tmp_path)
    _write(paths.render_root / "etc" / "named.conf", "options {};\n")
    _write(tmp_path / "target" / "etc" / "named.conf", "options {};\n")

    assert ComplianceService(paths).render_drift(target_root=tmp_path / "target") == "No configuration drift detected"


def test_compliance_detects_changed_file_as_warning(tmp_path: Path) -> None:
    paths = ProjectPaths(tmp_path)
    _write(paths.render_root / "etc" / "named.conf", "expected\n")
    _write(tmp_path / "target" / "etc" / "named.conf", "actual\n")

    report = ComplianceService(paths).verify(target_root=tmp_path / "target")

    assert report.status is ComplianceStatus.DRIFTED
    assert len(report.drifts) == 1
    assert report.drifts[0].resource == "etc/named.conf"
    assert report.drifts[0].severity is DriftSeverity.WARNING
    assert report.drifts[0].expected_hash != report.drifts[0].actual_hash


def test_compliance_detects_missing_file_as_failed(tmp_path: Path) -> None:
    paths = ProjectPaths(tmp_path)
    _write(paths.render_root / "etc" / "named.conf", "expected\n")

    report = ComplianceService(paths).verify(target_root=tmp_path / "target")

    assert report.status is ComplianceStatus.FAILED
    assert report.drifts[0].severity is DriftSeverity.CRITICAL
    assert report.drifts[0].actual_hash is None


def test_render_drift_lists_changed_file(tmp_path: Path) -> None:
    paths = ProjectPaths(tmp_path)
    _write(paths.render_root / "etc" / "named.conf", "expected\n")
    _write(tmp_path / "target" / "etc" / "named.conf", "actual\n")

    output = ComplianceService(paths).render_drift(target_root=tmp_path / "target")

    assert "Detected configuration drift" in output
    assert "WARNING\tetc/named.conf" in output


def test_render_verify_json_contains_fingerprint_and_drifts(tmp_path: Path) -> None:
    paths = ProjectPaths(tmp_path)
    _write(paths.render_root / "etc" / "named.conf", "expected\n")
    _write(tmp_path / "target" / "etc" / "named.conf", "actual\n")

    payload = json.loads(ComplianceService(paths).render_verify(target_root=tmp_path / "target", json_output=True))

    assert payload["schema"] == ComplianceService.SCHEMA
    assert payload["status"] == "DRIFTED"
    assert payload["fingerprint"]["scope"] == "bind"
    assert payload["drifts"][0]["resource"] == "etc/named.conf"
    assert payload["drifts"][0]["severity"] == "WARNING"


def test_render_drift_json_for_missing_render_tree_has_null_fingerprint(tmp_path: Path) -> None:
    payload = json.loads(
        ComplianceService(ProjectPaths(tmp_path)).render_drift(target_root=tmp_path / "target", json_output=True)
    )

    assert payload["status"] == "FAILED"
    assert payload["fingerprint"] is None
    assert payload["drifts"][0]["expected_hash"] is None


def test_render_repair_preview_lists_restore_candidates(tmp_path: Path) -> None:
    paths = ProjectPaths(tmp_path)
    _write(paths.render_root / "etc" / "named.conf", "expected\n")

    output = ComplianceService(paths).render_repair(target_root=tmp_path / "missing", preview=True)

    assert "Configuration repair plan" in output
    assert "Would restore: etc/named.conf" in output
    assert "Requires BIND reload: yes" in output


def test_render_repair_non_preview_uses_restore_required(tmp_path: Path) -> None:
    paths = ProjectPaths(tmp_path)
    _write(paths.render_root / "etc" / "named.conf", "expected\n")
    _write(tmp_path / "target" / "etc" / "named.conf", "actual\n")

    output = ComplianceService(paths).render_repair(target_root=tmp_path / "target", preview=False)

    assert "Restore required: etc/named.conf" in output


def test_render_repair_lists_regenerate_for_missing_render_tree(tmp_path: Path) -> None:
    paths = ProjectPaths(tmp_path)

    output = ComplianceService(paths).render_repair(target_root=tmp_path / "target")

    assert f"Would regenerate: {paths.render_root}" in output


def test_fingerprint_is_stable_for_same_tree(tmp_path: Path) -> None:
    paths = ProjectPaths(tmp_path)
    _write(paths.render_root / "etc" / "named.conf", "options {};\n")

    service = ComplianceService(paths)

    assert service.fingerprint().sha256 == service.fingerprint().sha256


def test_fingerprint_for_missing_tree_uses_missing_sentinel(tmp_path: Path) -> None:
    fingerprint = ComplianceService(ProjectPaths(tmp_path)).fingerprint(scope="dnssec")

    assert fingerprint.scope == "dnssec"
    assert len(fingerprint.sha256) == 64


def test_render_fingerprint_uses_custom_scope_and_target_root(tmp_path: Path) -> None:
    target = tmp_path / "rendered"
    _write(target / "named.conf", "options {};\n")

    output = ComplianceService(ProjectPaths(tmp_path)).render_fingerprint(target_root=target, scope="views")

    assert output.startswith("views\t")
    assert len(output.split("\t")) == 3


def test_baseline_defaults_to_unknown_without_setup(tmp_path: Path) -> None:
    paths = ProjectPaths(tmp_path)
    _write(paths.render_root / "etc" / "named.conf", "options {};\n")

    baseline = ComplianceService(paths).baseline()

    assert baseline.profile == "unknown"
    assert baseline.resources == ("etc/named.conf",)
    assert baseline.bind_layout


def test_baseline_uses_role_and_proxy_type_from_setup(tmp_path: Path, monkeypatch) -> None:
    setup_file = tmp_path / "setup.conf"
    setup_file.write_text('ROLE="proxy"\nPROXY_TYPE="hybrid"\n', encoding="utf-8")
    monkeypatch.setenv("DNSFORGE_SETUP_FILE", str(setup_file))
    paths = ProjectPaths(tmp_path)
    _write(paths.render_root / "etc" / "named.conf", "options {};\n")

    baseline = ComplianceService(paths).baseline()

    assert baseline.profile == "proxy:hybrid"


def test_render_baseline_text_and_json(tmp_path: Path, monkeypatch) -> None:
    setup_file = tmp_path / "setup.conf"
    setup_file.write_text('ROLE="authoritative"\n', encoding="utf-8")
    monkeypatch.setenv("DNSFORGE_SETUP_FILE", str(setup_file))
    paths = ProjectPaths(tmp_path)
    _write(paths.render_root / "etc" / "named.conf", "options {};\n")

    service = ComplianceService(paths)
    text_output = service.render_baseline()
    json_output = json.loads(service.render_baseline(json_output=True))

    assert "Profile: authoritative" in text_output
    assert "Resources: 1" in text_output
    assert "- etc/named.conf" in text_output
    assert json_output["schema"] == ComplianceService.SCHEMA
    assert json_output["profile"] == "authoritative"
    assert json_output["resources"] == ["etc/named.conf"]


def test_tree_hash_changes_when_file_content_changes(tmp_path: Path) -> None:
    paths = ProjectPaths(tmp_path)
    config = _write(paths.render_root / "named.conf", "one\n")
    service = ComplianceService(paths)
    first = service.fingerprint().sha256

    config.write_text("two\n", encoding="utf-8")

    assert service.fingerprint().sha256 != first
