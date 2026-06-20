# BIND Interface Discovery

DNSForge setup profiles declare network interface names, not volatile IP addresses.

```ini
BIND_EXTRANET_NICNAME="eth2"
BIND_INTRANET_NICNAME="eth1"
BIND_ADMIN_NICNAME="eth0"
```

At render time, the local DNSForge agent resolves these NIC names into canonical runtime keys:

```ini
BIND_EXTRANET_IP=<resolved IPv4>
BIND_INTRANET_IP=<resolved IPv4>
BIND_ADMIN_IP=<resolved IPv4>
```

`BIND_EXTRANET_NICNAME` is the external/client-facing side for internet, cloud or partner clients.
`BIND_INTRANET_NICNAME` is the internal side for enterprise clients and proxy-authoritative transfers.
`BIND_ADMIN_NICNAME` is used for BIND administration and RNDC/statistics controls.

If a node has a single interface, all three NIC values default to the admin interface.
Generated BIND listen lists are de-duplicated, so a single-interface node does not produce repeated listen addresses.

`BIND_EXTRANET_IP`, `BIND_INTRANET_IP` and `BIND_ADMIN_IP` have been fully removed. Runtime rendering uses only `BIND_EXTRANET_IP`, `BIND_INTRANET_IP` and `BIND_ADMIN_IP`, derived from the configured NIC names.
