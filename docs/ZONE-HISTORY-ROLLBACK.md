ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

# Zone History / Diff / Rollback

## Version active

```bash
dnsforge zone show example.com
```

`zone show <zone>` affiche toujours la version active actuelle.

## Historique

```bash
dnsforge zone history example.com
```

## Afficher une version historique

```bash
dnsforge zone show --zone example.com --version 2
```

La forme compatible suivante reste acceptée :

```bash
dnsforge zone show example.com --version 2
```

## Diff

```bash
dnsforge zone diff --zone example.com --from 1 --to 2
```

## Rollback

```bash
dnsforge zone rollback --zone example.com --version 1
```

Le rollback crée une nouvelle version courante.

---
Copyright
© IRIVEN Group — All Rights Reserved
