# ZoneForge DNSaaS

> Plateforme de Déploiement et de Configuration DNS as a Service

[Documentation](./docs/index.md) · [Architecture](#architecture) · [Fonctionnalités](#fonctionnalités) · [Sécurité](#sécurité) · [Exploitation](#exploitation)

---

## Présentation

ZoneForge DNSaaS est une plateforme de déploiement, de configuration et d'exploitation DNS destinée aux environnements entreprise.

Elle permet de construire, sécuriser, automatiser et exploiter des infrastructures DNS modernes basées sur BIND 9, avec une approche orientée **DNS as a Service**, **Infrastructure as Code**, haute disponibilité, conformité et exploitation industrielle.

Le README présente le produit. Les procédures détaillées de déploiement, d'exploitation, de sécurité et de dépannage sont centralisées dans la [documentation](./docs/index.md).

---

## Fonctionnalités

### Services DNS

- DNS Authoritative basé sur BIND 9.
- DNS Proxy / Recursive.
- Split-Horizon DNS.
- Multi-cluster authoritative.
- Multi-VIP.
- Haute disponibilité avec Keepalived.
- Catalogue centralisé des zones.
- Gestion des Zones via `zone-manager.sh`.

### Sécurité DNS

- DNSSEC.
- TSIG pour les transferts de zones.
- RNDC avec génération automatique du secret si absent.
- RPZ / DNS Firewall sur les services récursifs.
- Blocage de RPZ sur les nœuds authoritative.
- Validation stricte des settings avant rendu et déploiement.

### Déploiement et exploitation

- Génération automatisée des configurations BIND.
- Déploiement automatisé des rôles DNS Proxy et DNS Authoritative.
- Production Gate : preflight, diff de configuration, sauvegarde et rollback.
- Monitoring natif et healthchecks.
- Tests de conformité.
- Runbooks d'exploitation.

---

## Architecture

![Architecture ZoneForge DNSaaS](docs/images/zoneforge-dnsaas-architecture.png)

ZoneForge DNSaaS sépare clairement les rôles DNS récursifs/proxy et autoritatifs :

| Composant | Rôle |
|---|---|
| `dns-proxy` | Résolution récursive, cache, RPZ, filtrage, accès clients |
| `dns-authoritative` | Publication des zones, transferts TSIG, DNSSEC, VIP authoritative |
| `zone-manager.sh` | Gestion des Zones : create, read, update, disable, enable, delete |
| `settings/` | Paramètres par nœud et par rôle |
| `catalog/zones.yml` | Source de vérité des zones DNS |
| `tests/` | Contrôles de conformité, sécurité et rendu |

Pour les détails d'architecture, consulter [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md).

---

## Cas d'utilisation

ZoneForge DNSaaS est adapté aux contextes suivants :

- entreprise multi-sites ;
- datacenters privés ;
- cloud privé ;
- fournisseur de services managés ;
- environnement DNS critique ;
- plateforme interne DNS as a Service ;
- segmentation DNS interne, externe et partenaire ;
- exploitation standardisée de BIND 9.

---

## Sécurité

ZoneForge DNSaaS applique une séparation stricte des responsabilités :

```text
dns-proxy         : RPZ autorisé
dns-recursive     : RPZ autorisé
dns-authoritative : RPZ interdit
```

Les serveurs autoritatifs publient les données de référence. Les politiques de filtrage RPZ sont réservées aux services récursifs/proxy.

Voir :

- [Sécurité](./docs/SECURITY.md)
- [RPZ — DNS Firewall](./docs/SECURITY/RPZ.md)
- [Validation stricte des settings](./docs/SETTINGS-VALIDATION.md)

---

## Exploitation

L'exploitation détaillée est documentée dans `docs/` :

- [Déploiement](./docs/DEPLOYMENT.md)
- [Opérations](./docs/OPERATIONS.md)
- [Production Checklist](./docs/PRODUCTION-CHECKLIST.md)
- [Gestion des Zones](./docs/GESTION-DES-ZONES.md)
- [RNDC](./docs/RNDC-SECRET.md)
- [Monitoring](./docs/NATIVE-MONITORING.md)
- [Troubleshooting](./docs/TROUBLESHOOTING.md)

---

## Documentation

Le point d'entrée documentaire est :

[docs/index.md](./docs/index.md)

La documentation est organisée par contexte :

- présentation ;
- déploiement ;
- exploitation ;
- sécurité ;
- référence.

---

## Validation

Les tests de conformité sont regroupés dans :

```bash
./tests/run-all.sh
```

Des tests spécialisés sont disponibles par domaine :

```text
tests/settings/
tests/security/
tests/catalog/
tests/integration/
tests/monitoring/
tests/deployment/
```

---

## Copyright

© IRIVEN Group — All Rights Reserved
