from __future__ import annotations

from typing import Callable

from dnsforge.domain.events.model import AuditEvent

EventHandler = Callable[[AuditEvent], None]


class EventBus:
    """Synchronous in-process event bus for CLI, future REST adapters and DNSForge Manager."""

    def __init__(self) -> None:
        self._handlers: list[EventHandler] = []

    def subscribe(self, handler: EventHandler) -> None:
        self._handlers.append(handler)

    def publish(self, event: AuditEvent) -> AuditEvent:
        for handler in list(self._handlers):
            handler(event)
        return event


class RecordingEventBus(EventBus):
    def __init__(self) -> None:
        super().__init__()
        self.events: list[AuditEvent] = []

    def publish(self, event: AuditEvent) -> AuditEvent:
        self.events.append(event)
        return super().publish(event)
