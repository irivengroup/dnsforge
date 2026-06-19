from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from dnsforge.application.output.formatter import OutputEnvelope


class TableFormatter:
    """Render operator-friendly text while keeping JSON handled centrally."""

    def render(self, envelope: OutputEnvelope) -> str:
        data = envelope.data
        if isinstance(data, Mapping):
            return "\n".join(f"{key}: {value}" for key, value in data.items())
        if isinstance(data, Sequence) and not isinstance(data, (str, bytes)):
            return "\n".join(str(item) for item in data)
        return str(data)
