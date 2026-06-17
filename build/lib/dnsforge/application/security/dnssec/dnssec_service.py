from __future__ import annotations

import datetime as dt
import hashlib
from dataclasses import replace
from pathlib import Path

from dnsforge.domain.security.dnssec.model import (
    DnssecKeyMetadata,
    DnssecZoneMetadata,
    DnssecZoneState,
    require_dnssec_reason,
    utc_now,
)
from dnsforge.infrastructure.security.dnssec_state_repository import DnssecStateRepository
from dnsforge.infrastructure.settings.env_loader import EnvSettingsLoader
from dnsforge.shared.errors import DnsForgeError


class DnssecService:
    def __init__(self, loader: EnvSettingsLoader | None = None) -> None:
        self.loader = loader or EnvSettingsLoader()

    def status(self, setup_file: Path, zone: str | None = None) -> str:
        data = self.loader.load(setup_file) if setup_file.exists() else {}
        globally_enabled = self._bool(data.get("DNSSEC_ENABLED", data.get("ENABLE_DNSSEC", "no")))
        repository = self._repository(setup_file)
        if zone:
            metadata = repository.get(zone)
            return "\n".join(
                [
                    f"DNSSEC global: {'enabled' if globally_enabled else 'disabled'}",
                    f"Zone: {metadata.zone}",
                    f"State: {metadata.state.value}",
                    f"KSK: {metadata.ksk.key_id if metadata.ksk else 'missing'}",
                    f"ZSK: {metadata.zsk.key_id if metadata.zsk else 'missing'}",
                    f"Signed At: {metadata.signed_at or 'not signed'}",
                ]
            )
        zones = repository.list()
        if not zones:
            return f"DNSSEC global: {'enabled' if globally_enabled else 'disabled'}\nZones: none"
        lines = [f"DNSSEC global: {'enabled' if globally_enabled else 'disabled'}", "Zone\tState\tKSK\tZSK\tSigned"]
        lines.extend(
            f"{item.zone}\t{item.state.value}\t{item.ksk.key_id if item.ksk else 'missing'}\t"
            f"{item.zsk.key_id if item.zsk else 'missing'}\t{item.signed_at or '-'}"
            for item in zones
        )
        return "\n".join(lines)

    def validate(self, setup_file: Path, zone: str | None = None) -> str:
        data = self.loader.load(setup_file) if setup_file.exists() else {}
        enabled = self._bool(data.get("DNSSEC_ENABLED", data.get("ENABLE_DNSSEC", "no")))
        repository = self._repository(setup_file)
        findings: list[str] = []
        zones = [repository.get(zone)] if zone else repository.list()
        for metadata in zones:
            if metadata.enabled() and (metadata.ksk is None or metadata.zsk is None):
                findings.append(f"{metadata.zone}: enabled DNSSEC requires KSK and ZSK")
            if metadata.state is DnssecZoneState.SIGNED and not metadata.signed_at:
                findings.append(f"{metadata.zone}: signed state requires signed_at")
        if findings:
            raise DnsForgeError("\n".join(findings))
        if not enabled and not zones:
            return "DNSSEC validation WARN: disabled"
        return "DNSSEC validation OK"

    def enable(self, setup_file: Path, zone: str, reason: str) -> str:
        reason = require_dnssec_reason(reason)
        repository = self._repository(setup_file)
        metadata = repository.get(zone)
        if metadata.ksk is None:
            metadata = replace(metadata, ksk=self._new_key(zone, "KSK", months=24))
        if metadata.zsk is None:
            metadata = replace(metadata, zsk=self._new_key(zone, "ZSK", months=6))
        metadata = self._record(metadata, DnssecZoneState.ENABLED, "enable", reason)
        repository.save(metadata)
        self._write_key_metadata(setup_file, metadata)
        return f"DNSSEC enabled for zone {zone}"

    def disable(self, setup_file: Path, zone: str, reason: str) -> str:
        reason = require_dnssec_reason(reason)
        repository = self._repository(setup_file)
        metadata = self._record(repository.get(zone), DnssecZoneState.DISABLED, "disable", reason)
        repository.save(metadata)
        return f"DNSSEC disabled for zone {zone}"

    def sign(self, setup_file: Path, zone: str, reason: str) -> str:
        reason = require_dnssec_reason(reason)
        repository = self._repository(setup_file)
        metadata = repository.get(zone)
        if metadata.ksk is None or metadata.zsk is None:
            metadata = replace(
                metadata,
                ksk=metadata.ksk or self._new_key(zone, "KSK", months=24),
                zsk=metadata.zsk or self._new_key(zone, "ZSK", months=6),
            )
        metadata = replace(metadata, signed_at=utc_now().isoformat())
        metadata = self._record(metadata, DnssecZoneState.SIGNED, "sign", reason)
        repository.save(metadata)
        self._write_key_metadata(setup_file, metadata)
        return f"DNSSEC signed zone {zone}"

    def rotate_ksk(self, setup_file: Path, zone: str, reason: str) -> str:
        reason = require_dnssec_reason(reason)
        repository = self._repository(setup_file)
        metadata = repository.get(zone)
        metadata = replace(metadata, ksk=self._new_key(zone, "KSK", months=24))
        state = metadata.state if metadata.enabled() else DnssecZoneState.ENABLED
        metadata = self._record(metadata, state, "rotate-ksk", reason)
        repository.save(metadata)
        self._write_key_metadata(setup_file, metadata)
        return f"DNSSEC KSK rotated for zone {zone}"

    def rotate_zsk(self, setup_file: Path, zone: str, reason: str) -> str:
        reason = require_dnssec_reason(reason)
        repository = self._repository(setup_file)
        metadata = repository.get(zone)
        metadata = replace(metadata, zsk=self._new_key(zone, "ZSK", months=6))
        state = metadata.state if metadata.enabled() else DnssecZoneState.ENABLED
        metadata = self._record(metadata, state, "rotate-zsk", reason)
        repository.save(metadata)
        self._write_key_metadata(setup_file, metadata)
        return f"DNSSEC ZSK rotated for zone {zone}"

    def check_expiry(self, setup_file: Path | None = None, warn_days: int = 30) -> str:
        repository = (
            self._repository(setup_file)
            if setup_file is not None
            else DnssecStateRepository(Path("/etc/dnsforge/dnssec-state.json"))
        )
        now = utc_now()
        warnings: list[str] = []
        for metadata in repository.list():
            for key in (metadata.ksk, metadata.zsk):
                if key is None:
                    continue
                expires = dt.datetime.fromisoformat(key.expires_at)
                remaining = (expires - now).days
                if remaining <= warn_days:
                    warnings.append(f"{metadata.zone}: {key.key_type} {key.key_id} expires in {remaining} days")
        if warnings:
            return "\n".join(warnings)
        return "DNSSEC key expiry OK"

    def _repository(self, setup_file: Path) -> DnssecStateRepository:
        return DnssecStateRepository(setup_file.parent / "dnssec-state.json")

    def _key_dir(self, setup_file: Path) -> Path:
        settings = self.loader.load(setup_file) if setup_file.exists() else {}
        value = settings.get("DNSSEC_KEY_DIRECTORY", "")
        if value:
            return Path(value.strip("\"'"))
        return setup_file.parent / "dnssec" / "keys"

    def _write_key_metadata(self, setup_file: Path, metadata: DnssecZoneMetadata) -> None:
        directory = self._key_dir(setup_file) / metadata.zone
        directory.mkdir(parents=True, exist_ok=True)
        for key in (metadata.ksk, metadata.zsk):
            if key is None:
                continue
            path = directory / f"{key.key_id}.metadata"
            path.write_text(
                "\n".join(
                    [
                        f"zone={metadata.zone}",
                        f"key_type={key.key_type}",
                        f"algorithm={key.algorithm}",
                        f"created_at={key.created_at}",
                        f"expires_at={key.expires_at}",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

    def _new_key(self, zone: str, key_type: str, months: int) -> DnssecKeyMetadata:
        created = utc_now()
        expires = created + dt.timedelta(days=months * 30)
        seed = f"{zone}:{key_type}:{created.isoformat()}".encode("utf-8")
        digest = hashlib.sha256(seed).hexdigest()[:16]
        return DnssecKeyMetadata(
            key_id=f"{key_type.lower()}-{digest}",
            key_type=key_type,
            algorithm="ECDSAP256SHA256",
            created_at=created.isoformat(),
            expires_at=expires.isoformat(),
        )

    def _record(
        self, metadata: DnssecZoneMetadata, state: DnssecZoneState, action: str, reason: str
    ) -> DnssecZoneMetadata:
        event = f"{utc_now().isoformat()} {action}: {reason}"
        return replace(metadata, state=state, last_reason=reason, history=[*metadata.history, event])

    def _bool(self, value: str) -> bool:
        return value.strip("\"'").lower() in {"yes", "true", "1", "on", "enabled"}
