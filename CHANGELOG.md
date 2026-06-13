# Changelog

## 10.6.9

- Added `install/upgrade.sh` for controlled DNSForge upgrades.
- Added `install/uninstall.sh` for safe uninstall and explicit purge flows.
- Added tests for install, upgrade and uninstall entrypoints.
- Ensured BIND packages are never removed unless `--purge --remove-bind` is explicitly requested.
- Removed Python cache artifacts from release trees.


## 10.6.4 - Zone Transaction Engine

- Added atomic zone change planning for forward/reverse mutations.
- Added rollback-on-persistence-failure for zone catalog commits.
- Added post-commit history snapshots only after successful catalog writes.
- Added transaction regression tests for failed commits and forward/reverse consistency.

# 10.6.0

- Split render and deploy as first-class application commands.
- Added `dnsforge deploy` for applying previously rendered native BIND trees.
- `dnsforge initialize` now orchestrates one-shot `backup -> render -> deploy -> lock`.
- Added deploy tests ensuring deployment does not create the initialization lock.

# 10.5.25

- Added advisory `mypy` CI gate.
- Added project-level mypy configuration for Python 3.9+.
- Added typing CI documentation.

# 10.5.0

- Reoriented `dnsforge initialize` as a BIND configuration takeover/deployment command.
- Removed package installation from the Python initialize/configure application service.
- Added complete BIND configuration backup using move + tar.gz before applying rendered files.
- Added BIND prerequisite validation: `named-checkconf`, `rndc`, `systemctl`.
- Made `/etc/dnsforge/setup.conf` the preferred node source of truth, with legacy per-role env files only as fallback.
- Updated initialize documentation to reflect install/ vs initialize responsibilities.

## v10.4

- Ajout commandes sécurité : `security history/rollback`, `acl`, `view`, `dnssec`, `rpz`, `cluster validate-security`.
- Ajout de `docs/SECURITY-COMMANDS.md`.

## v10.3

- `dnsforge configure` devient `dnsforge initialize`.
- Suppression de l'option publique `--skip-install`.
- Installation automatique de BIND via `install/install.sh` si absent.
- Ajout de `LinuxDistribution`, `OsReleaseReader`, `PackageManager`.

## v10.2

- Suppression définitive de `src/libs`.
- Portage des responsabilités Bash vers modules Python natifs.
- Ajout de `BooleanSetting`, `AddressListParser`, `CommandRunner`, `AtomicFileWriter`, `BackupFile`, `ServiceManager`, `BindTools`.
- Ajout de `docs/BASH-LIBS-MIGRATION.md`.

## v10.1

- `dnsforge zone show <zone>` affiche explicitement la version active courante.
- `dnsforge zone show --zone <zone> --version N` affiche une version historique.
- `dnsforge zone history <zone>` indique la version courante.
- Suppression définitive de `src/settings` du livrable.
- Configuration opérateur déportée vers `/etc/dnsforge/setup.conf`.
- Les modèles restent dans `src/dnsforge/infrastructure/profile/resources/`.

## v10.0

- Ajout Zone History / Diff / Rollback.
- Snapshots filesystem automatiques avant modification des zones.
- Commandes `zone history`, `zone show --version`, `zone diff`, `zone rollback`.

## v9.9

- Ajout du domaine `cluster`.
- Ajout de `dnsforge cluster init/status/validate/sync`.
- Support proxy cluster avec VIP Keepalived.
- Support authoritative cluster en modèle Primary/Secondary.
- Ajout des variables cluster dans les templates `setup.conf`.
- Ajout de `docs/CLUSTER.md`.

## v9.8

- Ajout de `dnsforge status`.
- Ajout de `dnsforge health`.
- Ajout de `dnsforge doctor`.
- Ajout de `dnsforge backup create/list`.
- Ajout de `dnsforge restore`.
- Ajout de `dnsforge migrate --to proxy-forwarder|proxy-hybrid`.
- Migration lourde proxy <-> authoritative interdite.

## v9.7

- Ajout du domaine `security`.
- Ajout des profils `standard`, `hardened`, `enterprise`, `paranoid`.
- Ajout de `dnsforge security show` et `dnsforge security audit`.
- Injection des options BIND de sécurité : DNS Cookies, RRL, minimal responses, qname minimization, serve-stale.
- Ajout de `docs/SECURITY.md`.

## v9.6

- Ajout de `dnsforge zone show`.
- Ajout de `dnsforge zone edit` avec `--add`, `--update`, `--delete`.
- Ajout du modèle `DnsRecord`.
- Extension du catalogue avec `records`.

## v9.5

- Ajout du modèle `ConfigurationProfile`.
- Ajout de `ProfileSettingsValidator`.
- Ajout de `ProfileAuditor`.
- Ajout de la commande `dnsforge profile audit`.
- Durcissement des règles par profil : authoritative, proxy-forwarder, proxy-hybrid.
- Ajout de `docs/CONFIGURATION-PROFILES.md`.

## v9.4

- Intégration des variables présentes dans `src/settings` dans les templates `setup.conf`.
- Modèles complets par profil : authoritative, proxy-forwarder, proxy-hybrid.
- Ajout du manifeste `src/dnsforge/infrastructure/profile/resources/VARIABLE-COVERAGE.md`.
- Ajout de `docs/SETUP-CONF-TEMPLATES.md`.

## v9.3

