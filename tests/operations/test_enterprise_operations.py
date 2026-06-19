from __future__ import annotations

import json

from dnsforge.application.drift.drift_service import DriftService
from dnsforge.application.events.event_tail_service import EventTailService
from dnsforge.application.health.score_service import HealthScoreService
from dnsforge.application.security.dnssec_policy_service import DnssecPolicyService
from dnsforge.domain.events.model import AuditEvent
from dnsforge.infrastructure.audit.event_repository import AuditEventRepository
from dnsforge.infrastructure.filesystem.paths import ProjectPaths


def test_health_score_json_contract(tmp_path, monkeypatch):
    setup = tmp_path / "setup.conf"
    setup.write_text("ROLE=authoritative\nNODE_NAME=dns01\n", encoding="utf-8")
    monkeypatch.setenv("DNSFORGE_SETUP_FILE", str(setup))

    rendered = HealthScoreService().render(ProjectPaths(tmp_path), output_format="json")
    data = json.loads(rendered)

    assert "score" in data
    assert "categories" in data


def test_dnssec_policy_apply_and_show(tmp_path):
    service = DnssecPolicyService(tmp_path / "dnssec-policy.json")

    assert "zsk_rotation_days" in service.show()
    assert "zsk=45d" in service.apply(zsk_rotation_days=45, ksk_rotation_days=400)
    assert json.loads(service.show())["ksk_rotation_days"] == 400


def test_events_tail_reads_audit_repository(tmp_path):
    event_log = tmp_path / "events.jsonl"
    repository = AuditEventRepository(event_log)
    repository.append(AuditEvent("ZoneCreated", "zone", "created example.com", subject="example.com"))

    output = EventTailService(event_log).tail(limit=5)

    assert "ZoneCreated" in output
    assert "example.com" in output


def test_drift_audit_reports_missing_target(tmp_path):
    paths = ProjectPaths(tmp_path)
    rendered = paths.render_root / "named.conf"
    rendered.parent.mkdir(parents=True)
    rendered.write_text("options {};\n", encoding="utf-8")

    ok, output = DriftService(paths).audit(target_root=tmp_path / "target")

    assert not ok
    assert "MISSING" in output
