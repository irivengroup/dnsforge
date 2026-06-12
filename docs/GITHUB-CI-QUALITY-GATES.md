# DNSForge GitHub CI quality gates

The CI validates DNSForge as a Python-only Enterprise BIND deployment and configuration product.

Mandatory gates:

- Python syntax compilation on Python 3.9, 3.11 and 3.13.
- Ruff lint.
- Ruff format check.
- Architecture gates:
  - no `src/settings`;
  - no `src/libs`;
  - no `application/configure`;
  - no `infrastructure/build`;
  - no `infrastructure/templates` legacy tree;
  - no shell tests or shell product code under `src/` and `tests/`.
- Importability of every `dnsforge.*` Python module.
- Full pytest suite.
- BIND generated configuration validation with `named-checkconf` and `named-checkzone` when BIND tools are available.
- Coverage gate currently set to 60% to match the active baseline.
- Python package build with `python -m build`.
- Wheel installation and `dnsforge --help` smoke test.

Advisory gates:

- Bandit static security scan.
- pip-audit dependency vulnerability scan.

Advisory gates are intentionally non-blocking until their findings have been triaged and converted into enforced policy.
