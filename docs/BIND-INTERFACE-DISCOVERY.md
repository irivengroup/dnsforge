# DNSForge BIND Interface Discovery

Since v14.5.0, `setup.conf` stores BIND network bindings as NIC names, not static IP addresses.

## Variables

Proxy profiles use:

```conf
BIND_EXTERNET_NICNAME="eth2"
BIND_INTRANET_NICNAME="eth1"
BIND_ADMIN_NICNAME="eth0"
```

Authoritative profiles use:

```conf
BIND_INTRANET_NICNAME="eth1"
BIND_ADMIN_NICNAME="eth0"
```

`BIND_EXTERNET_NICNAME` is the external/client-facing side for internet or cloud clients. `BIND_INTRANET_NICNAME` is the internal side for enterprise clients and proxy-authoritative transfers. `BIND_ADMIN_NICNAME` is used for BIND administration and RNDC controls.

## Defaults

The profile generator defaults all NIC variables to the administrative interface detected from the default SSH/default route path. If only one interface exists, all variables resolve to that interface. This supports one-NIC, two-NIC and three-NIC deployments without forcing a rigid topology.

## Rendering behavior

At render time, the local DNSForge agent resolves each NIC name to its IPv4 address and injects the derived addresses into the generated BIND configuration. When the same interface is reused by several roles, generated BIND blocks include each distinct address only once.

Legacy `FRONT_IP`, `BACK_IP` and `ADM_IP` values are still accepted as a migration fallback, but new setup generation no longer emits them.
