# DNSForge native BIND layout

DNSForge is a BIND deployment and complete configuration management product.
It does not deploy runtime DNS configuration or DNS runtime data under DNSForge-owned generated/data directories.

`/etc/dnsforge/setup.conf` remains the node source of truth for DNSForge bootstrap parameters only. After `dnsforge initialize`, generated configuration and DNS data are deployed into the native BIND filesystem layout of the operating system.

## Initialization ownership model

`dnsforge initialize` takes ownership of the local BIND instance:

1. verify that BIND is already installed by the installer in `install/`;
2. refuse execution when the hidden initialization lock already exists;
3. render the modular BIND configuration for the detected OS family;
4. move the existing BIND configuration and data out of the live paths;
5. create a compressed backup under `/var/backups/dnsforge/bind-config/`;
6. deploy the new modular BIND tree into native BIND paths;
7. run `named-checkconf` against the native `named.conf`;
8. restore SELinux contexts where applicable;
9. restart the native BIND service.

The initialization lock is technical state and must not be displayed by `dnsforge status`.

## Supported native layouts

### Red Hat / Rocky / Alma / CentOS / Fedora

```text
/etc/named.conf
/etc/named/
├── acl/
├── catalog/
├── conf.d/
├── dnssec/
├── keys/
├── rpz/
├── views/
└── zones/

/var/named/
├── catalog/
├── rpz/
└── zones/
    ├── forward/
    ├── master/
    └── secondary/

/etc/sysconfig/named
/etc/systemd/system/named.service.d/override.conf
```

Service: `named`.

### Debian / Ubuntu

```text
/etc/bind/named.conf
/etc/bind/
├── acl/
├── catalog/
├── conf.d/
├── dnssec/
├── keys/
├── rpz/
├── views/
└── zones/

/var/lib/bind/
├── catalog/
├── rpz/
└── zones/
    ├── forward/
    ├── master/
    └── secondary/

/var/cache/bind/
/etc/default/named
/etc/systemd/system/bind9.service.d/override.conf
```

Service: `bind9`.

### SUSE / SLES / openSUSE

```text
/etc/named.conf
/etc/named/
├── acl/
├── catalog/
├── conf.d/
├── dnssec/
├── keys/
├── rpz/
├── views/
└── zones/

/var/lib/named/
├── catalog/
├── rpz/
└── zones/
    ├── forward/
    ├── master/
    └── secondary/

/etc/sysconfig/named
/etc/systemd/system/named.service.d/override.conf
```

Service: `named`.

## Modular configuration contract

The modularity of BIND configuration is mandatory and is part of the product design.
The top-level `named.conf` must only include DNSForge-managed modular files:

```text
acl/00-acl.conf
keys/10-keys.conf
conf.d/20-options.conf
conf.d/30-logging.conf
conf.d/40-controls.conf
conf.d/45-statistics.conf
conf.d/50-forwarders.conf
rpz/50-rpz.conf
views/60-views.conf
zones/60-zones.conf
```

The exact absolute include paths are rendered from the detected native layout.
