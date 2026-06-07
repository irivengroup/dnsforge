ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](../index.md) | [Architecture](../ARCHITECTURE.md) | [Déploiement](../DEPLOYMENT.md) | [Exploitation](../OPERATIONS.md) | [Sécurité](../SECURITY.md) | [Troubleshooting](../TROUBLESHOOTING.md) | [Checklist](../PRODUCTION-CHECKLIST.md)

# Exécuter l'audit de rendu

## Objectif

Valider les configurations générées avant copie vers `/`.

## 1. Rendre tous les inventaires

```bash
./tests/render/check-render-settings.sh
```

## 2. Rendre un proxy précis

```bash
./tests/render/check-render-proxy.sh <node>
```

## 3. Rendre un authoritative précis

```bash
./tests/render/check-render-authoritative.sh <node>
```

## 4. Vérifier les chemins

```bash
./tests/render/check-render-paths.sh
```

## 5. Vérifier les placeholders

```bash
./tests/render/check-render-no-placeholders.sh
```

## 6. Vérifier les index

```bash
./tests/dns-validation/check-zone-indexes.sh
```

## 7. Validation finale

```bash
./tests/run-all.sh
```

---

[← Retour à l'index](../index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
