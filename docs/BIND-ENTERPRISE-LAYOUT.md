# DNSForge Enterprise BIND Layout

DNSForge is a BIND deployment and full-configuration-management product. `/etc/dnsforge` is reserved for DNSForge node configuration only: `setup.conf`, product policy files and the hidden initialization lock. DNSForge does not store generated BIND configuration or DNS runtime data under `/etc/dnsforge` or `/var/lib/dnsforge`.

## Red Hat / Rocky / Alma

```text
/etc/named.conf
/etc/named/
├── conf.d/
│   ├── 00-acl.conf
│   ├── 10-keys.conf
│   ├── 20-options.conf
│   ├── 30-logging.conf
│   ├── 40-controls.conf
│   ├── 45-statistics.conf
│   ├── 50-rpz.conf
│   └── 60-views.conf
├── views/
│   ├── external/
│   │   ├── zones.available/
│   │   ├── zones.enabled/
│   │   │   └── zones.index.conf
│   │   └── templates/
│   │       ├── master.conf.tpl
│   │       ├── secondary.conf.tpl
│   │       └── forward.conf.tpl
│   └── internal/
│       ├── zones.available/
│       ├── zones.enabled/
│       │   └── zones.index.conf
│       └── templates/
│           ├── master.conf.tpl
│           ├── secondary.conf.tpl
│           └── forward.conf.tpl
├── tsig/
│   └── rndc.key
└── catalog/
    └── catalog.zone

/var/named/
├── master/
│   ├── external/
│   └── internal/
├── secondary/
├── dynamic/
│   └── managed-keys.bind
├── rpz/
│   └── rpz.local.zone
└── data/
    ├── named_stats.txt
    ├── named.memstats
    └── named_dump.db

/var/log/named/
├── default.log
├── security.log
├── transfer.log
├── rpz.log
└── resolver.log

/run/named/
```

## Debian / Ubuntu

The same logical layout is mapped to Debian-native roots:

```text
/etc/bind/named.conf
/etc/bind/...
/var/lib/bind/...
/var/cache/bind
/var/log/named
/run/named
```

The service name is `bind9`.

## SUSE / SLES

The same logical layout is mapped to SUSE-native roots:

```text
/etc/named.conf
/etc/named/...
/var/lib/named/...
/var/log/named
/run/named
```

The service name is `named`.

## Permissions and SELinux

Every initialization/deployment reapplies ownership, mode and SELinux contexts.

Default policy:

```text
named.conf and /etc/named or /etc/bind : root:<bind-group>, files 0640, dirs 0750
TSIG/catalog/config files             : root:<bind-group>, files 0640, dirs 0750
zone data, dynamic, rpz, statistics   : <bind-user>:<bind-group>
secondary/dynamic/statistics/runtime  : files 0660, dirs 0770
logs                                  : <bind-user>:<bind-group>, files 0640, dirs 0750
```

SELinux contexts are registered/restored for configuration, zone data, log and runtime paths when SELinux tools are available.
