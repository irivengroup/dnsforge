# ZoneForge DNSaaS

> Plateforme de Déploiement et de Configuration DNS as a Service

[Documentation](./docs/index.md) · [Architecture](#architecture) · [Fonctionnalités](#fonctionnalités) · [Sécurité](#sécurité)

---

## Présentation

ZoneForge DNSaaS est une plateforme de déploiement, de configuration et d'exploitation DNS destinée aux environnements entreprise.

Elle permet de construire, sécuriser, automatiser et exploiter des infrastructures DNS modernes basées sur BIND 9, avec une approche orientée **DNS as a Service**, **Infrastructure as Code**, haute disponibilité, conformité et gouvernance DNS.

Le README présente le produit. La documentation détaillée de déploiement, d'exploitation, de sécurité, de troubleshooting et de référence est centralisée dans [docs/index.md](./docs/index.md).

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

### Automatisation

- Génération automatisée des configurations BIND.
- Déploiement automatisé des rôles DNS Proxy et DNS Authoritative.
- Production Gate.
- Monitoring natif et healthchecks.
- Tests de conformité.

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

## Authors

Alfred TCHONDJO

Project Initiator — IRIVEN Group

---

## Copyright

© IRIVEN Group — All Rights Reserved


## Installation système

```bash
sudo ./install/install.sh --profile proxy-forwarder
sudo ./install/install.sh --profile proxy-hybrid
sudo ./install/install.sh --profile authoritative
```

Voir `docs/INSTALLATION.md`.

## Node configuration governance

After editing `/etc/dnsforge/setup.conf`, use the controlled configuration lifecycle:

```bash
sudo dnsforge config validate
sudo dnsforge config diff
sudo dnsforge config apply --reason "Describe the approved change"
sudo dnsforge config history
sudo dnsforge config rollback --id 1 --reason "Rollback approved change"
sudo dnsforge audit config
```

`setup.conf` remains the source of truth for the node. `dnsforge initialize` is still one-shot; later changes are applied through `dnsforge config apply`.

## CI / Quality gates

DNSForge CI is blocking and runs on Python 3.9, 3.11 and 3.13.

The pipeline enforces Ruff, mypy, pytest, coverage, Bandit, pip-audit, wheel build/install, and generated BIND configuration validation. In GitHub Actions, skipped tests are forbidden; local runs may skip BIND validation only when BIND tools are not installed.


## Catalog Zones

DNSForge 10.9 introduces Enterprise catalog zone governance.

```bash
sudo dnsforge catalog status
sudo dnsforge catalog enable --reason "Enable catalog publication"
sudo dnsforge catalog sync --reason "Publish active authoritative zones"
sudo dnsforge catalog list
sudo dnsforge catalog validate
sudo dnsforge audit catalog
```

Catalog sync publishes active eligible zones from the DNSForge zone catalog and writes the generated catalog zone into the native BIND layout for the current distribution.
## Authoritative Cluster Sync

```bash
sudo dnsforge cluster peers
sudo dnsforge cluster diff
sudo dnsforge cluster sync --dry-run --reason "Review authoritative sync"
sudo dnsforge cluster sync --reason "Apply authoritative sync"
```

Cluster sync is authoritative-only. Proxy nodes consume authoritative VIP/IP endpoints but are not HA cluster members.


## Release archive packaging

DNSForge release archives include the built wheel and source archive under `dist/`.
The repository itself must remain free of caches, build directories and egg metadata.

```bash
sudo python tools/clean.py --fix
python tools/clean.py --check-source
python -m build
sudo python tools/clean.py --fix-release
python tools/clean.py --check-release
```

Install from a release archive:

```bash
sudo ./install/install.sh --profile authoritative
sudo dnsforge initialize --render-only
sudo dnsforge initialize --apply
```
