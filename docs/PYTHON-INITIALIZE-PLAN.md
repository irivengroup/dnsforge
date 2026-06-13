ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

# Plan d’initialisation Python

## Objectif

La v8.8 ajoute un plan de configuration Python pour `dnsforge initialize`.

Le moteur Python produit le plan et applique directement le déploiement BIND : sauvegarde complète, rendu, copie, validation et redémarrage.

## Commandes

Proxy forwarder :

```bash
dnsforge initialize --dry-run
```

Proxy hybrid :

```bash
dnsforge initialize --dry-run
```

Authoritative :

```bash
dnsforge initialize --dry-run
```

## Composants

```text
InitializePlan
InitializeStep
InitializePlanner
```

## Rôle

```text
validate -> render -> initialize plan -> apply
```



---

Copyright
© IRIVEN Group — All Rights Reserved

