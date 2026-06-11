ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

# Produit Python v9.0

## Objectif

La v9.0 finalise la bascule du point d'entrée produit vers Python.

`dnsforge` porte désormais nativement :

```text
validate
render
initialize
zone
```

## Statut Bash

Les anciens scripts Bash ne sont plus dans le chemin produit `src/`.

Ils sont archivés dans :

```text
legacy/bash/
```

Ils ne sont plus appelés par le package Python `dnsforge`.

## Commandes

```bash
./bin/dnsforge validate proxy proxy01 --type forwarder
./bin/dnsforge render proxy proxy01 --type hybrid
./bin/dnsforge initialize proxy proxy01 --type forwarder --dry-run
./bin/dnsforge zone list
```

## Architecture

```text
src/dnsforge/
├── domain/
├── application/
├── infrastructure/
└── interfaces/
```



---

Copyright
© IRIVEN Group — All Rights Reserved

