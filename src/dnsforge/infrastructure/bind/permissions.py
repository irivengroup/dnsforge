from __future__ import annotations

import grp
import os
import pwd
from dataclasses import dataclass
from pathlib import Path

from dnsforge.infrastructure.bind.layout import BindLayout, BindLayoutDetector


@dataclass(frozen=True)
class PermissionRule:
    path: Path
    owner: str
    group: str
    file_mode: int
    dir_mode: int
    recursive: bool = True


class BindPermissionPolicy:
    """Enterprise ownership/mode policy for DNSForge-managed BIND files."""

    def __init__(self, layout: BindLayout | None = None) -> None:
        self.layout = layout or BindLayoutDetector().detect()
        self.runtime_user = "bind" if self.layout.family == "debian" else "named"
        self.runtime_group = "bind" if self.layout.family == "debian" else "named"

    def rules(self) -> tuple[PermissionRule, ...]:
        root_group = self.runtime_group
        return (
            PermissionRule(self.layout.named_conf, "root", root_group, 0o640, 0o750, recursive=False),
            PermissionRule(self.layout.config_dir, "root", root_group, 0o640, 0o750),
            PermissionRule(self.layout.tsig_dir, "root", root_group, 0o640, 0o750),
            PermissionRule(self.layout.catalog_conf_dir, "root", root_group, 0o640, 0o750),
            PermissionRule(self.layout.data_dir, self.runtime_user, self.runtime_group, 0o640, 0o750),
            PermissionRule(self.layout.master_data_dir, self.runtime_user, self.runtime_group, 0o640, 0o750),
            PermissionRule(self.layout.secondary_data_dir, self.runtime_user, self.runtime_group, 0o660, 0o770),
            PermissionRule(self.layout.dynamic_data_dir, self.runtime_user, self.runtime_group, 0o660, 0o770),
            PermissionRule(self.layout.rpz_data_dir, self.runtime_user, self.runtime_group, 0o640, 0o750),
            PermissionRule(self.layout.statistics_data_dir, self.runtime_user, self.runtime_group, 0o660, 0o770),
            PermissionRule(self.layout.log_dir, self.runtime_user, self.runtime_group, 0o640, 0o750),
            PermissionRule(self.layout.run_dir, self.runtime_user, self.runtime_group, 0o660, 0o770),
        )


class BindPermissionApplier:
    def __init__(self, policy: BindPermissionPolicy | None = None) -> None:
        self.policy = policy or BindPermissionPolicy()

    def apply(self, target_root: Path = Path("/"), dry_run: bool = True) -> list[str]:
        actions: list[str] = []
        root = target_root.resolve()
        for rule in self.policy.rules():
            effective = root / rule.path.relative_to("/")
            if not (effective.exists() or effective.is_symlink()):
                continue
            uid = self._uid(rule.owner)
            gid = self._gid(rule.group)
            candidates = [effective]
            if effective.is_dir() and rule.recursive:
                candidates.extend(effective.rglob("*"))
            for candidate in candidates:
                mode = rule.dir_mode if candidate.is_dir() else rule.file_mode
                actions.append(f"chown {rule.owner}:{rule.group} {candidate}")
                actions.append(f"chmod {oct(mode)} {candidate}")
                if dry_run:
                    continue
                if uid is not None or gid is not None:
                    os.chown(candidate, -1 if uid is None else uid, -1 if gid is None else gid)
                os.chmod(candidate, mode)
        return actions

    def _uid(self, name: str) -> int | None:
        try:
            return pwd.getpwnam(name).pw_uid
        except KeyError:
            return None

    def _gid(self, name: str) -> int | None:
        try:
            return grp.getgrnam(name).gr_gid
        except KeyError:
            return None
