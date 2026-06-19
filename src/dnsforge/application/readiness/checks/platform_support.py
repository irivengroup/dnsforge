from __future__ import annotations

import os
from pathlib import Path

from dnsforge.domain.readiness import ReadinessResult, ReadinessStatus

SUPPORTED_MINIMUMS = {
    "rhel": 8,
    "redhat": 8,
    "rocky": 8,
    "almalinux": 8,
    "alma": 8,
    "centos": 8,
    "ubuntu": 22,
    "debian": 10,
    "sles": 12,
    "suse": 12,
    "opensuse-leap": 12,
}


class PlatformSupportCheck:
    name = "Platform Support"
    critical = True

    def __init__(self, os_release: Path = Path("/etc/os-release")) -> None:
        self.os_release = os_release

    def run(self) -> ReadinessResult:
        data = self._read_os_release()
        distro_id = data.get("ID", "").lower()
        version = data.get("VERSION_ID", "")
        like = data.get("ID_LIKE", "").lower().split()
        candidates = [distro_id, *like]
        minimum = next((SUPPORTED_MINIMUMS[item] for item in candidates if item in SUPPORTED_MINIMUMS), None)
        if minimum is None:
            return ReadinessResult(
                self.name,
                ReadinessStatus.FAILED,
                f"unsupported platform: {distro_id or 'unknown'}",
                critical=self.critical,
            )
        major = self._major(version)
        if major is None:
            return ReadinessResult(
                self.name,
                ReadinessStatus.WARNING,
                f"could not determine OS major version for {distro_id or 'unknown'}",
                critical=False,
            )
        if major < minimum:
            return ReadinessResult(
                self.name,
                ReadinessStatus.FAILED,
                f"{distro_id} {version} is below supported minimum {minimum}+",
                critical=self.critical,
            )
        return ReadinessResult(
            self.name,
            ReadinessStatus.PASS,
            f"{distro_id} {version} meets minimum {minimum}+",
            critical=self.critical,
        )

    def _read_os_release(self) -> dict[str, str]:
        if not self.os_release.exists():
            return {}
        values: dict[str, str] = {}
        for line in self.os_release.read_text(encoding="utf-8", errors="ignore").splitlines():
            if "=" not in line or line.startswith("#"):
                continue
            key, value = line.split("=", 1)
            values[key] = value.strip().strip('"')
        return values

    def _major(self, version: str) -> int | None:
        token = version.split(".", 1)[0].strip()
        if not token:
            return None
        try:
            return int(token)
        except ValueError:
            return None
