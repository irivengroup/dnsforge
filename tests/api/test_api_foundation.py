from dnsforge.api import CatalogApi, ClusterApi, DisasterRecoveryApi, DnsForgeApplicationApi, DnssecApi, MigrationApi, ZoneApi
from dnsforge.application.events.event_bus import RecordingEventBus
from dnsforge.infrastructure.filesystem.paths import ProjectPaths


def test_application_api_exposes_stable_facades(tmp_path, monkeypatch):
    monkeypatch.setenv("DNSFORGE_CONFIG_ROOT", str(tmp_path / "etc"))
    monkeypatch.setenv("DNSFORGE_ZONE_CATALOG", str(tmp_path / "etc" / "zones.yml"))
    api = DnsForgeApplicationApi(ProjectPaths(tmp_path), event_bus=RecordingEventBus())

    assert isinstance(api.zones, ZoneApi)
    assert isinstance(api.catalog, CatalogApi)
    assert isinstance(api.disaster, DisasterRecoveryApi)
    assert isinstance(api.migration, MigrationApi)
    assert isinstance(api.cluster(tmp_path / "setup.conf"), ClusterApi)
    assert isinstance(api.dnssec(tmp_path / "setup.conf"), DnssecApi)


def test_zone_api_publishes_audit_event_on_create(tmp_path, monkeypatch):
    monkeypatch.setenv("DNSFORGE_CONFIG_ROOT", str(tmp_path / "etc"))
    monkeypatch.setenv("DNSFORGE_ZONE_CATALOG", str(tmp_path / "etc" / "zones.yml"))
    paths = ProjectPaths(tmp_path)
    bus = RecordingEventBus()
    api = ZoneApi(paths, event_bus=bus)

    api.create_zone(
        "example.org.",
        "master",
        ["internal"],
        reason="initial zone creation",
        business_owner="apps",
        technical_owner="dns",
        environment="prod",
        classification="internal",
        lifecycle="draft",
    )

    assert bus.events[-1].event_type == "ZoneCreated"
    assert bus.events[-1].category == "zone"
    assert bus.events[-1].subject == "example.org."
