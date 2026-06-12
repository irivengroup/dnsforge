from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from dnsforge.domain.model.proxy_type import ProxyType
from dnsforge.domain.model.roles import DnsRole
from dnsforge.domain.model.settings import AuthoritativeSettings, ProxySettings
from dnsforge.infrastructure.bind.layout import BindLayoutDetector
from dnsforge.infrastructure.rendering.bind_renderer import BindRenderTree


BIND_TOOLS = ("named-checkconf", "named-checkzone")


def _require_bind_tools() -> None:
    missing = [tool for tool in BIND_TOOLS if shutil.which(tool) is None]
    if missing:
        pytest.skip(f"BIND validation tools are not installed: {', '.join(missing)}")


def _run(command: list[str]) -> None:
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    assert completed.returncode == 0, "\n".join(
        [
            f"command failed: {' '.join(command)}",
            "--- stdout ---",
            completed.stdout,
            "--- stderr ---",
            completed.stderr,
        ]
    )


def _render_profile(family: str, profile: str) -> tuple[Path, object]:
    os.environ["DNSFORGE_BIND_LAYOUT"] = family
    destination = Path(tempfile.mkdtemp(prefix=f"dnsforge-{family}-{profile}-"))
    layout = BindLayoutDetector().from_family(family)

    if profile == "authoritative":
        settings = AuthoritativeSettings(
            role=DnsRole.AUTHORITATIVE,
            node_name="dnsforge-ci-auth",
            raw={
                "SECURITY_PROFILE": "enterprise",
                "RNDC_SECRET": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
            },
        )
        BindRenderTree(layout=layout).render_authoritative(settings, destination)
    else:
        settings = ProxySettings(
            role=DnsRole.PROXY,
            node_name="dnsforge-ci-proxy",
            raw={
                "ENABLE_RPZ": "yes",
                "SECURITY_PROFILE": "enterprise",
                "RNDC_SECRET": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
            },
            proxy_type=ProxyType.HYBRID,
        )
        BindRenderTree(layout=layout).render_proxy(settings, destination)

    return destination, layout


@pytest.mark.parametrize("family", ["redhat", "debian", "suse"])
@pytest.mark.parametrize("profile", ["authoritative", "proxy-hybrid"])
def test_generated_bind_configuration_is_accepted_by_bind_tools(family: str, profile: str) -> None:
    _require_bind_tools()
    root, layout = _render_profile(family, profile)

    _run(["named-checkconf", "-t", str(root), str(layout.named_conf)])
    _run(["named-checkconf", "-z", "-t", str(root), str(layout.named_conf)])

    _run(["named-checkzone", "-t", str(root), "catalog.dnsforge", str(layout.catalog_zone_file)])
    if profile == "proxy-hybrid":
        _run(["named-checkzone", "-t", str(root), "rpz.local", str(layout.rpz_data_dir / "rpz.local.zone")])


def test_ci_validates_every_registered_template_is_used() -> None:
    from dnsforge.infrastructure.bind.rendering.template_registry import TemplateRegistry

    resources = Path("src/dnsforge/infrastructure/bind/resources")
    resource_templates = {path.relative_to(resources) for path in resources.rglob("*") if path.suffix in {".j2", ".tpl"}}
    registered = set(TemplateRegistry.templates())

    assert resource_templates == registered
