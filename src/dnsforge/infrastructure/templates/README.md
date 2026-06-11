# DNSForge infrastructure templates

This package contains the hybrid BIND rendering layer.

Rules:

- `BindConfigFactory` builds the complete BIND configuration model in Python.
- `TemplateService` renders registered templates and rewrites canonical Red Hat paths to the active Linux distribution layout.
- reusable BIND templates live in `infrastructure/templates/bind/`.
- every `.j2` and `.tpl` file must be declared in `TemplateRegistry`.
- `infrastructure/build/` and `infrastructure/templates/templates/` must not exist.
