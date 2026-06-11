ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](./index.md) | [Architecture](./ARCHITECTURE.md) | [Déploiement](./DEPLOYMENT.md) | [Exploitation](./OPERATIONS.md) | [Sécurité](./SECURITY.md) | [Troubleshooting](./TROUBLESHOOTING.md) | [Checklist](./PRODUCTION-CHECKLIST.md)

# Normalisation universelle des listes

## Objectif

La v6.1 standardise les variables de type liste.

Les séparateurs acceptés sont l'espace, la virgule et le point-virgule. La virgule et le point-virgule peuvent être encadrés par des espaces.

## Exemples acceptés

```bash
AUTHORITATIVE_BACK_IP="10.0.0.1 10.0.0.2"
AUTHORITATIVE_BACK_IP="10.0.0.1,10.0.0.2"
AUTHORITATIVE_BACK_IP="10.0.0.1;10.0.0.2"
AUTHORITATIVE_BACK_IP="10.0.0.1 ; 10.0.0.2, 10.0.0.3"
```

## Clusters

```bash
AUTH_CLUSTER_A_BACK_IP="192.0.2.10"
AUTH_CLUSTER_B_BACK_IP="192.0.2.20, 192.0.2.21"
```

## Fonctions

```text

```

```bash
normalize_list
validate_ip_list
build_bind_ip_list
build_bind_tsig_list
```

## Tests

```bash
./tests/settings/check-list-normalization.sh
./tests/settings/check-authoritative-back-ip-list.sh
```

---

[← Retour à l'index](./index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
