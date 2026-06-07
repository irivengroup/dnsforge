ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](./index.md) | [Architecture](./ARCHITECTURE.md) | [Déploiement](./DEPLOYMENT.md) | [Exploitation](./OPERATIONS.md) | [Sécurité](./SECURITY.md) | [Troubleshooting](./TROUBLESHOOTING.md) | [Checklist](./PRODUCTION-CHECKLIST.md)

# Cohérence du projet

## Objectif

Ce document décrit les contrôles ajoutés pour éviter les écarts entre :

- les templates présents dans `src/build/` ;
- les scripts de rendu dans `src/libs/` ;
- les fichiers effectivement inclus dans BIND ;
- la documentation d'exploitation.

## Contrôle global

```bash
./tests/project/check-project-coherence.sh
```

Ce contrôle exécute :

```bash
./tests/project/check-template-usage.sh
./tests/project/check-rpz-coherence.sh
```

## Contrôle des templates inutilisés

```bash
./tests/project/check-template-usage.sh
```

Le test vérifie que les templates `.j2` sont réellement utilisés par les scripts ou les tests.

Les fichiers `.tpl` sont considérés comme des modèles réutilisables pour les administrateurs et ne sont pas obligatoirement rendus automatiquement.

## Contrôle RPZ

```bash
./tests/project/check-rpz-coherence.sh
```

Le contrôle vérifie que :

```text
src/build/dns-proxy/templates/50-rpz.conf.j2
```

est bien rendu vers :

```text
/etc/named/rpz/50-rpz.conf
```

et inclus dans la vue récursive interne via :

```bind
include "/etc/named/rpz/50-rpz.conf";
```

## Règle d'architecture RPZ

La RPZ ne doit pas être incluse globalement depuis `named.conf`.

Elle doit être attachée à la vue récursive, donc côté proxy, généralement dans la vue `internal`.

## Validation complète

```bash
./tests/run-all.sh
```

---

[← Retour à l'index](./index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
