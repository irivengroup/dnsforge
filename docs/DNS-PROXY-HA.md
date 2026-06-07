ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](./index.md) | [Architecture](./ARCHITECTURE.md) | [Déploiement](./DEPLOYMENT.md) | [Exploitation](./OPERATIONS.md) | [Sécurité](./SECURITY.md) | [Troubleshooting](./TROUBLESHOOTING.md) | [Checklist](./PRODUCTION-CHECKLIST.md)

# Haute disponibilité DNS Proxy sans VIP

## Objectif

Les DNS Proxy fonctionnent en haute disponibilité native DNS, sans VIP, sans VRRP et sans Keepalived.

Le principe est de configurer les consommateurs avec deux serveurs DNS distincts :

```text
DNS1 = proxy node A
DNS2 = proxy node B
```

Cette approche est simple, robuste et adaptée au protocole DNS, car les clients et systèmes d'exploitation savent généralement interroger un second serveur DNS si le premier ne répond pas.

## Pourquoi pas de VIP côté proxy

Le rôle proxy reçoit les requêtes clientes. Une VIP peut ajouter de la complexité inutile :

```text
- dépendance VRRP ;
- risque de split-brain réseau ;
- perte de visibilité sur le nœud réellement utilisé ;
- bascule parfois moins prévisible que DNS1/DNS2 côté client.
```

La conception retenue est donc :

```text
dns-proxy:
  - pas de VIP ;
  - pas de Keepalived ;
  - pas de VRRP ;
  - deux IPs DNS fournies aux clients.
```

## Vérifier la conception

```bash
./tests/proxy-ha/check-proxy-ha-design.sh
```

Le test échoue si des références VIP, VRRP ou Keepalived apparaissent dans le rôle `dns-proxy`.

## Inventaires proxy

Lister les nœuds proxy :

```bash
find src/settings/dns-proxy -maxdepth 1 -type f -name '*.env' -print
```

Il faut au moins deux inventaires proxy pour le mode DNS1/DNS2.

## Tests de rendu

```bash
./src/dnsProxyDeploy.sh <proxy-node-a> --render-only
./src/dnsProxyDeploy.sh <proxy-node-b> --render-only
./tests/render/check-render-settings.sh
```

## Tests de service

Après déploiement :

```bash
dig @<DNS1_IP> <ZONE> SOA +time=2 +tries=1
dig @<DNS2_IP> <ZONE> SOA +time=2 +tries=1
```

ou avec le test fourni :

```bash
DNS1=<DNS1_IP> DNS2=<DNS2_IP> TEST_ZONE=<ZONE> ./tests/proxy-ha/check-proxy-pair-smoke.sh
```

## Test de bascule

1. Tester DNS1 et DNS2 :

```bash
dig @<DNS1_IP> <ZONE> SOA
dig @<DNS2_IP> <ZONE> SOA
```

2. Arrêter temporairement BIND sur DNS1 :

```bash
sudo systemctl stop named
```

3. Vérifier que DNS2 répond :

```bash
dig @<DNS2_IP> <ZONE> SOA
```

4. Remettre DNS1 :

```bash
sudo systemctl start named
rndc status
```

## Configuration côté clients

Exemple Linux NetworkManager :

```bash
nmcli con mod "<CONNECTION_NAME>" ipv4.dns "<DNS1_IP> <DNS2_IP>"
nmcli con up "<CONNECTION_NAME>"
```

Exemple `/etc/resolv.conf` géré manuellement :

```text
nameserver <DNS1_IP>
nameserver <DNS2_IP>
options timeout:2 attempts:2 rotate
```

Exemple DHCP :

```text
option domain-name-servers <DNS1_IP>, <DNS2_IP>;
```

## Supervision

Surveiller séparément les deux proxys :

```bash
curl http://<DNS1_ADM_IP>:8053/json/v1/server
curl http://<DNS2_ADM_IP>:8053/json/v1/server
```

Tester les métriques exporter :

```bash
curl http://<DNS1_ADM_IP>:9119/metrics
curl http://<DNS2_ADM_IP>:9119/metrics
```

## Critères d'acceptation

```text
[ ] Deux inventaires dns-proxy existent
[ ] Aucun VIP/VRRP/Keepalived côté proxy
[ ] Les deux proxys rendent une configuration valide
[ ] DNS1 répond aux zones attendues
[ ] DNS2 répond aux zones attendues
[ ] L'arrêt de DNS1 ne bloque pas la résolution via DNS2
[ ] La supervision voit les deux proxys séparément
```

---

[← Retour à l'index](./index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
