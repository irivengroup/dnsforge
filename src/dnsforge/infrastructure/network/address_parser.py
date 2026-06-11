from __future__ import annotations

import ipaddress
import re

class AddressListParser:
    SEPARATORS = re.compile(r"\s*[;,\s]+\s*")

    def parse(self, value: str | None) -> list[str]:
        if not value:
            return []
        cleaned = value.strip().strip("'\"")
        return [item for item in self.SEPARATORS.split(cleaned) if item]

    def parse_ip_addresses(self, value: str | None) -> list[str]:
        items = self.parse(value)
        for item in items:
            ipaddress.ip_address(item)
        return items

    def parse_networks(self, value: str | None) -> list[str]:
        items = self.parse(value)
        for item in items:
            ipaddress.ip_network(item, strict=False)
        return items
