from __future__ import annotations

import json
from pathlib import Path


class DnssecPolicyService:
    def __init__(self, path: Path) -> None:
        self.path = path

    def show(self) -> str:
        if not self.path.exists():
            return json.dumps(self._default_policy(), indent=2, sort_keys=True)
        return self.path.read_text(encoding="utf-8").strip()

    def apply(self, *, zsk_rotation_days: int, ksk_rotation_days: int) -> str:
        if zsk_rotation_days <= 0 or ksk_rotation_days <= 0:
            raise ValueError("rotation days must be positive")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"zsk_rotation_days": zsk_rotation_days, "ksk_rotation_days": ksk_rotation_days}
        self.path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return f"DNSSEC policy applied: zsk={zsk_rotation_days}d ksk={ksk_rotation_days}d"

    def _default_policy(self) -> dict[str, int]:
        return {"zsk_rotation_days": 30, "ksk_rotation_days": 365}
