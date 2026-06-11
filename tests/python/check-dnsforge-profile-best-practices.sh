#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

PYTHONPATH="${PROJECT_ROOT}/src" python3 - <<'PY'
from pathlib import Path

from dnsforge.application.profile.profile_auditor import ProfileAuditor
from dnsforge.domain.profile.model import ConfigurationProfile, ProfilePolicy
from dnsforge.domain.profile.validator import ProfileSettingsValidator
from dnsforge.infrastructure.profile.template_loader import ProfileTemplateLoader
from dnsforge.interfaces.cli.main import build_parser
from dnsforge.shared.errors import SettingsError

root = Path.cwd()
loader = ProfileTemplateLoader()
validator = ProfileSettingsValidator()

for profile in ConfigurationProfile:
    path = root / "install" / "templates" / profile.value / "setup.conf"
    values = loader.load(path)
    validator.validate(profile, values)

errors = ProfileAuditor().audit_templates(root)
assert not errors, errors

assert ProfilePolicy(ConfigurationProfile.AUTHORITATIVE).rpz_allowed is False
assert ProfilePolicy(ConfigurationProfile.PROXY_FORWARDER).local_proxy_zones_allowed is False
assert ProfilePolicy(ConfigurationProfile.PROXY_HYBRID).local_proxy_zones_allowed is True

try:
    validator.validate(ConfigurationProfile.PROXY_FORWARDER, {
        "ROLE": "dns-proxy",
        "PROXY_TYPE": "forwarder",
        "ENABLE_PROXY_LOCAL_ZONES": "yes",
    })
except SettingsError:
    pass
else:
    raise SystemExit("forwarder with local zones must fail")

parser = build_parser()
parser.parse_args(["profile", "audit"])
PY

PYTHONPATH="${PROJECT_ROOT}/src" python3 -m dnsforge.interfaces.cli.main \
  --project-root "${PROJECT_ROOT}" profile audit | grep -q 'Profile audit OK'

echo "dnsforge profile best practices validation OK"
