ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

# Plan de configuration Python

## Objectif

La v8.8 ajoute un plan de configuration Python pour `dnsforge configure`.

Le moteur Bash historique reste utilisé en mode `apply`, mais `--dry-run` est entièrement piloté par Python.

## Commandes

Proxy forwarder :

```bash
./bin/dnsforge configure proxy proxy01 --type forwarder --dry-run
```

Proxy hybrid :

```bash
./bin/dnsforge configure proxy proxy01 --type hybrid --dry-run
```

Authoritative :

```bash
./bin/dnsforge configure authoritative auth01 --dry-run
```

## Composants

```text
ConfigurePlan
ConfigureStep
ConfigurePlanner
```

## Rôle

```text
validate -> render -> configure plan -> apply
```



---

Copyright
© IRIVEN Group — All Rights Reserved

