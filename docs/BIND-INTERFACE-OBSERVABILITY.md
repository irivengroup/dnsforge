# BIND Interface Observability

DNSForge exposes the resolved NIC-to-IP mapping in three operational paths:

- `dnsforge network preview` for preflight output before rendering or initialize.
- `dnsforge network audit` for machine-readable audit output.
- `dnsforge status` and `dnsforge doctor` for day-two operations.

The setup file remains NIC-based only. Runtime keys are resolved by the agent:

- `BIND_EXTRANET_IP`
- `BIND_INTRANET_IP`
- `BIND_ADMIN_IP`

Legacy aliases `FRONT_IP`, `BACK_IP`, and `ADM_IP` are not supported.

## Exporting diagnostics

Use the export command to persist the exact NIC-to-IP resolution used by DNSForge before BIND rendering:

```bash
dnsforge network export --setup-file /etc/dnsforge/setup.conf --format json --output /var/log/dnsforge/bind-interface-diagnostics.json
```

The JSON payload uses the stable schema `dnsforge.bind-interface-diagnostics.v1` and is suitable for CI artifacts or monitoring collectors.
