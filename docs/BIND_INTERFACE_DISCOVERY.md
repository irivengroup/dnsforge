# BIND Interface Discovery


## Runtime resolution audit

DNSForge records the exact NIC to IPv4 resolution used during BIND rendering.
The generated runtime settings expose:

- `BIND_EXTRANET_RESOLVED_FROM`
- `BIND_INTRANET_RESOLVED_FROM`
- `BIND_ADMIN_RESOLVED_FROM`
- `BIND_INTERFACE_AUDIT`

These values are runtime-only observability keys. Operators must keep
`setup.conf` based on NIC names (`BIND_EXTRANET_NICNAME`,
`BIND_INTRANET_NICNAME`, `BIND_ADMIN_NICNAME`).
