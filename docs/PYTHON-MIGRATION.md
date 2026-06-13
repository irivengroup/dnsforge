ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

# Migration Python progressive

## Objectif

La v8.5 introduit un vrai package Python `dnsforge` sans casser la base Bash existante.

Cette version est volontairement hybride :

```text
Python : CLI, modèle domaine, validation settings, orchestration
Bash   : moteur historique de rendu/configuration encore conservé
```

## Point d'entrée

```bash
dnsforge --help
```

## Commandes

Validation proxy :

```bash
dnsforge validate proxy <node> --type forwarder
dnsforge validate proxy <node> --type hybrid
```

Configuration proxy :

```bash
dnsforge initialize
dnsforge initialize --render-only
```

Authoritative :

```bash
dnsforge validate authoritative <node>
dnsforge initialize --render-only
```

Zones :

```bash
dnsforge zone list
```

## Étape suivante

Migrer progressivement :

```text
1. rendu BIND ;
2. zone manager ;
3. installation système ;
4. suppression des scripts Bash.
```



---

Copyright
© IRIVEN Group — All Rights Reserved

