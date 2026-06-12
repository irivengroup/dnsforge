from __future__ import annotations
import datetime as dt
import re
import shutil
from pathlib import Path

from dnsforge.domain.migration.model import MigrationTarget
from dnsforge.infrastructure.settings.env_loader import EnvSettingsLoader
from dnsforge.shared.errors import SettingsError


class MigrationService:
    def __init__(self, loader: EnvSettingsLoader | None = None) -> None:
        self.loader = loader or EnvSettingsLoader()

    def migrate(self, setup_file: Path, target: MigrationTarget, dry_run: bool = False) -> str:
        settings = self.loader.load(setup_file)
        role = settings.get("ROLE", "").strip("'\"")
        current_type = settings.get("PROXY_TYPE", "").strip("'\"")
        if role != "dns-proxy":
            raise SettingsError("only proxy-forwarder <-> proxy-hybrid migrations are supported")
        new_type = "forwarder" if target is MigrationTarget.PROXY_FORWARDER else "hybrid"
        if current_type == new_type:
            return f"Already on {target.value}"
        if current_type not in {"forwarder", "hybrid"}:
            raise SettingsError("current proxy type must be forwarder or hybrid")

        if dry_run:
            return f"Would migrate proxy-{current_type} -> {target.value}"

        backup = setup_file.with_suffix(f".conf.backup.{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d%H%M%S')}")
        shutil.copy2(setup_file, backup)
        text = setup_file.read_text(encoding="utf-8")
        text = self._set_var(text, "PROXY_TYPE", f'"{new_type}"')
        local = "yes" if new_type == "hybrid" else "no"
        for key in ("ENABLE_PROXY_MASTER_ZONES", "ENABLE_PROXY_AUTHORITATIVE_ZONES", "ENABLE_PROXY_LOCAL_ZONES"):
            text = self._set_var(text, key, f'"{local}"')
        setup_file.write_text(text, encoding="utf-8")
        return f"Migrated proxy-{current_type} -> {target.value}; backup={backup}"

    def _set_var(self, text: str, key: str, value: str) -> str:
        pattern = re.compile(rf"^\s*{key}=.*$", re.MULTILINE)
        line = f"{key}={value}"
        if pattern.search(text):
            return pattern.sub(line, text)
        return text.rstrip() + "\n" + line + "\n"
