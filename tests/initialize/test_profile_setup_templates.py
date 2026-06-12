from __future__ import annotations

from pathlib import Path

from dnsforge.domain.profile.model import ConfigurationProfile
from dnsforge.infrastructure.filesystem.paths import ProjectPaths
from dnsforge.infrastructure.profile.setup_template_service import ProfileSetupTemplateService
from dnsforge.application.initialize.initialize_authoritative import InitializeAuthoritative
from dnsforge.application.initialize.initialize_proxy import InitializeProxy
from dnsforge.domain.model.proxy_type import ProxyType


class _Renderer:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str | None]] = []

    def execute(self, node: str, proxy_type: ProxyType | None = None) -> None:
        self.calls.append((node, proxy_type.value if proxy_type else None))


class _InitializeService:
    def assert_not_initialized(self, setup_file: Path) -> None:
        return None

    def apply(self, *args, **kwargs) -> None:
        return None


def test_profile_setup_templates_are_package_resources() -> None:
    service = ProfileSetupTemplateService()

    assert 'ROLE="dns-authoritative"' in service.template_text(ConfigurationProfile.AUTHORITATIVE)
    assert 'PROXY_TYPE="forwarder"' in service.template_text(ConfigurationProfile.PROXY_FORWARDER)
    assert 'PROXY_TYPE="hybrid"' in service.template_text(ConfigurationProfile.PROXY_HYBRID)


def test_install_tree_no_longer_owns_profile_templates() -> None:
    assert not Path("install/templates").exists()


def test_authoritative_initialize_creates_setup_conf_from_project_resource(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("DNSFORGE_CONFIG_ROOT", str(tmp_path / "etc/dnsforge"))
    monkeypatch.setenv("DNSFORGE_BACKUP_ROOT", str(tmp_path / "backups"))
    paths = ProjectPaths(tmp_path)
    renderer = _Renderer()

    InitializeAuthoritative(paths, renderer=renderer, service=_InitializeService()).execute("auth01", render_only=True)

    content = paths.setup_file.read_text(encoding="utf-8")
    assert 'ROLE="dns-authoritative"' in content
    assert 'NODE_NAME="auth01"' in content
    assert "PROXY_TYPE" not in content


def test_proxy_initialize_creates_hybrid_setup_conf_by_default(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("DNSFORGE_CONFIG_ROOT", str(tmp_path / "etc/dnsforge"))
    monkeypatch.setenv("DNSFORGE_BACKUP_ROOT", str(tmp_path / "backups"))
    paths = ProjectPaths(tmp_path)
    renderer = _Renderer()

    InitializeProxy(paths, renderer=renderer, service=_InitializeService()).execute(
        "proxy01", ProxyType.HYBRID, render_only=True
    )

    content = paths.setup_file.read_text(encoding="utf-8")
    assert 'ROLE="dns-proxy"' in content
    assert 'PROXY_TYPE="hybrid"' in content
    assert 'NODE_NAME="proxy01"' in content
