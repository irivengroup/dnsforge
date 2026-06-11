ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

# Configuration Python native

## Objectif

La v8.9 rend `dnsforge configure` natif Python.

Le workflow est désormais :

```text
validate Python
render Python
configure plan Python
apply Python
```

Les scripts Bash historiques sont conservés dans `legacy/bash/`, mais ne sont plus appelés par `dnsforge configure`.

## Commandes

```bash
./bin/dnsforge configure proxy proxy01 --type forwarder --dry-run
./bin/dnsforge configure proxy proxy01 --type hybrid
./bin/dnsforge configure authoritative auth01 --dry-run
```



---

Copyright
© IRIVEN Group — All Rights Reserved

