ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](./index.md) | [Architecture](./ARCHITECTURE.md) | [Déploiement](./DEPLOYMENT.md) | [Exploitation](./OPERATIONS.md) | [Sécurité](./SECURITY.md) | [Troubleshooting](./TROUBLESHOOTING.md) | [Checklist](./PRODUCTION-CHECKLIST.md)

# Gestion des secrets

## Objectif

Les secrets ne doivent pas être codés en dur dans les templates ni dans le code.

## Secrets concernés

```text
TSIG_SECRET
RNDC_SECRET
KEEPALIVED_AUTH_PASS
```

## Vérifier les placeholders

```bash
./src/tools/check-secrets.sh
```

## Générer TSIG

```bash
./src/tools/generate-tsig.sh xfr-shared-key
```

## Bonnes pratiques

- Ne pas commiter `secrets/`.
- Utiliser un coffre de secrets en production.
- Appliquer la même clé TSIG uniquement aux nœuds participant à une même relation de transfert.
- Garder RNDC unique par nœud.

---

[← Retour à l'index](./index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
