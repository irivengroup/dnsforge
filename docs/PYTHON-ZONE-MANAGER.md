ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

# Gestion des Zones Python native

## Objectif

La v8.7 migre `dnsforge zone` vers Python natif.

## Commandes

```bash
dnsforge zone list
dnsforge zone get --name example.com
dnsforge zone create --name example.com --type master --views external,internal --cluster A
dnsforge zone disable --name example.com
dnsforge zone enable --name example.com
dnsforge zone delete --name example.com
```

## Catalogue

```text
/etc/dnsforge/zones.yml
```



---

Copyright
© IRIVEN Group — All Rights Reserved

