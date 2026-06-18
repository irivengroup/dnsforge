from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def run_clean(tmp_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    script = tmp_path / "tools" / "clean.py"
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
    )


def write_minimal_repo(tmp_path: Path) -> None:
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "clean.py").write_text((PROJECT_ROOT / "tools" / "clean.py").read_text(), encoding="utf-8")


def test_clean_source_rejects_dist_and_caches(tmp_path: Path) -> None:
    write_minimal_repo(tmp_path)
    (tmp_path / "dist").mkdir()
    (tmp_path / "dist" / "dnsforge-1.0.0-py3-none-any.whl").write_text("wheel", encoding="utf-8")
    (tmp_path / ".ruff_cache").mkdir()

    result = run_clean(tmp_path, "--check-source")

    assert result.returncode == 1
    assert "dist" in result.stdout
    assert ".ruff_cache" in result.stdout


def test_clean_release_allows_single_dist_pair_but_rejects_other_artifacts(tmp_path: Path) -> None:
    write_minimal_repo(tmp_path)
    (tmp_path / "dist").mkdir()
    (tmp_path / "dist" / "dnsforge-1.0.0-py3-none-any.whl").write_text("wheel", encoding="utf-8")
    (tmp_path / "dist" / "dnsforge-1.0.0.tar.gz").write_text("sdist", encoding="utf-8")

    assert run_clean(tmp_path, "--check-release").returncode == 0

    (tmp_path / "dnsforge.egg-info").mkdir()
    result = run_clean(tmp_path, "--check-release")

    assert result.returncode == 1
    assert "dnsforge.egg-info" in result.stdout


def test_clean_fix_release_preserves_dist(tmp_path: Path) -> None:
    write_minimal_repo(tmp_path)
    (tmp_path / "dist").mkdir()
    wheel = tmp_path / "dist" / "dnsforge-1.0.0-py3-none-any.whl"
    sdist = tmp_path / "dist" / "dnsforge-1.0.0.tar.gz"
    wheel.write_text("wheel", encoding="utf-8")
    sdist.write_text("sdist", encoding="utf-8")
    (tmp_path / "build").mkdir()
    (tmp_path / ".mypy_cache").mkdir()
    (tmp_path / "dnsforge.egg-info").mkdir()

    result = run_clean(tmp_path, "--fix-release")

    assert result.returncode == 0
    assert wheel.exists()
    assert sdist.exists()
    assert not (tmp_path / "build").exists()
    assert not (tmp_path / ".mypy_cache").exists()
    assert not (tmp_path / "dnsforge.egg-info").exists()
