ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service


# BindDNS Enterprise Red Hat

BindDNS Enterprise fournit un socle de déploiement et d'exploitation DNS pour environnements Red Hat / RHEL-like.

Le projet couvre deux rôles :

- **dns-proxy** : nœuds DNS consommés par les clients, sans VIP, configurables en DNS1/DNS2.
- **dns-authoritative** : nœuds DNS autoritaires globaux avec VIP interne, non exposés directement aux clients externes.

## Documentation

Le point d'entrée documentaire est :

- [docs/index.md](docs/index.md)

## Commandes rapides

```bash
cd /opt/binddns-enterprise

./src/dnsProxyDeploy.sh <node> --dry-run
sudo ./src/dnsProxyDeploy.sh <node>

./src/dnsAuthoritativeDeploy.sh <node> --dry-run
sudo ./src/dnsAuthoritativeDeploy.sh <node>
```

## Validation rapide

```bash
named-checkconf -z /etc/named.conf
rndc status
systemctl status named --no-pager
```

Consulter `docs/DEPLOYMENT.md`, `docs/OPERATIONS.md` et `docs/PRODUCTION-CHECKLIST.md` pour les procédures complètes.

## Sécurité intégrée

- TSIG
- RNDC limité ADM
- RPZ côté proxy
- RRL
- DNSSEC validation
- SELinux
- firewalld conditionnel

## Version courante

`v3.9`

## v3.9.1

Correction importante : les DNS Proxy peuvent aussi être autoritaires pour certaines zones.

Ajouts :

- `src/build/dns-proxy/zones/external/master/`
- `src/build/dns-proxy/zones/internal/master/`
- génération automatique des index master proxy ;
- copie automatique des fichiers `.zone` proxy master ;
- documentation et runbooks mis à jour.

## v4.0

La v4.0 ajoute une suite de validation complète :

```bash
./tests/run-all.sh
```

Voir :

- [Validation complète](docs/VALIDATION.md)
- [Runbook validation](docs/RUNBOOKS/RUN-VALIDATION.md)

## v4.1

La v4.1 ajoute l'outillage TSIG :

```bash
./src/tools/generate-tsig.sh xfr-shared-key
./src/tools/check-secrets.sh
```

## v4.2

La v4.2 corrige la cohérence RPZ :

- `50-rpz.conf.j2` est désormais rendu et inclus dans la vue récursive interne ;
- ajout de tests de cohérence projet ;
- ajout du document `docs/PROJECT-COHERENCE.md`.

## v4.3

La v4.3 ajoute l'audit de rendu :

```bash
./tests/render/check-render-settings.sh
./tests/run-all.sh
```

Voir [Audit de rendu](docs/RENDER-AUDIT.md).

## v4.4

La v4.4 ajoute les artefacts de supervision :

```bash
./tests/monitoring/check-monitoring-templates.sh
./tests/monitoring/check-rendered-monitoring.sh
```

Voir [Monitoring](docs/MONITORING.md).

## v4.5

La v4.5 formalise la haute disponibilité DNS Proxy sans VIP :

```bash
./tests/proxy-ha/check-proxy-ha-design.sh
DNS1=<DNS1_IP> DNS2=<DNS2_IP> TEST_ZONE=<ZONE> ./tests/proxy-ha/check-proxy-pair-smoke.sh
```

Voir [HA DNS Proxy sans VIP](docs/DNS-PROXY-HA.md).

## v4.6

La v4.6 ajoute le durcissement Red Hat/BIND :

```bash
./tests/security/check-hardening-source.sh
./tests/security/check-file-permissions-policy.sh
```

Voir [Durcissement](docs/HARDENING.md).


## v4.8

La v4.8 retire la génération HTML du cycle actif et ajoute un socle DNSSEC Enterprise optionnel :

```bash
./tests/dnssec/check-dnssec-templates.sh
./tests/dnssec/check-dnssec-render.sh
```

Voir [DNSSEC](docs/DNSSEC.md).

## v4.9

La v4.9 ajoute l'outillage sauvegarde/restauration :

```bash
sudo ./src/tools/backup-binddns.sh
sudo ./src/tools/list-backups.sh
sudo ./src/tools/restore-binddns.sh /var/backups/binddns/<timestamp>.tar.gz
```

Voir [Backup / Restore](docs/BACKUP-RESTORE.md).

## v5.0

La v5.0 aligne les inventaires avec le code et ajoute le support multi-VIP authoritative :

```bash
AUTHORITATIVE_BACK_IP=("192.0.2.10" "192.0.2.20")
```

Voir [Inventaires](docs/INVENTORIES.md).

## v5.1

Tests d'intégration multi-VIP authoritative côté proxy.

## v5.2

Routing DNS par zone vers clusters authoritative nommés.

## v5.3

ACL par vue et par zone, avec vue partenaire optionnelle.

## v5.5

Catalogue central des zones avec génération split-horizon.

## v5.6

DNSSEC Enterprise renforcé pour les zones publiques du catalogue.

## v5.7

Monitoring natif BindDNS : healthcheck, rndc stats, export métriques texte et timer systemd.

## v5.8

HA DNS Proxy optionnelle avec VIP, mode DNS1/DNS2 sans VIP conservé par défaut.

## v5.9

Production Gate : preflight, diff, backup obligatoire et rollback latest.

## v6.0

Renommage structurel :

```text
src/inventories/ -> src/settings/
tests/fixtures/inventories/ -> tests/fixtures/settings/
```

Les scripts, tests, docs et runbooks sont alignés sur `settings`.

## v6.1

Normalisation universelle des listes : `AUTHORITATIVE_BACK_IP="ip1 ; ip2, ip3 ip4"`.

## v6.2

Validation stricte des settings avant rendu/déploiement.

## v6.3

Outil de gestion du cycle de vie des zones : CRUD, disable/enable, delete.

## v6.4

Durcissement du cycle de vie des zones : `zone-manager.sh` 100% shell/awk, sans dépendance Python.

## v6.5

Gestion automatique du RNDC secret : `RNDC_KEY_NAME=rndc-key` par défaut, `RNDC_SECRET` généré si absent.


---

Copyright
© IRIVEN Group — All Rights Reserved


## DNS Firewall (RPZ)

ZoneForge DNSaaS implémente les RPZ uniquement sur les services récursifs/proxy.

L'utilisation de RPZ sur les services autoritatifs est interdite et bloquée par la validation stricte de la plateforme.

## v7.1

- RPZ interdit sur les nœuds authoritative.
- RPZ autorisé uniquement sur les services récursifs/proxy.
- Tests de conformité RPZ ajoutés.

## v7.2

Validation consolidée dans `src/libs/lib-settings-validate.sh`.


## Architecture

![Architecture ZoneForge DNSaaS](docs/images/zoneforge-dnsaas-architecture.png)

## v7.3

- Ajout de l’image d’architecture dans `docs/images/`.
- Affichage de l’architecture dans la section README Architecture.
