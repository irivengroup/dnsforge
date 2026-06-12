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
./bin/dnsforge --help
```

## Commandes

Validation proxy :

```bash
./bin/dnsforge validate proxy <node> --type forwarder
./bin/dnsforge validate proxy <node> --type hybrid
```

Configuration proxy :

```bash
./bin/dnsforge proxy initialize <node> --type forwarder
./bin/dnsforge proxy initialize <node> --type hybrid --render-only
```

Authoritative :

```bash
./bin/dnsforge validate authoritative <node>
./bin/dnsforge authoritative initialize <node> --render-only
```

Zones :

```bash
./bin/dnsforge zone list
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

