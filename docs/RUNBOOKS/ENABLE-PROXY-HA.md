ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](../index.md) | [Architecture](../ARCHITECTURE.md) | [Déploiement](../DEPLOYMENT.md) | [Exploitation](../OPERATIONS.md) | [Sécurité](../SECURITY.md) | [Troubleshooting](../TROUBLESHOOTING.md) | [Checklist](../PRODUCTION-CHECKLIST.md)

# Activer la HA DNS Proxy optionnelle

## 1. Confirmer le besoin

Le mode par défaut est DNS1/DNS2 sans VIP. Ne pas activer la VIP si ce mode suffit.

## 2. Modifier l'inventaire proxy

```bash
vi src/settings/dns-proxy/<node>.env
```

Définir :

```bash
ENABLE_PROXY_HA="yes"
PEER_PROXY_ADDRESSES="<VIP>/<CIDR>"
PEER_PROXY_ADDRESSES="<interface>"
PROXY_KEEPALIVED_STATE="MASTER"
PROXY_KEEPALIVED_PRIORITY="110"
PROXY_KEEPALIVED_VRID="61"
PROXY_KEEPALIVED_AUTH_PASS="<secret>"
PROXY_HA_HEALTHCHECK_ZONE="<zone>"
```

## 3. Rendre et valider

```bash
./src/dnsProxyDeploy.sh <node> --render-only
./tests/proxy-ha/check-proxy-ha-render.sh
```

## 4. Déployer

```bash
sudo ./src/dnsProxyDeploy.sh <node>
```

## 5. Vérifier

```bash
systemctl status keepalived --no-pager
ip addr show
/opt/binddns/proxy-ha/check-proxy-ha.sh
dig @<VIP> <ZONE> SOA
```

## 6. Rollback

```bash
systemctl disable --now keepalived
sed -i 's/^ENABLE_PROXY_HA=.*/ENABLE_PROXY_HA="no"/' src/settings/dns-proxy/<node>.env
sudo ./src/dnsProxyDeploy.sh <node>
```

---

[← Retour à l'index](../index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
