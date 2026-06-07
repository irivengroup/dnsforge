ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](./index.md) | [Architecture](./ARCHITECTURE.md) | [Déploiement](./DEPLOYMENT.md) | [Exploitation](./OPERATIONS.md) | [Sécurité](./SECURITY.md) | [Troubleshooting](./TROUBLESHOOTING.md) | [Checklist](./PRODUCTION-CHECKLIST.md)

# Rôle DNS Proxy

## Objectif

Le rôle DNS Proxy n'est pas uniquement un forwarder ou un secondary DNS. Il peut aussi être autoritaire pour certaines zones locales.

Un proxy peut porter :

```text
- zones master locales ;
- zones secondary reçues depuis l'autoritaire global ;
- zones forward ;
- zones reverse ;
- RPZ ;
- récursion contrôlée selon la vue.
```

## Arborescence des zones proxy

```text
src/build/dns-proxy/zones/
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

## Ajouter une zone master externe locale

```bash
vi src/build/dns-proxy/zones/external/master/example-edge-public.conf
vi src/build/dns-proxy/zones/external/master/example-edge-public.invalid.zone

./src/dnsProxyDeploy.sh <node> --render-only

cat src/render/dns-proxy/<node>/etc/named/views/external/master/zones.index.conf
ls -l src/render/dns-proxy/<node>/var/named/master/external/

sudo ./src/dnsProxyDeploy.sh <node>

dig @<PROXY_FRONT_IP> example-edge-public.invalid SOA
```

## Ajouter une zone master interne locale

```bash
vi src/build/dns-proxy/zones/internal/master/example-edge-internal.conf
vi src/build/dns-proxy/zones/internal/master/example-edge-internal.invalid.zone

./src/dnsProxyDeploy.sh <node> --render-only
sudo ./src/dnsProxyDeploy.sh <node>

dig @<PROXY_BACK_IP> example-edge-internal.invalid SOA
```

## Règles de sécurité

Les zones master locales côté proxy doivent désactiver transfert et update dynamique :

```bind
allow-transfer {
        none;
};

allow-update {
        none;
};
```

## AUTHORITATIVE_BACK_IP multi-VIP

Un DNS Proxy peut forwarder vers plusieurs clusters authoritative :

```bash
AUTHORITATIVE_BACK_IP=("192.0.2.10" "192.0.2.20")
```

Rendu attendu :

```bash
./src/dnsProxyDeploy.sh <node> --render-only

grep -Rni 'forwarders\|primaries\|allow-notify' src/render/dns-proxy/<node>/etc/named
```

---

[← Retour à l'index](./index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
