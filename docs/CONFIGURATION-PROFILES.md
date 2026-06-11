ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

# Profiles de configuration

## Profiles supportés

```text
authoritative
proxy-forwarder
proxy-hybrid
```

## Règles de sécurité

### authoritative

```text
ROLE=dns-authoritative
PROXY_TYPE interdit
ENABLE_RPZ=no
pas de zones proxy locales
```

### proxy-forwarder

```text
ROLE=dns-proxy
PROXY_TYPE=forwarder
pas de zones master/locales sur le proxy
récursion/cache/forwarding/RPZ uniquement
```

### proxy-hybrid

```text
ROLE=dns-proxy
PROXY_TYPE=hybrid
récursion/cache/forwarding/RPZ
zones locales proxy autorisées
```

## Audit

```bash
dnsforge profile audit
```

Cet audit vérifie que les modèles `setup.conf` restent cohérents avec les règles ci-dessus.

---
Copyright
© IRIVEN Group — All Rights Reserved
