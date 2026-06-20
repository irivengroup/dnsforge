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
