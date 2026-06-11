# DNSForge BIND infrastructure architecture

DNSForge keeps Python rendering code and embedded BIND resource templates separated.

```text
src/dnsforge/infrastructure/bind/
├── rendering/
│   ├── renderer.py              # future orchestration entry point
│   ├── template_registry.py     # registered BIND resource inventory
│   ├── template_service.py      # distribution-aware rendering service
│   └── render_context.py        # future rendering context model
└── resources/
    ├── named.conf.j2
    ├── 00-acl.conf.j2
    ├── 10-keys.conf.j2
    ├── 20-options.conf.j2
    ├── 30-logging.conf.j2
    ├── 40-controls.conf.j2
    ├── 45-statistics.conf.j2
    ├── 50-rpz.conf.j2
    ├── 55-catalog.conf.j2
    ├── 60-views.conf.j2
    └── *.tpl
```

Rules:

- no Python module is stored under a directory named `templates`;
- no compatibility shim is kept for the previous `infrastructure.bind.templates` path;
- all BIND `.j2` and `.tpl` files live under `infrastructure/bind/resources`;
- every resource template must be registered in `TemplateRegistry`;
- rendering code remains importable from `dnsforge.infrastructure.bind.rendering`.
