from __future__ import annotations

from pathlib import Path

from dnsforge.domain.audit.product_audit import ProductAuditReport


class ProductAuditor:
    REQUIRED_PATHS = (
        "pyproject.toml",
        "bin/dnsforge",
        "src/dnsforge/domain",
        "src/dnsforge/application",
        "src/dnsforge/infrastructure",
        "src/dnsforge/interfaces/cli",
    )

    def audit(self, project_root: Path) -> ProductAuditReport:
        report = ProductAuditReport(findings=[])
        self._check_required_paths(project_root, report)
        self._check_forbidden_references(project_root, report)
        self._check_no_legacy_directory(project_root, report)
        return report

    def _forbidden_references(self) -> tuple[str, ...]:
        return (
            "Legacy" + "ShellRunner",
            "dns" + "Proxy" + "Deploy" + ".sh",
            "dns" + "Authoritative" + "Deploy" + ".sh",
            "zone-" + "manager" + ".sh",
        )

    def _check_required_paths(self, project_root: Path, report: ProductAuditReport) -> None:
        for rel in self.REQUIRED_PATHS:
            path = project_root / rel
            if not path.exists():
                report.add_error(f"required path missing: {rel}", path)

    def _check_forbidden_references(self, project_root: Path, report: ProductAuditReport) -> None:
        source_root = project_root / "src" / "dnsforge"
        if not source_root.exists():
            report.add_error("src/dnsforge does not exist", source_root)
            return

        for path in source_root.rglob("*.py"):
            content = path.read_text(encoding="utf-8")
            for needle in self._forbidden_references():
                if needle in content:
                    report.add_error("forbidden legacy reference", path)

    def _check_no_legacy_directory(self, project_root: Path, report: ProductAuditReport) -> None:
        if (project_root / "legacy").exists():
            report.add_error("legacy directory must not be present in distributable product", project_root / "legacy")
