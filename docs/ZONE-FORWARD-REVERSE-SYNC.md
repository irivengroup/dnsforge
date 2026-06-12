# DNSForge zone configuration and reverse synchronization

DNSForge manages BIND as an Enterprise DNS deployment platform. Zone operations
must never update only the forward side when an address record requires reverse
DNS consistency.

## Forward/reverse rule

For every managed forward zone:

- adding an `A` record creates or updates the matching IPv4 reverse zone;
- adding an `AAAA` record creates or updates the matching IPv6 reverse zone;
- updating an `A` or `AAAA` record removes the old `PTR` and creates the new one;
- deleting an `A` or `AAAA` record removes the matching `PTR`;
- deleting a forward zone removes the reverse records generated from that zone.

Generated reverse zones are marked as `managed_reverse: yes` in `/etc/dnsforge/zones.yml`.
That flag is technical DNSForge state for zone ownership and is not rendered into BIND.

## DNS best-practice validation

DNSForge validates zone names and records before catalog persistence:

- no whitespace in zone names;
- valid DNS labels and owner names;
- TTL range: `1..2147483647`;
- `A` and `AAAA` values are validated with the Python `ipaddress` module;
- `MX` and `SRV` require valid priorities;
- `NS`, `MX`, `PTR`, and `CNAME` targets must be valid DNS names;
- `CNAME` owners cannot coexist with other record types;
- `secondary` and `forward` zones must not carry master zone records.

## Zone configuration templates

DNSForge keeps one zone declaration template per server profile, scope and zone type:

```text
src/dnsforge/infrastructure/bind/resources/zones/
├── authoritative/
│   ├── internal/{master,secondary,forward}.conf.tpl
│   └── external/{master,secondary,forward}.conf.tpl
├── proxy-forwarder/
│   ├── internal/{master,secondary,forward}.conf.tpl
│   └── external/{master,secondary,forward}.conf.tpl
└── proxy-hybrid/
    ├── internal/{master,secondary,forward}.conf.tpl
    └── external/{master,secondary,forward}.conf.tpl
```

This separation is intentional even when two templates are currently identical.
It allows DNSForge to evolve authoritative, forwarder and hybrid policies without
cross-profile regressions.

## BIND rendering contract

The hybrid rendering model is preserved:

1. Python builds the BIND configuration model.
2. `TemplateService` renders readable BIND files.
3. Paths are adapted dynamically for Red Hat, Debian/Ubuntu and SUSE.
4. Rendered templates are deployed under the native BIND layout, not under
   `/etc/dnsforge` or `/var/lib/dnsforge`.
