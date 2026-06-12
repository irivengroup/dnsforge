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

    _rewrite_generated_paths_for_host_validation(destination, layout)
    return destination, layout


def _rewrite_generated_paths_for_host_validation(root: Path, layout: object) -> None:
    """Make generated absolute BIND paths validate without named-checkconf -t.

    GitHub-hosted runners do not allow BIND to chroot into an arbitrary tmpdir
    and fail with ``isc_dir_chroot: permission denied``. The generated tree still
    uses native absolute paths, so for CI syntax validation we rewrite references
    to the temporary rendered tree and run the normal host-side BIND validators.
    This keeps validation strict while avoiding a privileged chroot requirement.
    """
    native_roots = sorted(
        {
            layout.named_conf,
            layout.config_dir,
            layout.data_dir,
            layout.cache_dir,
            layout.run_dir,
            layout.log_dir,
            Path("/etc/rndc.conf"),
            Path("/etc/rndc.key"),
        },
        key=lambda item: len(str(item)),
        reverse=True,
    )

    replacements = {str(native): str(root / native.relative_to("/")) for native in native_roots}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        content = path.read_text(encoding="utf-8")
        rewritten = content
        for source, target in replacements.items():
            rewritten = rewritten.replace(source, target)
        if rewritten != content:
            path.write_text(rewritten, encoding="utf-8")


@pytest.mark.parametrize("family", ["redhat", "debian", "suse"])
@pytest.mark.parametrize("profile", ["authoritative", "proxy-hybrid"])
def test_generated_bind_configuration_is_accepted_by_bind_tools(family: str, profile: str) -> None:
    _require_bind_tools()
    root, layout = _render_profile(family, profile)

    named_conf = root / layout.named_conf.relative_to("/")
    catalog_zone = root / layout.catalog_zone_file.relative_to("/")
    rpz_zone = root / (layout.rpz_data_dir / "rpz.local.zone").relative_to("/")

    _run(["named-checkconf", str(named_conf)])
    _run(["named-checkconf", "-z", str(named_conf)])

    _run(["named-checkzone", "catalog.dnsforge", str(catalog_zone)])
    if profile == "proxy-hybrid":
        _run(["named-checkzone", "rpz.local", str(rpz_zone)])


def test_ci_validates_every_registered_template_is_used() -> None:
    from dnsforge.infrastructure.bind.rendering.template_registry import TemplateRegistry

    resources = Path("src/dnsforge/infrastructure/bind/resources")
    resource_templates = {path.relative_to(resources) for path in resources.rglob("*") if path.suffix in {".j2", ".tpl"}}
    registered = set(TemplateRegistry.templates())

    assert resource_templates == registered
