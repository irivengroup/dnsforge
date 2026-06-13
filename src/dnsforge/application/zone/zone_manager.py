from __future__ import annotations

import ipaddress
from dataclasses import replace
from typing import List

from dnsforge.application.history.history_service import ZoneHistoryService
from dnsforge.domain.zone.model import ZoneDefinition, ZoneLifecycleState, ZoneType
from dnsforge.domain.zone.policy_validator import ServerProfile, ZonePolicyValidator
from dnsforge.domain.zone.record import DnsRecord, DnsRecordExpressionParser, DnsRecordType
from dnsforge.domain.zone.reverse import is_reverse_zone_name, reverse_mapping_for_address
from dnsforge.infrastructure.catalog.zone_catalog import ZoneCatalog
from dnsforge.application.zone.zone_transaction import ZoneChangePlan, ZoneTransactionEngine
from dnsforge.infrastructure.filesystem.paths import ProjectPaths
from dnsforge.infrastructure.history.filesystem_repository import FilesystemHistoryRepository
from dnsforge.shared.errors import ZoneError


def require_reason(reason: str) -> str:
    normalized = (reason or "").strip()
    if len(normalized) < 8:
        raise ZoneError("--reason is required and must contain at least 8 characters")
    return normalized


def action_with_reason(action: str, reason: str) -> str:
    return f"{action}: {require_reason(reason)}"


