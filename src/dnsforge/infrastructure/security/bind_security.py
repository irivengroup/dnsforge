from __future__ import annotations
from dnsforge.domain.security.model import SecurityControls

class BindSecurityOptionsRenderer:
    def render_options(self, controls: SecurityControls) -> str:
        lines: list[str] = []
        if controls.hide_version:
            lines.append('    version "not disclosed";')
        if controls.minimal_responses:
            lines.append('    minimal-responses yes;')
        if controls.minimal_any:
            lines.append('    minimal-any yes;')
        if controls.dns_cookies:
            lines.append('    answer-cookie yes;')
        if controls.dnssec_validation:
            lines.append('    dnssec-validation auto;')
        if controls.qname_minimization:
            lines.append('    qname-minimization yes;')
        if controls.serve_stale:
            lines.append('    stale-answer-enable yes;')
        return '\n'.join(lines)

    def render_rrl(self, controls: SecurityControls) -> str:
        if not controls.rrl:
            return ''
        return 'rate-limit {\n    responses-per-second 10;\n    window 15;\n};\n'
