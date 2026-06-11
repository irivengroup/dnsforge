ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

# Contexte Build dans le coeur DNSForge

## Changement

Le dossier historique :

```text
src/build/
```

est remplacé par :

```text
src/dnsforge/infrastructure/build/
```

## Emplacement canonique du catalogue

```text
src/dnsforge/infrastructure/build/catalog/zones.yml
```

## Justification DDD

Les artefacts `build`, le catalogue et les fichiers générés appartiennent au contexte infrastructure.

```text
src/dnsforge/
├── domain/
├── application/
├── infrastructure/
│   └── build/
└── interfaces/
```



---

Copyright
© IRIVEN Group — All Rights Reserved

