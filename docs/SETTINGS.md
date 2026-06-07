ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](./index.md) | [Architecture](./ARCHITECTURE.md) | [Déploiement](./DEPLOYMENT.md) | [Exploitation](./OPERATIONS.md) | [Sécurité](./SECURITY.md) | [Troubleshooting](./TROUBLESHOOTING.md) | [Checklist](./PRODUCTION-CHECKLIST.md)

# Settings

## Objectif

La v6.0 remplace l'ancien emplacement `src/inventories/` par `src/settings/`.

Les fichiers `.env` sont des paramètres de rendu et de déploiement par nœud.

## Structure

```text
src/settings/
├── dns-proxy/
│   ├── srv02.env
│   └── srv03.env
└── dns-authoritative/
    ├── svr01a.env
    └── svr01b.env
```

## Utilisation

```bash
./src/dnsProxyDeploy.sh srv02 --render-only
./src/dnsAuthoritativeDeploy.sh svr01a --render-only
```

## Fixtures

```text
tests/fixtures/settings/
```

## Validation

```bash
./tests/settings/check-settings-layout.sh
./tests/settings/check-settings-variables.sh
./tests/settings/check-authoritative-back-ip-list.sh
```

---

[← Retour à l'index](./index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
