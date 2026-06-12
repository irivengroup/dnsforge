# GitHub CI

DNSForge ships a GitHub Actions pipeline that validates both the Python codebase and the generated BIND configuration.

The workflow runs on pull requests, pushes and manual dispatches. It performs:

- Python installation on supported versions.
- BIND validation tool installation on the runner.
- Editable package installation with development dependencies.
- Python syntax compilation.
- Ruff linting.
- Assertion that no Bash test remains under `tests/`.
- Full pytest execution.
- Explicit generated BIND configuration validation using:
  - `named-checkconf`
  - `named-checkconf -z`
  - `named-checkzone`

The generated configuration is validated for the Red Hat, Debian/Ubuntu and SUSE layout families, and for both authoritative and proxy-hybrid profiles.
