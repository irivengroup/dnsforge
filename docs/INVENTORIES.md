ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](./index.md) | [Architecture](./ARCHITECTURE.md) | [Déploiement](./DEPLOYMENT.md) | [Exploitation](./OPERATIONS.md) | [Sécurité](./SECURITY.md) | [Troubleshooting](./TROUBLESHOOTING.md) | [Checklist](./PRODUCTION-CHECKLIST.md)

# Inventaires

## Objectif

Les inventaires décrivent les paramètres propres à chaque nœud.

La v5.0 aligne les inventaires avec le code actuel et ajoute la prise en charge de plusieurs clusters authoritative via plusieurs VIPs.

## DNS Proxy

Chemin :

```text
src/settings/dns-proxy/<node>.env
```

Variables principales :

```bash
ROLE="dns-proxy"
NODE_NAME="<node>"

FRONT_IP="<front-ip>"
BACK_IP="<back-ip>"
ADM_IP="<adm-ip>"

AUTHORITATIVE_BACK_IP=("192.0.2.10" "192.0.2.20")

FRONT_ALLOWED_CLIENTS="any"
BACK_RECURSIVE_CLIENTS="10.0.0.0/8; 172.16.0.0/12; 192.168.0.0/16; localhost; localnets;"
ADM_ALLOWED_CLIENTS="<adm-cidr>"

DNS_FORWARD_POLICY="first"

TSIG_KEY_NAME="xfr-shared-key"
TSIG_SECRET="<secret>"

RNDC_KEY_NAME="rndc-key"
RNDC_SECRET="<secret>"
```

## AUTHORITATIVE_BACK_IP multi-VIP

`AUTHORITATIVE_BACK_IP` accepte désormais une liste :

```bash
AUTHORITATIVE_BACK_IP=("192.0.2.10" "192.0.2.20")
```

Chaque entrée représente une VIP ou IP BACK d'un cluster authoritative.

Le rendu génère automatiquement :

```bind
forwarders {{
        192.0.2.10;
        192.0.2.20;
}};
```

Pour les zones secondary :

```bind
primaries {{
        192.0.2.10 key "xfr-shared-key";
        192.0.2.20 key "xfr-shared-key";
}};
```

Et :

```bind
allow-notify {{
        192.0.2.10;
        192.0.2.20;
}};
```

## DNS Authoritative

Chemin :

```text
src/settings/dns-authoritative/<node>.env
```

Variables principales :

```bash
ROLE="dns-authoritative"
NODE_NAME="<node>"

BACK_IP="<back-ip>"
ADM_IP="<adm-ip>"
VIP_BACK_IP="<vip-back-ip>"
PEER_BACK_IP="<peer-back-ip>"

PROXY_TRANSFER_CLIENTS="<proxy-back-ip-1>; <proxy-back-ip-2>;"
ADM_ALLOWED_CLIENTS="<adm-cidr>"
```

## Validation

```bash
./tests/settings/check-settings-variables.sh
./tests/settings/check-authoritative-back-ip-list.sh
```

---

[← Retour à l'index](./index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
