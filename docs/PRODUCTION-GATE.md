ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](./index.md) | [Architecture](./ARCHITECTURE.md) | [Déploiement](./DEPLOYMENT.md) | [Exploitation](./OPERATIONS.md) | [Sécurité](./SECURITY.md) | [Troubleshooting](./TROUBLESHOOTING.md) | [Checklist](./PRODUCTION-CHECKLIST.md)

# Production Gate

## Objectif

La v5.9 ajoute des garde-fous avant application d'une configuration DNS en production.

## Outils

```text
src/tools/deployment/preflight-production-gate.sh
src/tools/deployment/diff-rendered-config.sh
src/tools/deployment/rollback-latest.sh
```

## Séquence recommandée

```bash
./src/dnsProxyDeploy.sh <node> --render-only
./src/tools/deployment/preflight-production-gate.sh src/render/dns-proxy/<node>
./src/tools/deployment/diff-rendered-config.sh src/render/dns-proxy/<node>
sudo ./src/tools/backup-binddns.sh
sudo ./src/dnsProxyDeploy.sh <node>
```

Pour un authoritative :

```bash
./src/dnsAuthoritativeDeploy.sh <node> --render-only
./src/tools/deployment/preflight-production-gate.sh src/render/dns-authoritative/<node>
./src/tools/deployment/diff-rendered-config.sh src/render/dns-authoritative/<node>
sudo ./src/tools/backup-binddns.sh
sudo ./src/dnsAuthoritativeDeploy.sh <node>
```

## Rollback rapide

```bash
sudo ./src/tools/deployment/rollback-latest.sh
```

## Contrôles effectués

```text
- existence du rendu ;
- présence de named.conf ;
- absence de placeholders ;
- named-checkconf si disponible ;
- diff live vs rendu ;
- sauvegarde exploitable avant application.
```

## Tests

```bash
./tests/deployment/check-production-gate-tools.sh
./tests/deployment/check-production-gate-render.sh
```

---

[← Retour à l'index](./index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