- Ajout de `install/install.sh`.
- Installation sous `/opt/dnsforge`.
- Création de `/etc/dnsforge`.
- Création des liens `/opt/dnsforge/settings` et `/opt/dnsforge/src/settings` vers `/etc/dnsforge`.
- Exposition globale de `/usr/local/bin/dnsforge`.
- Ajout des templates `setup.conf` par profil.
- Installation centralisée via `install/install.sh`.
- Ajout de `docs/INSTALLATION.md`.

## v9.2

- Intégration du dossier `build` dans `src/dnsforge/infrastructure/templates`.
- Déplacement du catalogue vers `src/dnsforge/infrastructure/templates/catalog/zones.yml`.
- Mise à jour de `ProjectPaths.build_root` et `ProjectPaths.catalog_file`.
- Suppression de l'ancien dossier `src/dnsforge/infrastructure/templates`.
- Correction du dossier racine dans l'archive ZIP : `ZoneForge-DNSaaS-v9.2`.

## v9.1

- Suppression du répertoire legacy du livrable produit.
- Suppression des derniers helpers legacy du package Python.
- Ajout de la commande `dnsforge audit`.
- Ajout de `ProductAuditor` et `ProductAuditReport`.
- Ajout du guide d'exploitation `docs/OPERATING-GUIDE.md`.
- Durcissement de la cohérence produit Python.

## v9.0

- Finalisation de la bascule produit vers Python.
- Suppression des références Python vers les anciens entrypoints Bash.
- Archivage des anciens scripts Bash sous `legacy/bash/`.
- Nettoyage de `ProjectPaths` pour retirer les helpers legacy.
- Ajout du test `check-dnsforge-product-python.sh`.
- Ajout de la documentation `PYTHON-PRODUCT-V9.md`.

## v8.9

- `dnsforge initialize` devient natif Python.
- Ajout de `ConfigureService`.
- Ajout de `PackageInstaller`, `FileInstaller`, `FirewalldManager`, `SELinuxManager`, `SystemdManager`.
- `configure` n'appelle plus les scripts Bash historiques.
- Les scripts Bash historiques sont déplacés vers `legacy/bash/`.
- Ajout de la documentation `PYTHON-CONFIGURE-NATIVE.md`.

## v8.8

- Ajout de `ConfigurePlan` et `ConfigureStep`.
- Ajout de `ConfigurePlanner`.
- Ajout de l'option `--dry-run` à `dnsforge initialize`.
- `dnsforge initialize --dry-run` produit un plan Python sans exécuter le moteur Bash.
- Documentation `PYTHON-CONFIGURE-PLAN.md`.

## v8.7

- Migration de `dnsforge zone` vers Python natif.
- Ajout du modèle `ZoneDefinition` et `ZoneType`.
- Ajout de l'adaptateur `ZoneCatalog`.
- Ajout des commandes `zone list/get/create/disable/enable/delete`.
- Ajout de la documentation `PYTHON-ZONE-MANAGER.md`.

## v8.6

- Ajout du rendu Python natif via `dnsforge render`.
- Ajout de `BindRenderTree` et `BindConfigFactory`.
- Ajout du modèle `ProxyRenderProfile`.
- Support natif des sorties `forwarder` et `hybrid`.
- Conservation du moteur Bash historique pour `configure`.

## v8.5

- Ajout d'un vrai package Python `src/dnsforge`.
- Suppression du point d’entrée historique `bin/dnsforge`; le wheel expose désormais le console script `dnsforge`.
- Ajout du modèle domaine `DnsRole`, `ProxyType`, `ProxySettings`, `AuthoritativeSettings`.
- Ajout de la validation Python des settings proxy/authoritative.
- Ajout de la commande `configure` en remplacement conceptuel de `deploy`.
- Conservation du moteur Bash existant via une couche legacy contrôlée.
- Ajout de la documentation `docs/PYTHON-MIGRATION.md`.

## v8.2

- README restauré comme document de présentation produit.
- Suppression des sections `Exploitation` et `Validation` du README.
- Ajout de la section `Authors`.
- Maintien du lien vers `docs/index.md` et de l'image d'architecture.

## v8.1

- Ajout des tests qualité documentaire.
- Validation des liens Markdown locaux.
- Validation des en-têtes et pieds de page de la documentation.
- Validation du périmètre produit du README.
- Validation de la structure contextuelle de `docs/index.md`.

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


- Validation stricte proxy et authoritative.
- Tests positifs et négatifs de validation.

## v6.1


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

- Ajout de `src/dnsforge/infrastructure/templates/catalog/zones.yml`.
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
- Mode ``.
- Modes `--dry-run`, `--render-only`, `--validate-only`, `--audit`, `--rollback latest`.


---

Copyright
© IRIVEN Group — All Rights Reserved

## v10.5.4 - Native BIND layout ownership

- Aligned DNSForge initialize with the product model: BIND deployment and complete BIND configuration management.
- Added OS-aware native BIND layout detection for Red Hat family, Debian/Ubuntu and SUSE.
- Removed runtime dependency on `/etc/dnsforge/generated/` and `/var/lib/dnsforge/`.
- Rendered modular BIND configuration into native layout paths: `/etc/named`, `/etc/bind`, `/var/named`, `/var/lib/bind`, `/var/lib/named`.
- Backup now moves the detected native BIND configuration and data paths before creating the tar.gz archive.
- Validation now targets the detected native `named.conf`.
- Systemd operations now use `named` or `bind9` according to the detected platform.
- Added native BIND layout tests.
