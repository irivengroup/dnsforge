ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](./index.md) | [Architecture](./ARCHITECTURE.md) | [Déploiement](./DEPLOYMENT.md) | [Exploitation](./OPERATIONS.md) | [Sécurité](./SECURITY.md) | [Troubleshooting](./TROUBLESHOOTING.md) | [Checklist](./PRODUCTION-CHECKLIST.md)

# HA DNS Proxy optionnelle

## Position d'architecture

Le mode par défaut reste inchangé :

```text
DNS1 = proxy A
DNS2 = proxy B
pas de VIP
pas de keepalived
```

La v5.8 ajoute uniquement un mode optionnel avec VIP proxy, activable explicitement.

## Variables

```bash
ENABLE_PROXY_HA="no"
PEER_PROXY_ADDRESSES=""
PEER_PROXY_ADDRESSES=""
PROXY_KEEPALIVED_STATE="BACKUP"
PROXY_KEEPALIVED_PRIORITY="100"
PROXY_KEEPALIVED_VRID="61"
PROXY_KEEPALIVED_AUTH_PASS=""
PROXY_HA_HEALTHCHECK_ZONE="."
```

## Activer le mode VIP

```bash
ENABLE_PROXY_HA="yes"
PEER_PROXY_ADDRESSES="192.0.2.250/24"
PEER_PROXY_ADDRESSES="eth0"
PROXY_KEEPALIVED_STATE="MASTER"
PROXY_KEEPALIVED_PRIORITY="110"
PROXY_KEEPALIVED_VRID="61"
PROXY_KEEPALIVED_AUTH_PASS="<secret>"
PROXY_HA_HEALTHCHECK_ZONE="split-example.invalid"
```

## Artefacts générés

```text
/opt/binddns/proxy-ha/check-proxy-ha.sh
/etc/keepalived/keepalived-proxy.conf
```

## Healthcheck Keepalived

Le script vérifie :

```text
- named actif ;
- rndc status ;
- requête SOA sur la zone de healthcheck.
```

## Tests

```bash
./tests/proxy-ha/check-proxy-ha-design.sh
./tests/proxy-ha/check-proxy-ha-optional-default.sh
./tests/proxy-ha/check-proxy-ha-syntax.sh
./tests/proxy-ha/check-proxy-ha-render.sh
```

## Recommandation

Utiliser le mode VIP proxy uniquement si une contrainte d'architecture impose une IP unique côté clients. Sinon conserver DNS1/DNS2.

---

[← Retour à l'index](./index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
