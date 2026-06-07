ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](./index.md) | [Architecture](./ARCHITECTURE.md) | [Déploiement](./DEPLOYMENT.md) | [Exploitation](./OPERATIONS.md) | [Sécurité](./SECURITY.md) | [Troubleshooting](./TROUBLESHOOTING.md) | [Checklist](./PRODUCTION-CHECKLIST.md)

# Validation stricte des settings

## Objectif

La v6.2 ajoute une validation stricte des settings avant rendu/déploiement.

## Bibliothèque

```text
src/libs/lib-settings-validate.sh
```

## Contrôles principaux

```text
- rôle cohérent ;
- IPv4 valides ;
- listes IP valides ;
- secrets non vides et sans placeholder ;
- DNS_FORWARD_POLICY cohérent ;
- DNSSEC complet si activé ;
- HA Proxy complète si activée.
```

## Tests

```bash
./tests/settings/check-settings-strict-validation.sh
./tests/settings/check-settings-strict-negative.sh
```

---

[← Retour à l'index](./index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
