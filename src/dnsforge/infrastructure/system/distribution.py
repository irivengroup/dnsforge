from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LinuxDistribution:
    id: str
    id_like: str
    version_id: str

    @property
    def family(self) -> str:
        values = f"{self.id} {self.id_like}".lower()
        if any(x in values for x in ("rhel", "fedora", "rocky", "almalinux", "centos")):
            return "redhat"
        if any(x in values for x in ("debian", "ubuntu")):
            return "debian"
        if any(x in values for x in ("suse", "sles", "opensuse")):
            return "suse"
        return "unknown"


class OsReleaseReader:
    def read(self, path: Path = Path("/etc/os-release")) -> LinuxDistribution:
        data = {}
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    data[k] = v.strip().strip("'\"")
        return LinuxDistribution(data.get("ID", ""), data.get("ID_LIKE", ""), data.get("VERSION_ID", ""))
