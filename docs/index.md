ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

# Documentation

Bienvenue dans la documentation de **ZoneForge DNSaaS**.

Cette documentation est orientée **déploiement** et **exploitation** de la solution. Le README reste volontairement limité à la présentation produit.

---

## Présentation

- [Architecture](./ARCHITECTURE.md)
- [Concepts et positionnement](./CONCEPTS.md)
- [Image d'architecture](./images/zoneforge-dnsaas-architecture.png)

---

## Déploiement

- [Déploiement](./DEPLOYMENT.md)
- [Settings](./SETTINGS.md)
- [Validation stricte des settings](./SETTINGS-VALIDATION.md)
- [Production Gate](./PRODUCTION-GATE.md)
- [HA DNS Proxy optionnelle](./PROXY-HA-OPTIONAL.md)
- [Multi-VIP authoritative](./MULTI-AUTHORITATIVE-VIP.md)
- [Routing par zone vers clusters authoritative](./ZONE-CLUSTER-ROUTING.md)

---

## Exploitation

- [Opérations](./OPERATIONS.md)
- [Gestion des Zones](./GESTION-DES-ZONES.md)
- [Catalogue central des zones](./ZONE-CATALOG.md)
- [Monitoring natif](./NATIVE-MONITORING.md)
- [Gestion automatique du RNDC secret](./RNDC-SECRET.md)
- [Production Checklist](./PRODUCTION-CHECKLIST.md)
- [Runbook — Déploiement production sécurisé](./RUNBOOKS/PRODUCTION-DEPLOYMENT-GATE.md)
- [Runbook — Gestion des Zones](./RUNBOOKS/GESTION-DES-ZONES.md)
- [Runbook — Healthcheck monitoring](./RUNBOOKS/MONITORING-HEALTHCHECK.md)
- [Runbook — DNSSEC zone publique](./RUNBOOKS/DNSSEC-PUBLIC-ZONE.md)
- [Runbook — HA Proxy optionnelle](./RUNBOOKS/ENABLE-PROXY-HA.md)

---

## Sécurité

- [Sécurité](./SECURITY.md)
- [RPZ — DNS Firewall](./SECURITY/RPZ.md)
- [DNSSEC Enterprise](./DNSSEC-ENTERPRISE.md)
- [ACL par vue et par zone](./ZONE-ACL.md)
- [Bibliothèque de validation](./VALIDATION-LIBRARY.md)
- [Normalisation universelle des listes](./LIST-NORMALIZATION.md)

---

## Référence

- [Troubleshooting](./TROUBLESHOOTING.md)
- [Changelog projet](../CHANGELOG.md)



---

Copyright
© IRIVEN Group — All Rights Reserved


- [Migration Python progressive](./PYTHON-MIGRATION.md)

- [Rendu Python natif](./PYTHON-RENDERING.md)

- [Gestion des Zones Python native](./PYTHON-ZONE-MANAGER.md)

- [Plan d’initialisation Python](./PYTHON-INITIALIZE-PLAN.md)

- [Initialisation Python native](./PYTHON-INITIALIZE-NATIVE.md)

- [Produit Python v9.0](./PYTHON-PRODUCT-V9.md)

- [Guide d'exploitation](./OPERATING-GUIDE.md)

- [Contexte Build DDD](./DDD-BUILD-CONTEXT.md)

- [Installation système](./INSTALLATION.md)

- [Modèles setup.conf](./SETUP-CONF-TEMPLATES.md)

- [Profiles de configuration](./CONFIGURATION-PROFILES.md)

- [Gestion des enregistrements DNS](./ZONE-RECORDS.md)

- [Cluster](./CLUSTER.md)

- [Source de configuration](./CONFIGURATION-SOURCE.md)
