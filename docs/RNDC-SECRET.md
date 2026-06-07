ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](./index.md) | [Architecture](./ARCHITECTURE.md) | [Déploiement](./DEPLOYMENT.md) | [Exploitation](./OPERATIONS.md) | [Sécurité](./SECURITY.md) | [Troubleshooting](./TROUBLESHOOTING.md) | [Checklist](./PRODUCTION-CHECKLIST.md)

# Gestion automatique du RNDC secret

## Objectif

La v6.5 rend `RNDC_KEY_NAME` et `RNDC_SECRET` optionnels dans les settings.

## Comportement par défaut

```bash
RNDC_KEY_NAME="rndc-key"
```

Si `RNDC_SECRET` n'est pas défini, il est généré automatiquement.

## Emplacement généré

```text
src/settings/.generated/<role>/<node>/rndc.secret
```

Permissions : répertoire `0700`, fichier `0600`.

## Rotation manuelle

```bash
./src/tools/rndc-secret.sh rotate --role dns-proxy --node srv02
```

Afficher le chemin du secret :

```bash
./src/tools/rndc-secret.sh show --role dns-proxy --node srv02
```

S'assurer qu'un secret existe :

```bash
./src/tools/rndc-secret.sh ensure --role dns-proxy --node srv02
```

## Tests

```bash
./tests/rndc/check-rndc-secret-generation.sh
./tests/rndc/check-rndc-settings-optional.sh
```

---

[← Retour à l'index](./index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
