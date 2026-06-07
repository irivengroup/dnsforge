ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](../index.md) | [Architecture](../ARCHITECTURE.md) | [Déploiement](../DEPLOYMENT.md) | [Exploitation](../OPERATIONS.md) | [Sécurité](../SECURITY.md) | [Troubleshooting](../TROUBLESHOOTING.md) | [Checklist](../PRODUCTION-CHECKLIST.md)

# Runbook cycle de vie d'une zone

## Créer

```bash
./src/tools/zone-manager.sh create --name <zone> --type secondary --views "external, internal" --cluster A
```

## Contrôler

```bash
./src/tools/zone-manager.sh read --name <zone>
./src/tools/generate-zone-catalog.sh
```

## Rendre

```bash
./src/dnsProxyDeploy.sh <node> --render-only
```

## Désactiver

```bash
./src/tools/zone-manager.sh disable --name <zone>
```

## Supprimer

```bash
./src/tools/zone-manager.sh delete --name <zone> --force
```

---

[← Retour à l'index](../index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
