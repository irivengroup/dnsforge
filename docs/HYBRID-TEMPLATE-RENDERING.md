# DNSForge Hybrid BIND Rendering

DNSForge uses a hybrid rendering model:

1. `BindConfigFactory` builds the complete BIND configuration model in Python.
2. `TemplateService` renders registered modular BIND templates.
3. Canonical Red Hat paths are rewritten to the active distribution layout.
4. `TemplateRegistry` is the single catalog of committed `.j2` and `.tpl` files.

Rules:

- `/etc/dnsforge` contains only DNSForge node configuration.
- BIND configuration and data are deployed into native BIND paths.
- `infrastructure/build/` is forbidden.
- `infrastructure/bind/resources/templates/` is forbidden.
- every template under `infrastructure/bind/resources/` must be registered.
- no unregistered template may remain in the repository.
