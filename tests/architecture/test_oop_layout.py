from __future__ import annotations

from pathlib import Path

from dnsforge.application.initialize.initialize_proxy import InitializeProxy
from dnsforge.application.validate.validate_proxy import ValidateProxy
from dnsforge.domain.model.proxy_type import ProxyType
from dnsforge.infrastructure.settings.env_loader import EnvSettingsLoader

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_project_has_expected_oop_ddd_layout() -> None:
    assert (PROJECT_ROOT / "pyproject.toml").is_file()
    assert (PROJECT_ROOT / "src/dnsforge/domain").is_dir()
    assert (PROJECT_ROOT / "src/dnsforge/application").is_dir()
    assert (PROJECT_ROOT / "src/dnsforge/infrastructure").is_dir()
    assert (PROJECT_ROOT / "src/dnsforge/interfaces/cli").is_dir()


def test_core_ddd_components_are_importable() -> None:
    assert InitializeProxy is not None
    assert ValidateProxy is not None
    assert EnvSettingsLoader is not None
    assert ProxyType.from_value("forwarder") is ProxyType.FORWARDER
