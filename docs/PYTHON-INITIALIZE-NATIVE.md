ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

# Initialisation Python native

## Objectif

La v8.9 rend `dnsforge initialize` natif Python.

Le workflow est désormais :

```text
validate Python
render Python
initialize plan Python
apply Python
```

Les scripts Bash historiques sont conservés dans `legacy/bash/`, mais ne sont plus appelés par `dnsforge initialize`.

## Commandes

```bash
./bin/dnsforge initialize --dry-run
./bin/dnsforge initialize
./bin/dnsforge initialize --dry-run
```



---

Copyright
© IRIVEN Group — All Rights Reserved

