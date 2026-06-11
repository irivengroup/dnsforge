ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

# Commandes d'exploitation

```bash
dnsforge status
dnsforge health
dnsforge doctor
dnsforge backup create
dnsforge backup list
dnsforge restore --backup /var/backups/dnsforge/dnsforge-YYYYMMDD-HHMMSS.tar.gz --dry-run
dnsforge migrate --to proxy-forwarder
dnsforge migrate --to proxy-hybrid
```

Migration supportée uniquement entre `proxy-forwarder` et `proxy-hybrid`.

---
Copyright
© IRIVEN Group — All Rights Reserved
