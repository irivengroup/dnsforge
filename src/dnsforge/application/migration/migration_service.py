from __future__ import annotations

import datetime as dt
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

from dnsforge.application.deploy.deploy_service import DeployService
from dnsforge.application.render.render_proxy import RenderProxy
from dnsforge.domain.migration.model import MigrationTarget
from dnsforge.domain.model.proxy_type import ProxyType
from dnsforge.domain.model.roles import DnsRole
from dnsforge.infrastructure.bind.layout import BindLayout, BindLayoutDetector
from dnsforge.infrastructure.filesystem.paths import ProjectPaths
from dnsforge.infrastructure.settings.env_loader import EnvSettingsLoader
from dnsforge.shared.errors import SettingsError


@dataclass(frozen=True)
class MigrationSnapshot:
    """Filesystem checkpoint created before a proxy profile migration."""

    migration_id: str
    root: Path
    setup_file: Path
    bind_root: Path
    metadata_file: Path


class MigrationSnapshotService:
    """Create and restore migration snapshots without using unsafe archive extraction.

    Snapshots are plain filesystem copies. This is deliberately more verbose than
    tar-based snapshots, but rollback remains deterministic and avoids path
    traversal risks around archive extraction.
    """

    def __init__(self, paths: ProjectPaths, layout: BindLayout | None = None) -> None:
        self.paths = paths
        self.layout = layout or BindLayoutDetector().detect()

    def create(
        self,
        *,
        setup_file: Path,
        node: str,
        current_type: str,
        target_type: str,
        reason: str,
        target_root: Path,
    ) -> MigrationSnapshot:
        migration_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d%H%M%S")
        root = self.paths.backup_root / "migrations" / migration_id
        setup_snapshot = root / "setup.conf"
        bind_root = root / "bind"
        root.mkdir(parents=True, exist_ok=False)
        shutil.copy2(setup_file, setup_snapshot)

        copied_paths: list[str] = []
        for source in self.layout.backup_paths:
            effective_source = self._effective_path(source, target_root)
            if not effective_source.exists():
                continue
            destination = bind_root / self._relative_name(source)
            self._copy_path(effective_source, destination)
            copied_paths.append(str(source))

        metadata = {
            "id": migration_id,
            "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "node": node,
            "from": f"proxy-{current_type}",
            "to": f"proxy-{target_type}",
            "reason": reason,
            "setup_file": str(setup_file),
            "target_root": str(target_root),
            "bind_paths": copied_paths,
            "status": "prepared",
        }
        metadata_file = root / "metadata.json"
        metadata_file.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return MigrationSnapshot(migration_id, root, setup_snapshot, bind_root, metadata_file)

    def mark(self, snapshot: MigrationSnapshot, status: str) -> None:
        metadata = json.loads(snapshot.metadata_file.read_text(encoding="utf-8"))
        metadata["status"] = status
        metadata["updated_at_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
        snapshot.metadata_file.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def restore(self, snapshot: MigrationSnapshot, setup_file: Path, target_root: Path) -> None:
        if snapshot.setup_file.exists():
            setup_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(snapshot.setup_file, setup_file)

        if not snapshot.bind_root.exists():
            return

        for stored in sorted(snapshot.bind_root.rglob("*"), key=lambda item: len(item.parts)):
            if stored.is_dir():
                continue
            relative = stored.relative_to(snapshot.bind_root)
            destination = target_root / relative if not relative.is_absolute() else relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(stored, destination)

    def _effective_path(self, path: Path, target_root: Path) -> Path:
        if target_root == Path("/"):
            return path
        return target_root / self._relative_name(path)

    def _relative_name(self, path: Path) -> Path:
        return Path(*path.parts[1:]) if path.is_absolute() else path

    def _copy_path(self, source: Path, destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            if destination.exists():
                shutil.rmtree(destination)
            shutil.copytree(source, destination, symlinks=True)
            return
        shutil.copy2(source, destination)


class MigrationService:
    """Migrate a proxy node between forwarder and hybrid modes transactionally.

    Migration is intentionally limited to proxy-forwarder <-> proxy-hybrid. The
    operation now uses a filesystem transaction: preflight, snapshot, setup.conf
    update, full render, deploy, post-validation, commit. On failure DNSForge
    restores setup.conf and the BIND paths captured before deployment.
    """

    def __init__(
        self,
        paths: ProjectPaths | None = None,
        loader: EnvSettingsLoader | None = None,
        renderer: RenderProxy | None = None,
        deployer: DeployService | None = None,
        snapshotter: MigrationSnapshotService | None = None,
    ) -> None:
        self.paths = paths or ProjectPaths()
        self.loader = loader or EnvSettingsLoader()
        self.renderer = renderer
        self.deployer = deployer or DeployService()
        self.snapshotter = snapshotter or MigrationSnapshotService(self.paths)

    def migrate(
        self,
        setup_file: Path,
        target: MigrationTarget,
        dry_run: bool = False,
        reason: str | None = None,
        target_root: Path = Path("/"),
    ) -> str:
        settings = self.loader.load(setup_file)
        role = settings.get("ROLE", "").strip("'\"")
        node = settings.get("NODE_NAME", "").strip("'\"") or "proxy"
        current_type = settings.get("PROXY_TYPE", "").strip("'\"")

        if role != "dns-proxy":
            raise SettingsError("only proxy-forwarder <-> proxy-hybrid migrations are supported")

        new_type = "forwarder" if target is MigrationTarget.PROXY_FORWARDER else "hybrid"
        if current_type == new_type:
            return f"Already on {target.value}"
        if current_type not in {"forwarder", "hybrid"}:
            raise SettingsError("current proxy type must be forwarder or hybrid")

        plan = [
            f"proxy-{current_type} -> {target.value}",
            f"setup file: {setup_file}",
            f"snapshot root: {self.paths.backup_root / 'migrations'}",
            f"render root: {self.paths.render_dir(DnsRole.PROXY, node)}",
            f"target root: {target_root}",
        ]
        if dry_run:
            return "Would migrate " + "; ".join(plan)

        clean_reason = self._require_reason(reason)
        original_text = setup_file.read_text(encoding="utf-8")
        snapshot = self.snapshotter.create(
            setup_file=setup_file,
            node=node,
            current_type=current_type,
            target_type=new_type,
            reason=clean_reason,
            target_root=target_root,
        )
        try:
            setup_file.write_text(self._render_migrated_setup(original_text, new_type), encoding="utf-8")
            render_service = self.renderer or RenderProxy(self.paths)
            render_service.execute(node, ProxyType.from_value(new_type))
            render_root = self.paths.render_dir(DnsRole.PROXY, node)
            self.deployer.deploy(render_root, target_root=target_root, dry_run=False)
            self.snapshotter.mark(snapshot, "committed")
        except Exception:
            self.snapshotter.restore(snapshot, setup_file, target_root)
            self.snapshotter.mark(snapshot, "rolled_back")
            raise

        return (
            f"Migrated proxy-{current_type} -> {target.value}; "
            f"snapshot={snapshot.root}; rendered={self.paths.render_dir(DnsRole.PROXY, node)}; deployed={target_root}"
        )

    def _require_reason(self, reason: str | None) -> str:
        clean = (reason or "").strip()
        if len(clean) < 8:
            raise SettingsError("--reason is required and must contain at least 8 characters")
        return clean

    def _render_migrated_setup(self, text: str, new_type: str) -> str:
        migrated = self._set_var(text, "ROLE", '"dns-proxy"')
        migrated = self._set_var(migrated, "PROXY_TYPE", f'"{new_type}"')
        local = "yes" if new_type == "hybrid" else "no"
        for key in ("ENABLE_PROXY_MASTER_ZONES", "ENABLE_PROXY_AUTHORITATIVE_ZONES", "ENABLE_PROXY_LOCAL_ZONES"):
            migrated = self._set_var(migrated, key, f'"{local}"')
        return migrated

    def _set_var(self, text: str, key: str, value: str) -> str:
        pattern = re.compile(rf"^\s*{key}=.*$", re.MULTILINE)
        line = f"{key}={value}"
        if pattern.search(text):
            return pattern.sub(line, text)
        return text.rstrip() + "\n" + line + "\n"
