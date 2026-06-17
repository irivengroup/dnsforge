ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](./index.md) | [Architecture](./ARCHITECTURE.md) | [Déploiement](./DEPLOYMENT.md) | [Exploitation](./OPERATIONS.md) | [Sécurité](./SECURITY.md) | [Troubleshooting](./TROUBLESHOOTING.md) | [Checklist](./PRODUCTION-CHECKLIST.md)

# Architecture


Les exemples ci-dessous utilisent des noms de nœuds d'inventaire à titre d'exemple. Le code projet ne doit pas dépendre de ces noms : les scripts chargent toujours les valeurs depuis `src/settings/`.

Avant toute opération, se placer à la racine du projet :

```bash
cd /opt/binddns-enterprise
```

Vérifier l'arborescence :

```bash
tree -L 3
```

Vérifier les scripts :

```bash
ls -l src/dnsProxyDeploy.sh src/dnsAuthoritativeDeploy.sh
```

## 1. Vue d'ensemble

L'architecture sépare deux responsabilités :

```text
Clients / Cloud / Réseaux consommateurs
        |
        | DNS
        v
DNS Proxy 1 + DNS Proxy 2
        |
        | BACK uniquement
        v
DNS Authoritative 1 + DNS Authoritative 2 + VIP BACK
```

## 2. DNS Proxy

Les nœuds proxy :

- reçoivent les requêtes clientes ;
- répondent pour les zones secondaires qu'ils portent ;
- forwardent vers l'autoritaire global via BACK ;
- ne possèdent pas de VIP entre eux ;
- sont consommés directement en DNS1/DNS2 côté client.

Commandes de vérification sur un proxy :

```bash
ip addr show
ss -lntup | grep ':53'
named-checkconf -z /etc/named.conf
rndc status
```

## 3. DNS Authoritative

Les nœuds authoritative :

- portent les zones master ;
- exposent une VIP BACK via Keepalived ;
- ne doivent pas recevoir de requêtes directes depuis l'extérieur ;
- autorisent les transferts uniquement avec TSIG ;
- servent de source de vérité aux proxys.

Commandes de vérification :

```bash
ip addr show
systemctl status keepalived --no-pager
systemctl status named --no-pager
dig @<VIP_BACK_IP> <ZONE> SOA
```

## 4. Flux réseau

DNS clients vers proxy :

```bash
dig @<PROXY_FRONT_IP> <ZONE> SOA
```

Proxy vers authoritative via BACK :

```bash
dig @<PEER_AUTHORITATIVE_ADDRESSES> <ZONE> SOA
```

Transfert de zone depuis proxy :

```bash
dig @<PEER_AUTHORITATIVE_ADDRESSES> <ZONE> AXFR -y <KEY_NAME>:<SECRET>
```

## 5. Interfaces

- FRONT : réception des requêtes clientes.
- BACK : forwarding, transferts, échanges inter-DNS.
- ADM : RNDC, SSH, statistics-channel.

Vérifier les interfaces :

```bash
ip -brief addr
ip route
```

## 6. Ports

```bash
ss -lntup | grep -E ':53|:953|:8053'
```

Ports attendus :

- 53/tcp et 53/udp : DNS.
- 953/tcp : RNDC.
- 8053/tcp : statistics-channel.
- protocole VRRP : uniquement côté authoritative si Keepalived actif.

## 7. Règle d'or

Aucune résolution directe de l'extérieur vers les nœuds authoritative. Tout flux client doit passer par les DNS proxy.


    ---

    [← Retour à l'index](./index.md)

## HA DNS Proxy sans VIP

Les nœuds DNS Proxy ne partagent pas de VIP. Les clients utilisent deux serveurs DNS :

```text
DNS1 = proxy node A
DNS2 = proxy node B
```

Validation :

```bash
./tests/proxy-ha/check-proxy-ha-design.sh
DNS1=<DNS1_IP> DNS2=<DNS2_IP> TEST_ZONE=<ZONE> ./tests/proxy-ha/check-proxy-pair-smoke.sh
```

---

[← Retour à l'index](./index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
