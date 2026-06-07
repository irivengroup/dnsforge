ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](./index.md) | [Architecture](./ARCHITECTURE.md) | [Déploiement](./DEPLOYMENT.md) | [Exploitation](./OPERATIONS.md) | [Sécurité](./SECURITY.md) | [Troubleshooting](./TROUBLESHOOTING.md) | [Checklist](./PRODUCTION-CHECKLIST.md)

# Cycle de vie d'une zone

## Objectif

La v6.3 ajoute un outil CRUD pour gérer le cycle de vie des zones dans le catalogue central.

## Outil

```text
src/tools/zone-manager.sh
```

Depuis la v6.4, l’outil est implémenté en Bash/AWK uniquement et ne dépend plus de Python au runtime.

## Commandes

```bash
./src/tools/zone-manager.sh list
./src/tools/zone-manager.sh read --name example.com
```

Créer :

```bash
./src/tools/zone-manager.sh create \
  --name app.example.com \
  --type secondary \
  --views "external, internal" \
  --cluster A
```

Mettre à jour :

```bash
./src/tools/zone-manager.sh update \
  --name app.example.com \
  --type forward \
  --views internal \
  --cluster B
```

Désactiver / réactiver :

```bash
./src/tools/zone-manager.sh disable --name app.example.com
./src/tools/zone-manager.sh enable --name app.example.com
```

Supprimer :

```bash
./src/tools/zone-manager.sh delete --name app.example.com --force
```

## Désactivation

Une zone désactivée est déplacée sous `disabled_zones` dans le catalogue généré. Elle reste documentée mais n'est plus active.

## Tests

```bash
./tests/catalog/check-zone-manager.sh
./tests/catalog/check-zone-manager-negative.sh
```

---

[← Retour à l'index](./index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
