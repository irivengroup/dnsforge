from __future__ import annotations

from pathlib import Path

from dnsforge.application.initialize.initialize_command import InitializeCommand
from dnsforge.domain.profile.model import ConfigurationProfile
from dnsforge.infrastructure.bind.layout import BindLayoutDetector
from dnsforge.infrastructure.profile.setup_profile_generator import SetupProfileGenerator
from dnsforge.infrastructure.filesystem.paths import ProjectPaths
from dnsforge.infrastructure.profile.setup_template_service import ProfileSetupTemplateService


class _Renderer:
    def __init__(self) -> None:
        self.calls: list[tuple[str, object | None]] = []

    def execute(self, node: str, proxy_type: object | None = None) -> None:
        self.calls.append((node, proxy_type))


class _InitializeService:
    def assert_not_initialized(self, setup_file: Path) -> None:
        return None

    def apply(self, *args, **kwargs) -> None:
        return None


def test_profile_setup_conf_is_generated_from_profile_policy() -> None:
    service = ProfileSetupTemplateService()

    assert 'ROLE="dns-authoritative"' in service.template_text(ConfigurationProfile.AUTHORITATIVE)
    assert 'PROXY_TYPE="forwarder"' in service.template_text(ConfigurationProfile.PROXY_FORWARDER)
    assert 'PROXY_TYPE="hybrid"' in service.template_text(ConfigurationProfile.PROXY_HYBRID)


def test_proxy_templates_use_distributed_peer_and_nic_variables() -> None:
    service = ProfileSetupTemplateService()
    for profile in (ConfigurationProfile.PROXY_FORWARDER, ConfigurationProfile.PROXY_HYBRID):
        text = service.template_text(profile)
        assert "BIND_EXTERNET_NICNAME" in text
        assert "BIND_INTRANET_NICNAME" in text
        assert "BIND_ADMIN_NICNAME" in text
        assert "PEER_AUTHORITATIVE_ADDRESSES" in text
        assert "PEER_PROXY_ADDRESSES" in text
        assert "FRONT_IP" not in text
        assert "BACK_IP" not in text
        assert "ADM_IP" not in text
        assert "AUTHORITATIVE_BACK_IP" not in text
        assert "PROXY_VIP_FRONT_IP" not in text
        assert "PROXY_KEEPALIVED_INTERFACE" not in text


def test_install_tree_no_longer_owns_profile_templates() -> None:
    assert not Path("install/templates").exists()


def test_initialize_consumes_existing_authoritative_setup_conf(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("DNSFORGE_CONFIG_ROOT", str(tmp_path / "etc/dnsforge"))
    monkeypatch.setenv("DNSFORGE_BACKUP_ROOT", str(tmp_path / "backups"))
    paths = ProjectPaths(tmp_path)
    paths.setup_file.parent.mkdir(parents=True, exist_ok=True)
    paths.setup_file.write_text('ROLE="dns-authoritative"\nNODE_NAME="auth01"\n', encoding="utf-8")
    renderer = _Renderer()

    InitializeCommand(paths, authoritative_renderer=renderer, service=_InitializeService()).execute(render_only=True)

    assert renderer.calls == [("auth01", None)]
    assert 'ROLE="dns-authoritative"' in paths.setup_file.read_text(encoding="utf-8")


def test_initialize_consumes_existing_proxy_setup_conf(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("DNSFORGE_CONFIG_ROOT", str(tmp_path / "etc/dnsforge"))
    monkeypatch.setenv("DNSFORGE_BACKUP_ROOT", str(tmp_path / "backups"))
    paths = ProjectPaths(tmp_path)
    paths.setup_file.parent.mkdir(parents=True, exist_ok=True)
    paths.setup_file.write_text('ROLE="dns-proxy"\nNODE_NAME="proxy01"\nPROXY_TYPE="hybrid"\n', encoding="utf-8")
    renderer = _Renderer()

    InitializeCommand(paths, proxy_renderer=renderer, service=_InitializeService()).execute(render_only=True)

    assert len(renderer.calls) == 1
    assert renderer.calls[0][0] == "proxy01"
    assert 'PROXY_TYPE="hybrid"' in paths.setup_file.read_text(encoding="utf-8")


def test_setup_profile_generator_uses_layered_dictionaries() -> None:
    generator = ProfileSetupTemplateService().generator

    assert "ROLE" in generator.common_setup
    assert "BIND_ADMIN_NICNAME" in generator.common_setup
    assert "PEER_AUTHORITATIVE_ADDRESSES" in generator.proxy_common_setup
    assert "VIP_BACK_IP" in generator.autoritative_setup
    assert generator.hybrid_setup["ENABLE_PROXY_MASTER_ZONES"] == "yes"
    assert generator.forwader_setup["ENABLE_PROXY_MASTER_ZONES"] == "no"

    authoritative = generator.generate(ConfigurationProfile.AUTHORITATIVE, "auth01")
    hybrid = generator.generate(ConfigurationProfile.PROXY_HYBRID, "proxy01")
    forwarder = generator.generate(ConfigurationProfile.PROXY_FORWARDER, "proxy02")

    assert 'ENABLE_CLUSTER="yes"' in authoritative
    assert 'ENABLE_PROXY_MASTER_ZONES="yes"' in hybrid
    assert 'ENABLE_PROXY_MASTER_ZONES="no"' in forwarder
    assert 'TSIG_SECRET="CHANGE_ME_BASE64"' in authoritative


def test_setup_profile_generator_uses_distribution_aware_dnssec_directory() -> None:
    detector = BindLayoutDetector()

    redhat = SetupProfileGenerator(bind_layout=detector.from_family("redhat"))
    debian = SetupProfileGenerator(bind_layout=detector.from_family("debian"))
    suse = SetupProfileGenerator(bind_layout=detector.from_family("suse"))

    assert 'DNSSEC_KEY_DIRECTORY="/var/named/dnssec"' in redhat.generate(
        ConfigurationProfile.AUTHORITATIVE,
        "auth01",
    )
    assert 'DNSSEC_KEY_DIRECTORY="/var/lib/bind/dnssec"' in debian.generate(
        ConfigurationProfile.AUTHORITATIVE,
        "auth01",
    )
    assert 'DNSSEC_KEY_DIRECTORY="/var/lib/named/dnssec"' in suse.generate(
        ConfigurationProfile.AUTHORITATIVE,
        "auth01",
    )


def test_profile_resources_are_not_packaged_or_consumed() -> None:
    assert not Path("src/dnsforge/infrastructure/profile/resources").exists()
    service = ProfileSetupTemplateService()
    assert not hasattr(service, "_RESOURCE_PACKAGE")
