ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

# Cluster

## Modes supportés

```text
proxy-vip                    Keepalived Active/Passive
authoritative-replication    Primary + Secondary via AXFR/IXFR/TSIG
```

## Commandes

```bash
dnsforge cluster init
dnsforge cluster status
# or
 dnsforge cluster status --setup-file /etc/dnsforge/setup.conf
dnsforge cluster validate
dnsforge cluster sync
```

## Règles

- Proxy : VIP autorisée, Keepalived généré.
- Authoritative : pas de VIP ; modèle Primary/Secondary DNS.
- TSIG obligatoire pour AXFR/IXFR dans le modèle authoritative.

---
Copyright
© IRIVEN Group — All Rights Reserved
