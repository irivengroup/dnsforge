from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from dnsforge.application.audit.product_auditor import ProductAuditor
from dnsforge.interfaces.cli.main import build_parser

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_product_audit_parser_and_service() -> None:
    parser = build_parser()
    parser.parse_args(["audit"])
    parser.parse_args(["audit", "--strict"])
    report = ProductAuditor().audit(PROJECT_ROOT)
    assert report.ok, report.render()
    assert "Product audit OK" in report.render()


def test_product_audit_cli() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "dnsforge.interfaces.cli.main", "--project-root", str(PROJECT_ROOT), "audit"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=True,
        env={**os.environ, "PYTHONPATH": str(PROJECT_ROOT / "src")},
    )
    assert "Product audit OK" in result.stdout
