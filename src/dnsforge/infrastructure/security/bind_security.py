from __future__ import annotations
from dnsforge.domain.security.model import SecurityControls


class BindSecurityOptionsRenderer:
    def render_options(self, controls: SecurityControls) -> str:
        """Render supplemental options not already present in the Enterprise template.

        The baseline template intentionally contains the safest defaults as
        first-class options. This renderer is kept for profile-driven extension
        without producing duplicate BIND directives.
        """
        lines: list[str] = []
        return "\n".join(lines)

    def render_rrl(self, controls: SecurityControls) -> str:
        if not controls.rrl:
            return ""
        return "\n".join(
            [
                "    rate-limit {",
                "        responses-per-second 10;",
                "        referrals-per-second 5;",
                "        nodata-per-second 5;",
                "        nxdomains-per-second 5;",
                "        errors-per-second 5;",
                "        all-per-second 50;",
                "        window 15;",
                "        slip 2;",
                "    };",
                "",
            ]
        )
