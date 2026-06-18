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
dnsforge migrate --to proxy-forwarder --reason "Retour en mode forwarder"
dnsforge migrate --to proxy-hybrid --reason "Activation proxy hybrid"
```

Migration supportée uniquement entre `proxy-forwarder` et `proxy-hybrid`. Depuis v11.0.3, la migration réelle est transactionnelle : validation du profil courant, snapshot filesystem de `setup.conf` et des chemins BIND natifs, modification contrôlée du profil proxy, render complet, deploy, validation via le pipeline de déploiement, puis commit du snapshot. En cas d'échec, DNSForge restaure automatiquement `setup.conf` et les fichiers BIND capturés avant migration.

---
Copyright
© IRIVEN Group — All Rights Reserved
