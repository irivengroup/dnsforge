# DNSForge Certification Matrix

## Official support baseline

| Platform family | Minimum | Certified scope |
| --- | --- | --- |
| RHEL / Rocky / Alma | 8+ | Agent install, BIND rendering, validation, live smoke, package install. |
| Ubuntu | 22.04 LTS+ | Agent install, BIND rendering, validation, live smoke, package install. |
| Debian | 10+ | Agent install, BIND rendering, validation, live smoke, package install. |
| SUSE / SLES | 12+ | Agent install, BIND rendering, validation, live smoke, package install. |

## DNSForge profiles

Each supported platform family must retain coverage for:

- `authoritative`
- `proxy-forwarder`
- `proxy-hybrid`

## Required validation classes

- Python quality gates: Ruff, MyPy, Bandit.
- Product gates: CLI/API/Event/Service/Release hygiene.
- BIND gates: `named-checkconf`, `named-checkzone`, and isolated live `named` smoke when BIND is available.
- Manager gates: Manager → DNSSync → DNSForge Agent dry-run/apply security checks.
- Packaging gates: wheel build, wheel install, entrypoint validation and clean release artifact validation.

## Non-goal

The certification matrix is not limited to the newest available operating systems. It is anchored on minimum enterprise versions to protect customers running conservative infrastructure baselines.
