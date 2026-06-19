from __future__ import annotations

import importlib.util
from pathlib import Path

from dnsforge.interfaces.api import DnsForgeApplicationApi


def test_agent_api_facades_live_under_interfaces() -> None:
    assert DnsForgeApplicationApi.__module__ == "dnsforge.interfaces.api.facade"


def test_legacy_top_level_api_package_is_removed() -> None:
    assert not Path("src/dnsforge/api").exists()
    assert importlib.util.find_spec("dnsforge.api") is None
