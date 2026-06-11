ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](./index.md) | [Architecture](./ARCHITECTURE.md) | [Déploiement](./DEPLOYMENT.md) | [Exploitation](./OPERATIONS.md) | [Sécurité](./SECURITY.md) | [Troubleshooting](./TROUBLESHOOTING.md) | [Checklist](./PRODUCTION-CHECKLIST.md)

# Industrialisation des zones

## Objectif

La v3.9.1 industrialise aussi les zones `master` locales côté DNS Proxy.

## DNS Proxy

```text
src/dnsforge/infrastructure/build/dns-proxy/zones/
├── external/
│   ├── master/
│   ├── secondary/
│   └── forward/
├── internal/
│   ├── master/
│   ├── secondary/
│   ├── forward/
│   └── reverse/
└── rpz/
```

## DNS Authoritative

```text
src/dnsforge/infrastructure/build/dns-authoritative/zones/
├── external/
│   └── master/
├── internal/
│   └── master/
└── reverse/
    └── master/
```

## Génération proxy

```bash
./src/dnsProxyDeploy.sh <node> --render-only

find src/render/dns-proxy/<node> -name 'zones.index.conf' -print -exec cat {} \;
```

Les index suivants doivent exister :

```text
/etc/named/views/external/master/zones.index.conf
/etc/named/views/external/secondary/zones.index.conf
/etc/named/views/external/forward/zones.index.conf
/etc/named/views/internal/master/zones.index.conf
/etc/named/views/internal/secondary/zones.index.conf
/etc/named/views/internal/forward/zones.index.conf
/etc/named/views/internal/reverse/zones.index.conf
```

## Validation

```bash
./tests/dns-validation/check-zone-sources.sh
./tests/dns-validation/check-zone-indexes.sh
./tests/dns-validation/check-proxy-master-zones.sh
```

---

[← Retour à l'index](./index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
