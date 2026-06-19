from __future__ import annotations

import json

from dnsforge.application.readiness import ReadinessService
from dnsforge.application.readiness.checks.config_features import (
    AclConfigurationCheck,
    CatalogConfigurationCheck,
    ClusterConfigurationCheck,
    DnssecConfigurationCheck,
    ViewsConfigurationCheck,
)
from dnsforge.domain.readiness import ReadinessReport, ReadinessResult, ReadinessStatus
from dnsforge.interfaces.api.readiness import ReadinessApi
from dnsforge.interfaces.cli.application import DnsForgeCli
from dnsforge.infrastructure.filesystem.paths import ProjectPaths


class NoRootGuard:
    def require_root(self) -> None:
        return None


def test_readiness_cli_json_alias(monkeypatch, capsys, tmp_path) -> None:
    report = ReadinessReport([ReadinessResult("Platform Support", ReadinessStatus.PASS, "ok", True)])
    monkeypatch.setattr("dnsforge.interfaces.cli.application.ReadinessService.run", lambda self: report)

    code = DnsForgeCli(privilege_guard=NoRootGuard()).run(["--project-root", str(tmp_path), "readiness", "--json"])

    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "READY"
    assert payload["overall_status"] == "READY"
    assert payload["checks"][0]["name"] == "Platform Support"


def test_readiness_api_returns_json_contract(tmp_path) -> None:
    payload = ReadinessApi(ProjectPaths(tmp_path)).status()

    assert "status" in payload
    assert "score" in payload
    assert "checks" in payload


def test_configuration_feature_checks_pass_and_warn(tmp_path, monkeypatch) -> None:
    setup = tmp_path / "etc" / "dnsforge" / "setup.conf"
    monkeypatch.setenv("DNSFORGE_CONFIG_ROOT", str(setup.parent))
    monkeypatch.setenv("DNSFORGE_SETUP_FILE", str(setup))
    paths = ProjectPaths(tmp_path)

    for check_cls in [
        AclConfigurationCheck,
        ViewsConfigurationCheck,
        DnssecConfigurationCheck,
        CatalogConfigurationCheck,
        ClusterConfigurationCheck,
    ]:
        result = check_cls(paths).run()
        assert result.status is ReadinessStatus.WARNING
        assert result.critical is False

    setup.parent.mkdir(parents=True)
    setup.write_text(
        "ALLOW_QUERY=local\nINTERNAL_VIEW=enabled\nDNSSEC=true\nCATALOG_ZONE=dnsforge.catalog\nPEER_AUTHORITATIVE_ADDRESSES=127.0.0.1\n",
        encoding="utf-8",
    )

    for check_cls in [
        AclConfigurationCheck,
        ViewsConfigurationCheck,
        DnssecConfigurationCheck,
        CatalogConfigurationCheck,
        ClusterConfigurationCheck,
    ]:
        result = check_cls(paths).run()
        assert result.status is ReadinessStatus.PASS
