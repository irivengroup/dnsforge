ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

# RPZ — DNS Firewall

## Position d’architecture

ZoneForge DNSaaS applique les RPZ uniquement sur les services récursifs.

```text
dns-proxy         : RPZ autorisé
dns-recursive     : RPZ autorisé
dns-authoritative : RPZ interdit
```

## Raison

Une RPZ modifie ou réécrit les réponses DNS selon une politique locale. Ce comportement est adapté au filtrage récursif, mais pas à un serveur autoritatif.

Un serveur autoritatif doit répondre avec les données de référence exactes de ses zones.

## Règle ZoneForge

Sur un nœud authoritative, la configuration suivante est interdite :

```bash
ROLE="dns-authoritative"
ENABLE_RPZ="yes"
```

La validation stricte bloque ce cas avec l’erreur :

```text
RPZ is not supported on authoritative servers
```

## Où activer RPZ

RPZ doit être activé côté proxy/récursif :

```bash
ROLE="dns-proxy"
ENABLE_RPZ="yes"
RPZ_ZONE_NAME="rpz.local"
```

## Tests

```bash
./tests/security/check-rpz-authoritative-forbidden.sh
./tests/security/check-rpz-authoritative-render-clean.sh
```



---

Copyright
© IRIVEN Group — All Rights Reserved

