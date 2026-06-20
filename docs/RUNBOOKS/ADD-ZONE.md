ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](../index.md) | [Architecture](../ARCHITECTURE.md) | [Déploiement](../DEPLOYMENT.md) | [Exploitation](../OPERATIONS.md) | [Sécurité](../SECURITY.md) | [Troubleshooting](../TROUBLESHOOTING.md) | [Checklist](../PRODUCTION-CHECKLIST.md)

# Ajouter une zone

## Cas 1 — Ajouter une zone globale authoritative

```bash
vi native BIND view directories managed by DNSForgeexternal/master/example.net.conf
vi native BIND view directories managed by DNSForgeexternal/master/example.net.zone

./src/dnsAuthoritativeDeploy.sh <node> --render-only
sudo ./src/dnsAuthoritativeDeploy.sh <node>
```

Ajouter la zone secondary côté proxy :

```bash
vi native BIND view directories managed by DNSForgeexternal/secondary/example.net.conf

./src/dnsProxyDeploy.sh <node> --render-only
sudo ./src/dnsProxyDeploy.sh <node>
```

Tester :

```bash
dig @<PEER_AUTHORITATIVE_ADDRESSES> example.net SOA
dig @<BIND_EXTRANET_IP> example.net SOA
```

## Cas 2 — Ajouter une zone master locale sur proxy

```bash
vi native BIND view directories managed by DNSForgeexternal/master/example-edge-public.conf
vi native BIND view directories managed by DNSForgeexternal/master/example-edge-public.invalid.zone

./src/dnsProxyDeploy.sh <node> --render-only

cat src/render/dns-proxy/<node>/etc/named/views/external/master/zones.index.conf
ls -l src/render/dns-proxy/<node>/var/named/master/external/

./tests/dns-validation/check-proxy-master-zones.sh
./tests/dns-validation/check-zone-sources.sh

sudo ./src/dnsProxyDeploy.sh <node>

dig @<BIND_EXTRANET_IP> example-edge-public.invalid SOA
```

## Cas 3 — Ajouter une zone master interne sur proxy

```bash
vi native BIND view directories managed by DNSForgeinternal/master/example-edge-internal.conf
vi native BIND view directories managed by DNSForgeinternal/master/example-edge-internal.invalid.zone

./src/dnsProxyDeploy.sh <node> --render-only
sudo ./src/dnsProxyDeploy.sh <node>

dig @<BIND_INTRANET_IP> example-edge-internal.invalid SOA
```

---

[← Retour à l'index](../index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
