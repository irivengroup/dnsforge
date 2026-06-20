from __future__ import annotations

import hashlib
import json
from pathlib import Path

from dnsforge.domain.compliance import (
    ComplianceStatus,
    ConfigurationBaseline,
    ConfigurationCompliance,
    ConfigurationDrift,
    ConfigurationFingerprint,
    ConfigurationRepairPlan,
    DriftSeverity,
)
from dnsforge.infrastructure.filesystem.paths import ProjectPaths
from dnsforge.infrastructure.settings.env_loader import EnvSettingsLoader


class ComplianceService:
    """Compare rendered DNSForge BIND configuration with deployed native BIND files."""

    SCHEMA = "dnsforge.configuration-compliance.v1"

    def __init__(self, paths: ProjectPaths, loader: EnvSettingsLoader | None = None) -> None:
        self.paths = paths
        self.loader = loader or EnvSettingsLoader()

    def fingerprint(self, *, target_root: Path | None = None, scope: str = "bind") -> ConfigurationFingerprint:
        root = target_root or self.paths.render_root
        return ConfigurationFingerprint(scope=scope, sha256=self._tree_hash(root))

    def baseline(self) -> ConfigurationBaseline:
        settings = self._settings()
        resources = tuple(self._iter_relative_files(self.paths.render_root))
        layout = type(self.paths.bind_layout).__name__
        profile = settings.get("ROLE", "unknown")
        proxy_type = settings.get("PROXY_TYPE")
        if proxy_type:
            profile = f"{profile}:{proxy_type}"
        return ConfigurationBaseline(profile=profile, bind_layout=layout, resources=resources)

    def verify(self, *, target_root: Path = Path("/")) -> ConfigurationCompliance:
        if not self.paths.render_root.exists():
            drift = ConfigurationDrift(
                resource=str(self.paths.render_root),
                expected_hash=None,
                actual_hash=None,
                severity=DriftSeverity.CRITICAL,
            )
            return ConfigurationCompliance(ComplianceStatus.FAILED, None, (drift,))
        drifts = tuple(self._detect_drifts(target_root))
        if not drifts:
            return ConfigurationCompliance(ComplianceStatus.COMPLIANT, self.fingerprint(), ())
        status = ComplianceStatus.DRIFTED
        if any(drift.severity is DriftSeverity.CRITICAL for drift in drifts):
            status = ComplianceStatus.FAILED
        return ConfigurationCompliance(status, self.fingerprint(), drifts)

    def drift(self, *, target_root: Path = Path("/")) -> tuple[ConfigurationDrift, ...]:
        return self.verify(target_root=target_root).drifts

    def repair_plan(self, *, target_root: Path = Path("/")) -> ConfigurationRepairPlan:
        drifts = self.drift(target_root=target_root)
        restore = tuple(drift.resource for drift in drifts if drift.expected_hash)
        regenerate = tuple(drift.resource for drift in drifts if not drift.expected_hash)
        return ConfigurationRepairPlan(
            resources_to_restore=restore,
            resources_to_regenerate=regenerate,
            requires_reload=bool(restore or regenerate),
            requires_restart=False,
        )

    def render_fingerprint(self, *, target_root: Path | None = None, scope: str = "bind") -> str:
        fp = self.fingerprint(target_root=target_root, scope=scope)
        return f"{fp.scope}\t{fp.sha256}\t{fp.generated_at.isoformat()}"

    def render_baseline(self, *, json_output: bool = False) -> str:
        baseline = self.baseline()
        if json_output:
            return json.dumps(
                {
                    "schema": self.SCHEMA,
                    "profile": baseline.profile,
                    "bind_layout": baseline.bind_layout,
                    "resources": list(baseline.resources),
                    "generated_at": baseline.generated_at.isoformat(),
                },
                indent=2,
                sort_keys=True,
            )
        lines = [
            f"Profile: {baseline.profile}",
            f"BIND layout: {baseline.bind_layout}",
            f"Resources: {len(baseline.resources)}",
        ]
        lines.extend(f"- {resource}" for resource in baseline.resources)
        return "\n".join(lines)

    def render_verify(self, *, target_root: Path = Path("/"), json_output: bool = False) -> str:
        compliance = self.verify(target_root=target_root)
        if json_output:
            return self._compliance_json(compliance)
        if compliance.is_compliant:
            return "Configuration compliance: COMPLIANT"
        lines = [f"Configuration compliance: {compliance.status.value}"]
        lines.extend(drift.title() for drift in compliance.drifts)
        return "\n".join(lines)

    def render_drift(self, *, target_root: Path = Path("/"), json_output: bool = False) -> str:
        compliance = self.verify(target_root=target_root)
        if json_output:
            return self._compliance_json(compliance)
        if not compliance.drifts:
            return "No configuration drift detected"
        return "Detected configuration drift\n" + "\n".join(drift.title() for drift in compliance.drifts)

    def render_repair(self, *, target_root: Path = Path("/"), preview: bool = True) -> str:
        plan = self.repair_plan(target_root=target_root)
        if plan.is_empty:
            return "Configuration repair plan: empty"
        prefix = "Would restore" if preview else "Restore required"
        lines = ["Configuration repair plan"]
        lines.extend(f"{prefix}: {resource}" for resource in plan.resources_to_restore)
        lines.extend(f"Would regenerate: {resource}" for resource in plan.resources_to_regenerate)
        if plan.requires_reload:
            lines.append("Requires BIND reload: yes")
        return "\n".join(lines)

    def _detect_drifts(self, target_root: Path) -> list[ConfigurationDrift]:
        drifts: list[ConfigurationDrift] = []
        for relative in self._iter_relative_files(self.paths.render_root):
            expected = self.paths.render_root / relative
            actual = target_root / relative
            expected_hash = self._file_hash(expected)
            if not actual.exists():
                drifts.append(ConfigurationDrift(relative, expected_hash, None, DriftSeverity.CRITICAL))
                continue
            actual_hash = self._file_hash(actual)
            if expected_hash != actual_hash:
                drifts.append(ConfigurationDrift(relative, expected_hash, actual_hash, DriftSeverity.WARNING))
        return drifts

    def _settings(self) -> dict[str, str]:
        if not self.paths.setup_file.exists():
            return {}
        return self.loader.load(self.paths.setup_file)

    def _compliance_json(self, compliance: ConfigurationCompliance) -> str:
        return json.dumps(
            {
                "schema": self.SCHEMA,
                "status": compliance.status.value,
                "fingerprint": None
                if compliance.fingerprint is None
                else {
                    "scope": compliance.fingerprint.scope,
                    "sha256": compliance.fingerprint.sha256,
                    "generated_at": compliance.fingerprint.generated_at.isoformat(),
                },
                "drifts": [
                    {
                        "resource": drift.resource,
                        "expected_hash": drift.expected_hash,
                        "actual_hash": drift.actual_hash,
                        "severity": drift.severity.value,
                    }
                    for drift in compliance.drifts
                ],
            },
            indent=2,
            sort_keys=True,
        )

    def _tree_hash(self, root: Path) -> str:
        digest = hashlib.sha256()
        if not root.exists():
            digest.update(b"<missing>")
            return digest.hexdigest()
        for relative in self._iter_relative_files(root):
            path = root / relative
            digest.update(relative.encode("utf-8"))
            digest.update(self._file_hash(path).encode("ascii"))
        return digest.hexdigest()

    def _file_hash(self, path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def _iter_relative_files(self, root: Path) -> tuple[str, ...]:
        if not root.exists():
            return ()
        return tuple(
            str(path.relative_to(root))
            for path in sorted(candidate for candidate in root.rglob("*") if candidate.is_file())
        )
