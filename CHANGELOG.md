## v8.0

- README réécrit comme document de présentation produit.
- Documentation opérationnelle recentrée dans `docs/`.
- `docs/index.md` restructuré par contexte : Présentation, Déploiement, Exploitation, Sécurité, Référence.
- Image d'architecture explicitement référencée dans le README.
- Renommage documentaire `Zone Lifecycle` vers `Gestion des Zones`.
- Références alignées sur `zone-manager.sh`.

## v7.3

- Ajout de `docs/images/zoneforge-dnsaas-architecture.png`.
- Insertion de l’image d’architecture dans le README.

## v7.2

- Fusion de la logique utile dans `src/libs/lib-settings-validate.sh`.
- Suppression de l'ancienne bibliothèque de validation séparée.
- Réalignement des scripts et tests sur `lib-settings-validate.sh`.
- Ajout du test `check-validation-library-consolidation.sh`.
- Ajout de la documentation `VALIDATION-LIBRARY.md`.

## v7.1

- RPZ interdit sur les nœuds `dns-authoritative`.
- Ajout du test `check-rpz-authoritative-forbidden.sh`.
- Ajout du test `check-rpz-authoritative-render-clean.sh`.
- Documentation RPZ alignée sur les bonnes pratiques DNS.
- Checklist production mise à jour.

ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

## v6.5

- Ajout de `src/libs/lib-rndc.sh`.
- Ajout de `src/tools/rndc-secret.sh`.
- `RNDC_KEY_NAME` vaut `rndc-key` par défaut.
- `RNDC_SECRET` est généré automatiquement si absent.
- Suppression de l'obligation de déclarer RNDC dans les settings.
- Ajout de tests de génération et rotation RNDC.

## v6.4

- Remplacement de l’implémentation Python du lifecycle par Bash/AWK.
- Suppression de la dépendance runtime Python pour le CRUD des zones.
- Tests CRUD/disable/enable/delete fiabilisés.

## v6.3

- Ajout de `src/tools/zone-manager.sh`.
- CRUD zone dans le catalogue central.
- Support disable/enable via `disabled_zones`.
- Tests positifs et négatifs du lifecycle.

## v6.2

- Ajout de `src/libs/lib-settings-validate.sh`.
- Validation stricte proxy et authoritative.
- Tests positifs et négatifs de validation.

## v6.1

- Ajout de `src/libs/lib-network.sh`.
- Normalisation universelle des listes.
- `AUTHORITATIVE_BACK_IP` et `AUTH_CLUSTER_*_BACK_IP` acceptent espace, virgule et point-virgule.
- Abandon du format tableau Bash pour les listes IP.

## v6.0

- Renommage de `src/inventories/` en `src/settings/`.
- Renommage de `tests/fixtures/inventories/` en `tests/fixtures/settings/`.
- Adaptation des scripts de déploiement.
- Adaptation des tests, runbooks et docs.
- Ajout de `docs/SETTINGS.md`.
- Ajout de `tests/settings/check-settings-layout.sh`.

## v5.9

- Ajout Production Gate.
- Ajout diff live vs rendu.
- Ajout rollback latest.
- Tests de garde-fous de déploiement.

## v5.8

- HA DNS Proxy optionnelle.
- Mode par défaut conservé : DNS1/DNS2 sans VIP.
- Ajout templates Keepalived proxy.
- Ajout healthcheck proxy HA.
- Tests HA proxy optionnelle.

## v5.7

- Ajout des scripts natifs de monitoring.
- Ajout de healthcheck DNS/RNDC/statistics-channel.
- Ajout de collecte `rndc stats`.
- Ajout d'un export métriques texte.
- Ajout timer systemd healthcheck.

## v5.6

- Ajout de la politique DNSSEC enterprise.
- DNSSEC automatique sur zones publiques master du catalogue.
- Tests DNSSEC enterprise templates/render/catalog.
- Runbook DNSSEC zone publique.

## v5.5

- Ajout de `src/build/catalog/zones.yml`.
- Ajout du générateur de catalogue de zones.
- Génération split-horizon master/secondary/forward.
- Tests catalog generate/render.

## v5.3

- Ajout des ACL par zone.
- Ajout de la vue partner.
- Ajout des zones partner master/secondary/forward.
- Test d'intégration `check-zone-acl-render.sh`.

## v5.2

- Clusters authoritative nommés.
- Routing secondary/forward par cluster.
- Indexation récursive des zones.
- Test d'intégration zone-to-cluster.

## v5.1

- Rendu multi-lignes robuste via Perl pour variables BIND.
- Fixtures et tests d'intégration multi-VIP.
- Validation forwarders, primaries, allow-notify.

## v5.0

- Alignement des paramètres d'inventaire avec le code.
- `AUTHORITATIVE_BACK_IP` supporte plusieurs VIP/IPs.
- Ajout de `lib-settings.sh`.
- Rendu BIND multi-forwarders, multi-primaries et multi-allow-notify.
- Ajout des tests d'inventaire.
- Mise à jour de `docs/INVENTORIES.md`.

