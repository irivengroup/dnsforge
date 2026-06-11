ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

# Bibliothèque de validation

## Décision d'architecture

Depuis la v7.2, ZoneForge DNSaaS utilise un point d'entrée unique pour la validation :

```text

```

L'ancienne bibliothèque de validation séparée a été supprimée afin d'éviter les doublons.

## Rôle

`lib-settings-validate.sh` porte désormais les validations strictes DNS Proxy, DNS Authoritative, RPZ, DNSSEC, HA Proxy optionnelle et les wrappers de compatibilité.

## Validation

```bash
./tests/settings/check-validation-library-consolidation.sh
./tests/settings/check-settings-strict-validation.sh
./tests/settings/check-settings-strict-negative.sh
```



---

Copyright
© IRIVEN Group — All Rights Reserved

