ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](./index.md) | [Architecture](./ARCHITECTURE.md) | [Déploiement](./DEPLOYMENT.md) | [Exploitation](./OPERATIONS.md) | [Sécurité](./SECURITY.md) | [Troubleshooting](./TROUBLESHOOTING.md) | [Checklist](./PRODUCTION-CHECKLIST.md)

# Sécurité


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

## 1. Vérifier l'absence de secrets par défaut

```bash
grep -R 'CHANGE_ME\|REPLACE_' src/settings
```

En production, cette commande ne doit rien retourner.

## 2. TSIG

TSIG protège les échanges DNS serveur-à-serveur : AXFR, IXFR, NOTIFY.

Générer une clé :

```bash
tsig-keygen -a hmac-sha256 xfr-shared-key
```

Extraire le secret et le reporter dans les inventaires concernés :

```bash
vi src/settings/dns-proxy/<node>.env
vi src/settings/dns-authoritative/<node>.env
```

Tester un AXFR avec TSIG :

```bash
dig @<AUTHORITATIVE_BACK_IP> <ZONE> AXFR -y <TSIG_KEY_NAME>:<TSIG_SECRET>
```

Tester qu'un AXFR sans TSIG est refusé :

```bash
dig @<AUTHORITATIVE_BACK_IP> <ZONE> AXFR
```

Résultat attendu : `Transfer failed` ou `REFUSED`.

## 3. RNDC

RNDC doit être limité à ADM.

Tester :

```bash
rndc -s <ADM_IP> status
```

Vérifier le port :

```bash
ss -lntup | grep ':953'
```

## 4. SELinux

État :

```bash
getenforce
```

Relabel :

```bash
restorecon -Rv /etc/named.conf /etc/named /var/named /var/log/named
```

Boolean utile :

```bash
getsebool named_write_master_zones
setsebool -P named_write_master_zones on
```

Audit SELinux :

```bash
ausearch -m avc -ts recent
```

## 5. Firewalld

État :

```bash
systemctl is-active firewalld
```

Règles :

```bash
firewall-cmd --list-services
firewall-cmd --list-ports
firewall-cmd --list-all
```

Appliquer manuellement si nécessaire :

```bash
firewall-cmd --permanent --add-service=dns
firewall-cmd --permanent --add-port=953/tcp
firewall-cmd --permanent --add-port=8053/tcp
firewall-cmd --reload
```

Côté authoritative avec VRRP :

```bash
firewall-cmd --permanent --add-protocol=vrrp
firewall-cmd --reload
```

## 6. Anti-abus DNS

Vérifier les options dans le rendu :

```bash
grep -RniE 'minimal-any|minimal-responses|rate-limit|recursion|allow-recursion|allow-query-cache' src/render
```

Contrôler en production :

```bash
named-checkconf -p /etc/named.conf | grep -E 'recursion|allow-recursion|rate-limit'
```

## 7. Exposition externe

Tester depuis un réseau non autorisé :

```bash
dig @<FRONT_IP> www.redhat.com A +time=2 +tries=1
dig @<FRONT_IP> <ZONE_INTERNE> SOA +time=2 +tries=1
```

Le serveur ne doit pas exposer de zones internes non prévues.


    ---

    [← Retour à l'index](./index.md)

---

[← Retour à l'index](./index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved


## RPZ — DNS Firewall

Voir [RPZ — DNS Firewall](./SECURITY/RPZ.md).
