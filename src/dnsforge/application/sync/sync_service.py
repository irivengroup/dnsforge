from __future__ import annotations

import hashlib
import re
from pathlib import Path

from dnsforge.application.zone.zone_manager import require_reason
from dnsforge.domain.cluster.validator import ClusterValidator
from dnsforge.domain.sync.model import ClusterDrift, ClusterDriftSeverity, ClusterPeerState, ClusterSyncPlan
from dnsforge.infrastructure.catalog.zone_catalog import ZoneCatalog
from dnsforge.infrastructure.settings.env_loader import EnvSettingsLoader


class SyncService:
    """Authoritative synchronization service.

    Cluster commands remain the public orchestration surface. This service owns the
    sync-specific logic so it can later be extracted into DNSSync without moving
    DNSForge cluster command semantics.
    """

    def __init__(self, loader: EnvSettingsLoader | None = None, validator: ClusterValidator | None = None) -> None:
        self.loader = loader or EnvSettingsLoader()
        self.validator = validator or ClusterValidator()

    def peers(self, setup_file: Path) -> str:
        config = self._load_valid_config(setup_file)
        if not config.enabled:
            return "Cluster peers: disabled"
        lines = ["Peer\tState\tMessage"]
        lines.extend(
            f"{state.address}\t{self._state_label(state)}\t{state.message}" for state in self.peer_states(setup_file)
        )
        return "\n".join(lines)

    def diff(self, setup_file: Path) -> str:
        config = self._load_valid_config(setup_file)
        if not config.enabled:
            return "Cluster diff: disabled"
        drifts = self.drift_report(setup_file)
        if not drifts:
            return "Cluster diff OK"
        lines = ["Severity\tPeer\tArea\tMessage"]
        lines.extend(f"{drift.severity.value}\t{drift.peer}\t{drift.area}\t{drift.message}" for drift in drifts)
        return "\n".join(lines)

    def sync(self, setup_file: Path, reason: str | None = None, dry_run: bool = False) -> str:
        normalized = require_reason(reason or "")
        config = self._load_valid_config(setup_file)
        if not config.enabled:
            return "Cluster disabled"
        plan = self.sync_plan(setup_file, dry_run=dry_run)
        if dry_run:
            return self._format_sync_plan(plan, normalized)
        bundle = self._write_sync_bundle(setup_file, plan, normalized)
        return (
            f"Authoritative HA cluster sync completed: {plan.zone_count} zone(s), "
            f"{plan.target_count} peer(s), manifest_sha256={plan.manifest_checksum}, bundle {bundle}"
        )

    def sync_plan(self, setup_file: Path, dry_run: bool = True) -> ClusterSyncPlan:
        config = self._load_valid_config(setup_file)
        zones = [zone.name for zone in ZoneCatalog(self._zone_catalog_path(setup_file)).list() if zone.enabled]
        files = [str(self._zone_catalog_path(setup_file))]
        catalog_state = setup_file.parent / "catalog-state.yml"
        if catalog_state.exists():
            files.append(str(catalog_state))
        dnssec_state = setup_file.parent / "dnssec-state.yml"
        if dnssec_state.exists():
            files.append(str(dnssec_state))
        zone_files = self._discover_zone_files(setup_file)
        files.extend(str(path) for path in zone_files)
        file_checksums = {path: self._sha256(Path(path)) for path in files if Path(path).exists()}
        zone_checksum = self._digest_mapping(
            {zone: file_checksums.get(path, "") for zone, path in self._zone_file_map(zone_files).items()}
        )
        soa_serials = self._soa_serials(zone_files)
        soa_serials_checksum = self._digest_mapping({name: str(serial) for name, serial in soa_serials.items()})
        manifest_checksum = self._manifest_checksum(
            config.local_node,
            list(config.peers),
            zones,
            file_checksums,
            zone_checksum,
            soa_serials_checksum,
        )
        return ClusterSyncPlan(
            config.local_node,
            list(config.peers),
            zones,
            files,
            dry_run,
            file_checksums=file_checksums,
            zone_checksum=zone_checksum,
            soa_serials=soa_serials,
            soa_serials_checksum=soa_serials_checksum,
            manifest_checksum=manifest_checksum,
        )

    def peer_states(self, setup_file: Path) -> list[ClusterPeerState]:
        config = self._load_valid_config(setup_file)
        states: list[ClusterPeerState] = []
        for peer in config.peers:
            manifest = self._peer_manifest_path(setup_file, peer)
            if not manifest.exists():
                states.append(ClusterPeerState(peer, False, message="no peer manifest available"))
                continue
            values = self._parse_simple_manifest(manifest)
            states.append(
                ClusterPeerState(
                    peer,
                    True,
                    zone_count=int(values.get("zone_count", "0") or "0"),
                    catalog_serial=values.get("catalog_serial", "unknown"),
                    dnssec_state=values.get("dnssec_state", "unknown"),
                    manifest_checksum=values.get("manifest_sha256", "unknown"),
                    zone_checksum=values.get("zone_checksum", "unknown"),
                    soa_serials_checksum=values.get("soa_serials_checksum", "unknown"),
                    message="manifest loaded",
                )
            )
        return states

    def drift_report(self, setup_file: Path) -> list[ClusterDrift]:
        plan = self.sync_plan(setup_file, dry_run=True)
        drifts: list[ClusterDrift] = []
        for state in self.peer_states(setup_file):
            if not state.reachable:
                drifts.append(
                    ClusterDrift(
                        ClusterDriftSeverity.WARNING,
                        state.address,
                        "reachability",
                        state.message or "peer state unavailable",
                    )
                )
                continue
            if state.zone_count != plan.zone_count:
                drifts.append(
                    ClusterDrift(
                        ClusterDriftSeverity.CRITICAL,
                        state.address,
                        "zones",
                        f"local={plan.zone_count} peer={state.zone_count}",
                    )
                )
            if state.zone_checksum not in {"unknown", plan.zone_checksum}:
                drifts.append(
                    ClusterDrift(
                        ClusterDriftSeverity.CRITICAL,
                        state.address,
                        "zone-checksum",
                        f"local={plan.zone_checksum} peer={state.zone_checksum}",
                    )
                )
            if state.soa_serials_checksum not in {"unknown", plan.soa_serials_checksum}:
                drifts.append(
                    ClusterDrift(
                        ClusterDriftSeverity.CRITICAL,
                        state.address,
                        "soa-serial",
                        f"local={plan.soa_serials_checksum} peer={state.soa_serials_checksum}",
                    )
                )
            if state.dnssec_state not in {"unknown", "aligned"}:
                drifts.append(ClusterDrift(ClusterDriftSeverity.WARNING, state.address, "dnssec", state.dnssec_state))
        return drifts

    def _load_valid_config(self, setup_file: Path):
        config = (
            self.validator.service_load(setup_file, self.loader) if hasattr(self.validator, "service_load") else None
        )
        if config is None:
            from dnsforge.application.cluster.cluster_service import ClusterService

            config = ClusterService(loader=self.loader, validator=self.validator, sync_service=self).load(setup_file)
        self.validator.validate(config)
        return config

    def _format_sync_plan(self, plan: ClusterSyncPlan, reason: str) -> str:
        lines = [
            "Authoritative HA cluster sync dry-run",
            f"Local Node: {plan.local_node}",
            f"Reason: {reason}",
            f"Peers: {', '.join(plan.peers)}",
            f"Zones: {plan.zone_count}",
            f"Zone Checksum: {plan.zone_checksum}",
            f"SOA Serials Checksum: {plan.soa_serials_checksum}",
            f"Manifest SHA256: {plan.manifest_checksum}",
            "Files:",
        ]
        lines.extend(f"- {path} sha256={plan.file_checksums.get(path, 'missing')}" for path in plan.files)
        if plan.soa_serials:
            lines.append("SOA serials:")
            lines.extend(f"- {zone}: {serial}" for zone, serial in sorted(plan.soa_serials.items()))
        return "\n".join(lines)

    def _write_sync_bundle(self, setup_file: Path, plan: ClusterSyncPlan, reason: str) -> Path:
        target = setup_file.parent / "cluster-sync" / "outbox" / f"{plan.local_node}.manifest"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "\n".join(
                [
                    f"local_node={plan.local_node}",
                    f"reason={reason}",
                    f"peer_count={plan.target_count}",
                    f"zone_count={plan.zone_count}",
                    "catalog_serial=local",
                    "dnssec_state=aligned",
                    f"manifest_sha256={plan.manifest_checksum}",
                    f"zone_checksum={plan.zone_checksum}",
                    f"soa_serials_checksum={plan.soa_serials_checksum}",
                    "files=",
                    *[f"- {path} sha256={plan.file_checksums.get(path, 'missing')}" for path in plan.files],
                    "soa_serials=",
                    *[f"- {zone}={serial}" for zone, serial in sorted(plan.soa_serials.items())],
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        return target

    def _state_label(self, state: ClusterPeerState) -> str:
        return "known" if state.reachable else "unknown"

    def _discover_zone_files(self, setup_file: Path) -> list[Path]:
        candidates = [setup_file.parent]
        found: list[Path] = []
        for root in candidates:
            if not root.exists():
                continue
            for pattern in ("*.zone", "*.db"):
                for path in root.rglob(pattern):
                    if path.is_file() and "cluster-sync" not in path.parts:
                        found.append(path)
        return sorted(set(found))

    def _zone_file_map(self, zone_files: list[Path]) -> dict[str, str]:
        return {path.stem: str(path) for path in zone_files}

    def _soa_serials(self, zone_files: list[Path]) -> dict[str, int]:
        serials: dict[str, int] = {}
        for path in zone_files:
            serial = self._extract_soa_serial(path)
            if serial is not None:
                serials[path.stem] = serial
        return serials

    def _extract_soa_serial(self, path: Path) -> int | None:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return None
        if " SOA " not in text and "\tSOA\t" not in text and " SOA\t" not in text:
            return None
        lines = text.splitlines()
        in_soa = False
        for line in lines:
            cleaned = line.split(";", 1)[0].strip()
            if not cleaned:
                continue
            if " SOA " in f" {cleaned} " or "\tSOA\t" in cleaned or " SOA\t" in cleaned:
                in_soa = True
                numbers = re.findall(r"\b\d{8,14}\b|\b\d+\b", cleaned)
                if numbers:
                    return int(numbers[-1])
                continue
            if in_soa:
                match = re.search(r"\b(\d{8,14}|\d+)\b", cleaned)
                if match:
                    return int(match.group(1))
                if ")" in cleaned:
                    break
        return None

    def _sha256(self, path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def _digest_mapping(self, values: dict[str, str]) -> str:
        digest = hashlib.sha256()
        for key in sorted(values):
            digest.update(key.encode("utf-8"))
            digest.update(b"=")
            digest.update(values[key].encode("utf-8"))
            digest.update(b"\n")
        return digest.hexdigest()

    def _manifest_checksum(
        self,
        local_node: str,
        peers: list[str],
        zones: list[str],
        file_checksums: dict[str, str],
        zone_checksum: str,
        soa_serials_checksum: str,
    ) -> str:
        payload: dict[str, str] = {
            "local_node": local_node,
            "peers": ",".join(sorted(peers)),
            "zones": ",".join(sorted(zones)),
            "zone_checksum": zone_checksum,
            "soa_serials_checksum": soa_serials_checksum,
        }
        payload.update({f"file:{path}": checksum for path, checksum in file_checksums.items()})
        return self._digest_mapping(payload)

    def _parse_simple_manifest(self, path: Path) -> dict[str, str]:
        values: dict[str, str] = {}
        for raw in path.read_text(encoding="utf-8").splitlines():
            if "=" not in raw or raw.lstrip().startswith("#"):
                continue
            key, value = raw.split("=", 1)
            values[key.strip()] = value.strip()
        return values

    def _peer_manifest_path(self, setup_file: Path, peer: str) -> Path:
        safe = peer.replace(":", "_").replace("/", "_")
        return setup_file.parent / "cluster-sync" / "peers" / f"{safe}.manifest"

    def _zone_catalog_path(self, setup_file: Path) -> Path:
        configured = self._optional(self.loader.load(setup_file).get("ZONE_CATALOG_FILE"))
        if configured:
            return Path(configured)
        return setup_file.parent / "zones.yml"

    def _optional(self, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip().strip("'\"")
        return cleaned or None
