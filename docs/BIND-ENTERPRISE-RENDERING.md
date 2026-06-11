# DNSForge BIND Enterprise Rendering

DNSForge renders BIND configuration through a hybrid model:

1. `BindConfigFactory` builds the complete in-memory BIND model.
2. `TemplateService` renders modular BIND files.
3. `BindLayoutDetector` adapts every path to Red Hat, Debian/Ubuntu or SUSE.
4. `BindPermissionApplier` reapplies ownership and permissions.
5. SELinux contexts are restored on supported platforms.

## Enterprise baseline

Generated files now include hardened defaults suitable for Enterprise DNS:

- closed recursion for authoritative profiles;
- recursion restricted to `recursive_clients` for proxy profiles;
- DNSSEC validation enabled;
- QNAME minimisation enabled;
- minimal responses and minimal-any enabled;
- DNS cookies enabled;
- EDNS UDP size capped to 1232;
- controlled cache TTLs and cache size;
- recursive query limits;
- fetch limits per server and per zone;
- response-rate limiting;
- segmented logging;
- admin/monitoring-limited statistics channel;
- RPZ rendered as a policy inside `options` and as a managed zone file;
- catalog zone declaration rendered as a modular conf.d artifact;
- deny-by-default dynamic updates and explicit zone transfer policy.

## Generated modular files

Typical Red Hat layout:

```text
/etc/named.conf
/etc/named/conf.d/00-acl.conf
/etc/named/conf.d/10-keys.conf
/etc/named/conf.d/20-options.conf
/etc/named/conf.d/30-logging.conf
/etc/named/conf.d/40-controls.conf
/etc/named/conf.d/45-statistics.conf
/etc/named/conf.d/50-rpz.conf
/etc/named/conf.d/55-catalog.conf
/etc/named/conf.d/60-views.conf
```

The same logical layout is adapted to Debian/Ubuntu and SUSE by `BindLayoutDetector`.
