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

Migration supportée uniquement entre `proxy-forwarder` et `proxy-hybrid`. La migration réelle sauvegarde `setup.conf`, rend le layout BIND complet du profil cible, puis déploie les fichiers de configuration et de données BIND via le pipeline `render -> deploy`.

---
Copyright
© IRIVEN Group — All Rights Reserved
