from dnsforge.application.events.event_bus import RecordingEventBus
from dnsforge.domain.events.model import AuditEvent
from dnsforge.infrastructure.audit.event_repository import AuditEventRepository


def test_event_bus_records_and_dispatches_events():
    bus = RecordingEventBus()
    seen = []
    bus.subscribe(seen.append)

    event = bus.publish(AuditEvent(event_type="ZoneCreated", category="zone", subject="example.org", message="created"))

    assert bus.events == [event]
    assert seen == [event]


def test_audit_event_repository_is_append_only_jsonl(tmp_path):
    repo = AuditEventRepository(tmp_path / "audit-events.jsonl")
    repo.append(AuditEvent(event_type="ClusterAuditCompleted", category="cluster", message="ok"))
    repo.append(AuditEvent(event_type="ZoneCreated", category="zone", message="created"))

    assert [event.category for event in repo.list()] == ["cluster", "zone"]
    assert [event.event_type for event in repo.list(category="zone")] == ["ZoneCreated"]
