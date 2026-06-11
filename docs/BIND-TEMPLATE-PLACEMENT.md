# BIND template placement

The previous `src/dnsforge/infrastructure/bind/templates/` tree was removed.

Current layout:

```text
src/dnsforge/infrastructure/bind/
├── rendering/
│   ├── template_registry.py
│   └── template_service.py
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
    └── zone templates
```

`rendering/` contains Python modules only. `resources/` contains BIND resource templates only.
No compatibility layer is provided for the old imports.