class ZoneManager:
    def __init__(
        self,
        paths: ProjectPaths,
        catalog: ZoneCatalog | None = None,
        profile: ServerProfile = ServerProfile.AUTHORITATIVE,
    ) -> None:
        self.paths = paths
        self.profile = profile
        self.catalog = catalog or ZoneCatalog(paths.catalog_file)
        self.parser = DnsRecordExpressionParser()
        self.history = ZoneHistoryService(
            self.catalog,
            FilesystemHistoryRepository(paths.history_root),
        )
        self.transactions = ZoneTransactionEngine(self.catalog, self.profile)

    def list(self, enabled_only: bool = False) -> List[ZoneDefinition]:
        zones = self.catalog.list()
        if enabled_only:
            return [zone for zone in zones if zone.enabled and zone.lifecycle is ZoneLifecycleState.ACTIVE]
        return zones

    def get(self, name: str) -> ZoneDefinition:
        return self.catalog.get(name)

    def search_zones(
        self,
        owner: str | None = None,
        view: str | None = None,
        state: str | None = None,
        environment: str | None = None,
        classification: str | None = None,
    ) -> List[ZoneDefinition]:
        zones = self.catalog.list()
        if owner:
            wanted = owner.lower()
            zones = [
                zone
                for zone in zones
                if wanted in zone.business_owner.lower() or wanted in zone.technical_owner.lower()
            ]
        if view:
            zones = [zone for zone in zones if view in zone.views]
        if state:
            zones = [zone for zone in zones if zone.lifecycle.value == state]
        if environment:
            zones = [zone for zone in zones if zone.environment == environment]
        if classification:
            zones = [zone for zone in zones if zone.classification == classification]
        return zones

    def search_records(
        self,
        zone_name: str,
        record_name: str | None = None,
        record_type: str | None = None,
        value: str | None = None,
    ) -> List[DnsRecord]:
        zone = self.get(zone_name)
        records = zone.records
        if record_name:
            wanted = record_name.lower()
            records = [record for record in records if wanted in record.name.lower()]
        if record_type:
            wanted_type = record_type.upper()
            records = [record for record in records if record.record_type.value == wanted_type]
        if value:
            wanted_value = value.lower()
            records = [record for record in records if wanted_value in record.value.lower()]
        return records

    def show(self, name: str) -> str:
        zone = self.get(name)
        lines = [
            f"Zone: {zone.name}",
            f"Type: {zone.zone_type.value}",
            f"Status: {'enabled' if zone.enabled else 'disabled'}",
            f"Views: {', '.join(zone.views)}",
            f"Managed Reverse: {'yes' if zone.managed_reverse else 'no'}",
            f"Lifecycle: {zone.lifecycle.value}",
            f"Business Owner: {zone.business_owner or 'unset'}",
            f"Technical Owner: {zone.technical_owner or 'unset'}",
            f"Environment: {zone.environment or 'unset'}",
            f"Classification: {zone.classification or 'unset'}",
            f"Description: {zone.description or 'unset'}",
            "",
            "Records:",
        ]
        if not zone.records:
            lines.append("  none")
        else:
            lines.extend(f"  {record.to_bind_line()}" for record in zone.records)
        return "\n".join(lines)

    def status(self, name: str) -> str:
        zone = self.get(name)
        current_version = self.history.current_version(name)
        lifecycle = zone.lifecycle.value
        return "\n".join(
            [
                f"Zone: {zone.name}",
                f"Status: {'enabled' if zone.enabled else 'disabled'}",
                f"Lifecycle: {lifecycle}",
                f"Type: {zone.zone_type.value}",
                f"Views: {', '.join(zone.views)}",
                f"Current Version: {current_version}",
                f"Managed Reverse: {'yes' if zone.managed_reverse else 'no'}",
                f"Business Owner: {zone.business_owner or 'unset'}",
                f"Technical Owner: {zone.technical_owner or 'unset'}",
                f"Environment: {zone.environment or 'unset'}",
                f"Classification: {zone.classification or 'unset'}",
            ]
        )

    def backup(self, name: str, reason: str) -> str:
        self.get(name)
        self.history.snapshot_current(name, action_with_reason("manual-backup", reason))
        return f"Zone backup created: {name}#{self.history.current_version(name)}"

    def create(
        self,
        name: str,
        zone_type: str,
        views: List[str],
        cluster: str | None = None,
        enabled: bool = True,
        description: str = "",
        business_owner: str = "",
        technical_owner: str = "",
        environment: str = "",
        classification: str = "",
        lifecycle: str = "draft",
        reason: str = "",
    ) -> None:
        snapshot_reason = action_with_reason("create", reason)
        plan = self.transactions.plan()
        zone = ZoneDefinition(
            name=name,
            zone_type=ZoneType.from_value(zone_type),
            views=views,
            cluster=cluster,
            enabled=enabled,
            description=description,
            business_owner=business_owner,
            technical_owner=technical_owner,
            environment=environment,
            classification=classification,
            lifecycle=ZoneLifecycleState.from_value(lifecycle),
        )
        plan.create(zone)
        self.transactions.commit(plan)
        self.history.snapshot_current(name, snapshot_reason)

    def enable(self, name: str, reason: str) -> None:
        zone = self.get(name)
        if zone.lifecycle is not ZoneLifecycleState.DRAFT:
            raise ZoneError("only draft zones can be enabled")
        self._update_zone(replace(zone, enabled=True, lifecycle=ZoneLifecycleState.ACTIVE), "enable", reason)

    def disable(self, name: str, reason: str) -> None:
        zone = self.get(name)
        if zone.lifecycle is not ZoneLifecycleState.ACTIVE:
            raise ZoneError("only active zones can be disabled")
        self._update_zone(replace(zone, enabled=False, lifecycle=ZoneLifecycleState.DEPRECATED), "disable", reason)

    def retire(self, name: str, reason: str) -> None:
        zone = self.get(name)
        if zone.lifecycle is not ZoneLifecycleState.DEPRECATED:
            raise ZoneError("only deprecated zones can be retired")
        self._update_zone(replace(zone, enabled=False, lifecycle=ZoneLifecycleState.RETIRED), "retire", reason)

    def delete(self, name: str, reason: str) -> None:
        zone = self.get(name)
        if zone.lifecycle is not ZoneLifecycleState.RETIRED:
            raise ZoneError("zone delete requires lifecycle retired")
        self.history.snapshot_current(name, action_with_reason("pre-delete", reason))
        plan = self.transactions.plan()
        working_zone = plan.get(name)
        for record in working_zone.records:
            self._apply_reverse_delete(plan, working_zone, record)
        plan.delete(name)
        self.transactions.commit(plan)

    def _update_zone(self, zone: ZoneDefinition, action: str, reason: str) -> None:
        plan = self.transactions.plan()
        plan.update(zone)
        self.transactions.commit(plan)
        self.history.snapshot_current(zone.name, action_with_reason(action, reason))

    def audit_zones(self) -> tuple[bool, str]:
        findings: list[str] = []
        zone_names = {zone.name for zone in self.catalog.list()}
        for zone in self.catalog.list():
            prefix = f"{zone.name}:"
            for snapshot in self.history.repository.list(zone.name):
                if ":" not in snapshot.action or len(snapshot.action.split(":", 1)[1].strip()) < 8:
                    findings.append(f"{prefix} history version {snapshot.version} has missing or too-short reason")
            if not zone.business_owner:
                findings.append(f"{prefix} missing business owner")
            if not zone.technical_owner:
                findings.append(f"{prefix} missing technical owner")
            if not zone.classification:
                findings.append(f"{prefix} missing classification")
            if not zone.environment:
                findings.append(f"{prefix} missing environment")
            if zone.lifecycle is ZoneLifecycleState.ACTIVE and not zone.enabled:
                findings.append(f"{prefix} active zone is disabled")
            if zone.lifecycle is not ZoneLifecycleState.ACTIVE and zone.enabled:
                findings.append(f"{prefix} non-active zone is enabled")
            for record in zone.records:
                if record.record_type in {DnsRecordType.A, DnsRecordType.AAAA}:
                    reverse = reverse_mapping_for_address(
                        record.value, self._absolute_owner(zone.name, record.name)
                    ).zone_name
                    if reverse not in zone_names:
                        findings.append(f"{prefix} missing reverse zone for {record.name} {record.value}")

        if not findings:
            return True, "Zone audit OK"
        return False, "\n".join(findings)

    def add_record(self, zone_name: str, expr: str, ttl: int | None = None, reason: str = "") -> None:
        plan = self.transactions.plan()
        zone = plan.get(zone_name)
        record = self.parser.parse_add(expr, ttl)
        if record in zone.records:
            raise ZoneError("record already exists")
        updated_zone = self._replace_records(zone, [*zone.records, record])
        plan.update(updated_zone)
        self._apply_reverse_add(plan, updated_zone, record)
        self.transactions.commit(plan)
        self._snapshot_changes(zone_name, action_with_reason("add-record", reason), plan)

    def update_record(self, zone_name: str, expr: str, ttl: int | None = None, reason: str = "") -> None:
        plan = self.transactions.plan()
        zone = plan.get(zone_name)
        new_record, old_value = self.parser.parse_update(expr, ttl)
        found = False
        records = []
        old_record: DnsRecord | None = None
        for record in zone.records:
            if (
                record.record_type == new_record.record_type
                and record.name == new_record.name
                and record.priority == new_record.priority
                and record.value == old_value
            ):
                records.append(new_record)
                old_record = record
                found = True
            else:
                records.append(record)
        if not found or old_record is None:
            raise ZoneError("record to update not found")
        updated_zone = self._replace_records(zone, records)
        plan.update(updated_zone)
        self._apply_reverse_delete(plan, updated_zone, old_record)
        self._apply_reverse_add(plan, updated_zone, new_record)
        self.transactions.commit(plan)
        self._snapshot_changes(zone_name, action_with_reason("update-record", reason), plan)

    def delete_record(self, zone_name: str, expr: str, reason: str = "") -> None:
        plan = self.transactions.plan()
        zone = plan.get(zone_name)
        record_type, name, priority, value = self.parser.parse_delete(expr)
        found = False
        records = []
        removed: List[DnsRecord] = []
        for record in zone.records:
            match = (
                record.record_type == record_type
                and record.name == name
                and (priority is None or record.priority == priority)
                and (value is None or record.value == value)
            )
            if match:
                found = True
                removed.append(record)
            else:
                records.append(record)
        if not found:
            raise ZoneError("record to delete not found")
        updated_zone = self._replace_records(zone, records)
        plan.update(updated_zone)
        for record in removed:
            self._apply_reverse_delete(plan, updated_zone, record)
        self.transactions.commit(plan)
        self._snapshot_changes(zone_name, action_with_reason("delete-record", reason), plan)

    def _save(self, zone: ZoneDefinition, records: List[DnsRecord]) -> None:
        updated = ZoneDefinition(
            zone.name,
            zone.zone_type,
            zone.views,
            zone.cluster,
            zone.enabled,
            zone.acl,
            records,
            zone.managed_reverse,
            zone.description,
            zone.business_owner,
            zone.technical_owner,
            zone.environment,
            zone.classification,
            zone.lifecycle,
        )
        ZonePolicyValidator.validate_zone(updated, self.profile)
        self.catalog.update(updated)

    def _apply_reverse_add(self, plan: ZoneChangePlan, zone: ZoneDefinition, record: DnsRecord) -> None:
        mapping_record = self._reverse_record_for(zone, record)
        if mapping_record is None:
            return
        reverse_name, ptr_record = mapping_record
        reverse_zone = self._get_or_create_reverse_zone(plan, reverse_name, zone)
        if ptr_record not in reverse_zone.records:
            plan.update(self._replace_records(reverse_zone, [*reverse_zone.records, ptr_record]))

    def _apply_reverse_delete(self, plan: ZoneChangePlan, zone: ZoneDefinition, record: DnsRecord) -> None:
        mapping_record = self._reverse_record_for(zone, record)
        if mapping_record is None:
            return
        reverse_name, ptr_record = mapping_record
        try:
            reverse_zone = plan.get(reverse_name)
        except ZoneError:
            return
        records = [item for item in reverse_zone.records if item != ptr_record]
        if reverse_zone.managed_reverse and not records:
            plan.delete(reverse_name)
        else:
            plan.update(self._replace_records(reverse_zone, records))

    def _reverse_record_for(self, zone: ZoneDefinition, record: DnsRecord) -> tuple[str, DnsRecord] | None:
        if zone.managed_reverse or is_reverse_zone_name(zone.name):
            return None
        if record.record_type not in {DnsRecordType.A, DnsRecordType.AAAA}:
            return None
        try:
            ipaddress.ip_address(record.value)
        except ValueError:
            return None
        target = self._absolute_owner(zone.name, record.name)
        mapping = reverse_mapping_for_address(record.value, target)
        return mapping.zone_name, DnsRecord(DnsRecordType.PTR, mapping.ptr_owner, mapping.ptr_target, ttl=record.ttl)

    def _get_or_create_reverse_zone(
        self, plan: ZoneChangePlan, reverse_name: str, source_zone: ZoneDefinition
    ) -> ZoneDefinition:
        try:
            return plan.get(reverse_name)
        except ZoneError:
            reverse_zone = ZoneDefinition(
                name=reverse_name,
                zone_type=ZoneType.REVERSE_MASTER,
                views=list(source_zone.views),
                cluster=source_zone.cluster,
                enabled=source_zone.enabled,
                acl=dict(source_zone.acl),
                records=[],
                managed_reverse=True,
            )
            plan.create(reverse_zone)
            return reverse_zone

    def _replace_records(self, zone: ZoneDefinition, records: List[DnsRecord]) -> ZoneDefinition:
        updated = ZoneDefinition(
            zone.name,
            zone.zone_type,
            list(zone.views),
            zone.cluster,
            zone.enabled,
            dict(zone.acl),
            records,
            zone.managed_reverse,
            zone.description,
            zone.business_owner,
            zone.technical_owner,
            zone.environment,
            zone.classification,
            zone.lifecycle,
        )
        ZonePolicyValidator.validate_zone(updated, self.profile)
        return updated

    def _absolute_owner(self, zone_name: str, record_name: str) -> str:
        if record_name == "@":
            return zone_name.rstrip(".") + "."
        if record_name.endswith("."):
            return record_name
        return f"{record_name}.{zone_name.rstrip('.')}."

    def _snapshot_changes(self, primary_zone: str, action: str, plan: ZoneChangePlan) -> None:
        for zone_name in plan.affected_zones():
            if zone_name == primary_zone:
                self.history.snapshot_current(zone_name, action)
            elif zone_name in plan.deleted_zones:
                # Deleted managed reverse zones are intentionally not snapshotted
                # after commit because they are no longer present in the catalog.
                continue
            else:
                self.history.snapshot_current(zone_name, f"sync-reverse-{action}")

    def history_list(self, zone_name: str) -> str:
        return self.history.history(zone_name)

    def history_diff(self, zone_name: str, from_version: int, to_version: int) -> str:
        return self.history.diff(zone_name, from_version, to_version)

    def diff_current(self, zone_name: str, version: int) -> str:
        return self.history.diff_current(zone_name, version)

    def restore(self, zone_name: str, version: int) -> str:
        return self.history.rollback(zone_name, version)

    def rollback(self, zone_name: str, version: int, reason: str) -> str:
        require_reason(reason)
        result = self.restore(zone_name, version)
        self.history.snapshot_current(zone_name, action_with_reason(f"rollback-to-{version}", reason))
        return result

    def show_version(self, zone_name: str, version: int) -> str:
        return self.history.show_version(zone_name, version)