## v4.9

- Ajout de `backup-binddns.sh`.
- Ajout de `restore-binddns.sh`.
- Ajout de `list-backups.sh`.
- Ajout des tests backup.
- Mise à jour de `BACKUP-RESTORE.md` et `DISASTER-RECOVERY.md`.
- Ajout du runbook backup/restore.

## v4.8

- Retrait de la génération HTML du cycle actif.
- Ajout du socle DNSSEC Enterprise optionnel.
- Ajout des templates DNSSEC policy/options.
- Ajout du template de zone authoritative signée.
- Ajout des tests DNSSEC.
- Mise à jour de `docs/DNSSEC.md`.
- Ajout du runbook `DNSSEC-ROLLOVER.md`.

## v4.7

- Ajout de `src/tools/build-doc-site.sh`.
- Ajout de `src/tools/build-doc-site.py`.
- Ajout du répertoire `site/`.
- Ajout des tests de génération et liens HTML.
- Ajout de `docs/DOC-SITE.md`.
- Ajout du runbook `BUILD-DOC-SITE.md`.

## v4.6

- Ajout du profil systemd hardening pour named.
- Ajout des tests de durcissement.
- Ajout de `docs/HARDENING.md`.
- Ajout du runbook `APPLY-HARDENING.md`.

## v4.5

- Formalisation de la HA DNS Proxy sans VIP.
- Ajout de `docs/DNS-PROXY-HA.md`.
- Ajout du runbook `FAILOVER-PROXY.md`.
- Ajout des tests `tests/proxy-ha/check-proxy-ha-design.sh` et `check-proxy-pair-smoke.sh`.

## v4.4

- Ajout des artefacts Prometheus / Telegraf / Grafana.
- Ajout du rendu `/opt/binddns/monitoring`.
- Ajout des tests monitoring.
- Mise à jour de `docs/MONITORING.md`.
- Ajout du runbook `SETUP-MONITORING.md`.

## v4.3

- Ajout de l'audit de rendu complet.
- Ajout de `tests/render/check-render-settings.sh`.
- Ajout de contrôles des chemins générés.
- Ajout de contrôles anti-placeholders dans `src/render`.
- Ajout de `docs/RENDER-AUDIT.md`.
- Ajout du runbook `RUN-RENDER-AUDIT.md`.

## v4.2

- Correction : `50-rpz.conf.j2` n'est plus orphelin.
- RPZ rendue sous `/etc/named/rpz/50-rpz.conf`.
- RPZ incluse dans la vue récursive interne.
- Ajout des tests `tests/project/check-template-usage.sh`, `check-rpz-coherence.sh`, `check-project-coherence.sh`.
- Ajout de `docs/PROJECT-COHERENCE.md`.

## v4.1

- Ajout de `src/tools/generate-tsig.sh`.
- Ajout de `src/tools/check-secrets.sh`.
- Ajout de la documentation `docs/SECRETS.md`.
- Mise à jour du runbook `ROTATE-TSIG`.
- Ajout du test `check-tsig-tooling.sh`.

## v4.0

- Ajout d'une suite de validation complète.
- Ajout de `tests/run-all.sh`.
- Ajout de contrôles BIND, zones, RPZ, RNDC, SELinux, firewalld, documentation et style.
- Ajout du document `docs/VALIDATION.md`.
- Ajout du runbook `RUNBOOKS/RUN-VALIDATION.md`.

## v3.9.1

- Ajout du support des zones `master` sur les DNS Proxy.
- Les proxys peuvent être autoritaires pour certaines zones locales.
- Ajout de `external/master` et `internal/master` côté proxy.
- Génération automatique des index `master/zones.index.conf`.
- Copie automatique des fichiers `.zone` proxy vers `/var/named/master/...`.
- Documentation et runbooks alignés.

## v3.9

- Industrialisation des zones.
- Génération automatique des `zones.index.conf`.
- Tests `dns-validation`.
- Runbooks `ADD-ZONE` et `REMOVE-ZONE` mis à jour.
- Archive régénérée avec dossier racine `binddns-enterprise-redhat-v3.9`.

# Changelog

## v3.6 complete

- Documentation complète avec `docs/index.md`.
- Liens retour vers l'index en tête et fin de document.
- Scripts de déploiement proxy et authoritative.
- Librairies communes : logging, rendu, validation, permissions, SELinux, firewall, bind.
- Templates BIND formatés et lisibles.
- Inventaires séparés par rôle.
- Tests smoke, validation, style et documentation.
- Mode `--skip-install`.
- Modes `--dry-run`, `--render-only`, `--validate-only`, `--audit`, `--rollback latest`.


---

Copyright
© IRIVEN Group — All Rights Reserved
