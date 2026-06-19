from __future__ import annotations

import json

from dnsforge.application.output.formatter import OutputEnvelope


class JsonFormatter:
    """Render the stable DNSForge JSON envelope."""

    def render(self, envelope: OutputEnvelope) -> str:
        return json.dumps(envelope.as_dict(), indent=2, sort_keys=True)
