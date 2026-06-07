ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](./index.md) | [Architecture](./ARCHITECTURE.md) | [Déploiement](./DEPLOYMENT.md) | [Exploitation](./OPERATIONS.md) | [Sécurité](./SECURITY.md) | [Troubleshooting](./TROUBLESHOOTING.md) | [Checklist](./PRODUCTION-CHECKLIST.md)

# BindDNS Enterprise - Index documentaire

Ce dossier constitue le point d'entrée de la documentation d'exploitation.

## Documents principaux

- [Architecture](./ARCHITECTURE.md)
- [Déploiement](./DEPLOYMENT.md)
- [Exploitation quotidienne](./OPERATIONS.md)
- [Sécurité](./SECURITY.md)
- [Troubleshooting](./TROUBLESHOOTING.md)
- [Checklist de production](./PRODUCTION-CHECKLIST.md)

## Rôles DNS

- [DNS Proxy](./DNS-PROXY.md)
- [DNS Authoritative](./DNS-AUTHORITATIVE.md)

## Sécurité et composants

- [DNSSEC](./DNSSEC.md)
- [RPZ](./RPZ.md)
- [TSIG](./TSIG.md)
- [SELinux](./SELINUX.md)
- [Firewalld](./FIREWALLD.md)

## Projet et exploitation

- [Inventaires](./INVENTORIES.md)
- [Templates](./TEMPLATES.md)
- [Variables](./VARIABLES.md)
- [Backup / Restore](./BACKUP-RESTORE.md)
- [Disaster Recovery](./DISASTER-RECOVERY.md)
- [Monitoring](./MONITORING.md)

## Runbooks

- [Ajouter une zone](./RUNBOOKS/ADD-ZONE.md)
- [Supprimer une zone](./RUNBOOKS/REMOVE-ZONE.md)
- [Rotation TSIG](./RUNBOOKS/ROTATE-TSIG.md)
- [Rotation RNDC](./RUNBOOKS/ROTATE-RNDC.md)
- [Mise à jour BIND](./RUNBOOKS/UPGRADE-BIND.md)
- [Failover Authoritative](./RUNBOOKS/FAILOVER-AUTHORITATIVE.md)
- [Restaurer un serveur](./RUNBOOKS/RESTORE-SERVER.md)

- [Baseline sécurité](./SECURITY-BASELINE.md)

- [Gérer la RPZ](./RUNBOOKS/MANAGE-RPZ.md)

- [Industrialisation des zones](./ZONE-INDUSTRIALIZATION.md)

- [Validation complète](./VALIDATION.md)
- [Runbook validation](./RUNBOOKS/RUN-VALIDATION.md)

- [Gestion des secrets](./SECRETS.md)

- [Cohérence du projet](./PROJECT-COHERENCE.md)

- [Audit de rendu](./RENDER-AUDIT.md)
- [Runbook audit de rendu](./RUNBOOKS/RUN-RENDER-AUDIT.md)

- [Runbook supervision](./RUNBOOKS/SETUP-MONITORING.md)

- [HA DNS Proxy sans VIP](./DNS-PROXY-HA.md)
- [Runbook failover proxy](./RUNBOOKS/FAILOVER-PROXY.md)

- [Durcissement](./HARDENING.md)
- [Runbook durcissement](./RUNBOOKS/APPLY-HARDENING.md)
- [Runbook rollover DNSSEC](./RUNBOOKS/DNSSEC-ROLLOVER.md)
- [Runbook backup/restore](./RUNBOOKS/BACKUP-RESTORE.md)

- [Multi-VIP authoritative](./MULTI-AUTHORITATIVE-VIP.md)

- [Routing par zone vers clusters authoritative](./ZONE-CLUSTER-ROUTING.md)

- [ACL par vue et par zone](./ZONE-ACL.md)

- [Catalogue central des zones](./ZONE-CATALOG.md)

- [DNSSEC Enterprise](./DNSSEC-ENTERPRISE.md)
- [Runbook DNSSEC zone publique](./RUNBOOKS/DNSSEC-PUBLIC-ZONE.md)

- [Monitoring natif](./NATIVE-MONITORING.md)
- [Runbook healthcheck monitoring](./RUNBOOKS/MONITORING-HEALTHCHECK.md)

- [HA DNS Proxy optionnelle](./PROXY-HA-OPTIONAL.md)
- [Runbook activer HA Proxy](./RUNBOOKS/ENABLE-PROXY-HA.md)

- [Production Gate](./PRODUCTION-GATE.md)
- [Runbook déploiement production sécurisé](./RUNBOOKS/PRODUCTION-DEPLOYMENT-GATE.md)

- [Settings](./SETTINGS.md)

- [Normalisation universelle des listes](./LIST-NORMALIZATION.md)

- [Validation stricte des settings](./SETTINGS-VALIDATION.md)

- [Cycle de vie d'une zone](./ZONE-LIFECYCLE.md)
- [Runbook cycle de vie zone](./RUNBOOKS/ZONE-LIFECYCLE.md)

- [Gestion automatique du RNDC secret](./RNDC-SECRET.md)


---

Copyright
© IRIVEN Group — All Rights Reserved

- [RPZ — DNS Firewall](./SECURITY/RPZ.md)

- [Bibliothèque de validation](./VALIDATION-LIBRARY.md)
