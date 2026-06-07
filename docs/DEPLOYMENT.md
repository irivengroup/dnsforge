ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](./index.md) | [Architecture](./ARCHITECTURE.md) | [Déploiement](./DEPLOYMENT.md) | [Exploitation](./OPERATIONS.md) | [Sécurité](./SECURITY.md) | [Troubleshooting](./TROUBLESHOOTING.md) | [Checklist](./PRODUCTION-CHECKLIST.md)

# Déploiement


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

## 1. Préparer les inventaires

Lister les inventaires disponibles :

```bash
find src/settings -type f -name '*.env' -print
```

Éditer un inventaire proxy :

```bash
vi src/settings/dns-proxy/srv02.env
```

Éditer un inventaire authoritative :

```bash
vi src/settings/dns-authoritative/svr01a.env
```

Vérifier qu'aucun secret par défaut ne reste en place :

```bash
grep -R 'CHANGE_ME\|REPLACE_' src/settings
```

La commande ne doit retourner aucune valeur en production.

## 2. Déploiement DNS Proxy

Rendu seul :

```bash
./src/dnsProxyDeploy.sh srv02 --render-only
```

Contrôler le rendu généré :

```bash
find src/render/dns-proxy/srv02 -type f | sort
```

Vérifier le fichier principal rendu :

```bash
sed -n '1,160p' src/render/dns-proxy/srv02/etc/named.conf
```

Dry-run complet :

```bash
./src/dnsProxyDeploy.sh srv02 --dry-run
```

Validation seule :

```bash
./src/dnsProxyDeploy.sh srv02 --validate-only
```

Déploiement complet avec installation BIND si nécessaire :

```bash
sudo ./src/dnsProxyDeploy.sh srv02
```

Déploiement sans installation de paquets :

```bash
sudo ./src/dnsProxyDeploy.sh srv02 --skip-install
```

## 3. Déploiement DNS Authoritative

Rendu seul :

```bash
./src/dnsAuthoritativeDeploy.sh svr01a --render-only
```

Contrôler le rendu :

```bash
find src/render/dns-authoritative/svr01a -type f | sort
```

Dry-run :

```bash
./src/dnsAuthoritativeDeploy.sh svr01a --dry-run
```

Déploiement complet :

```bash
sudo ./src/dnsAuthoritativeDeploy.sh svr01a
```

Sans installation de paquets :

```bash
sudo ./src/dnsAuthoritativeDeploy.sh svr01a --skip-install
```

## 4. Vérifications post-déploiement

Service BIND :

```bash
systemctl status named --no-pager
systemctl is-enabled named
```

Configuration BIND :

```bash
named-checkconf -z /etc/named.conf
```

RNDC :

```bash
rndc status
rndc reconfig
```

Logs :

```bash
journalctl -u named -n 100 --no-pager
tail -n 100 /var/log/named/default.log
tail -n 100 /var/log/named/security.log
```

## 5. Vérification DNS Proxy

Tester l'écoute FRONT :

```bash
dig @<FRONT_IP> <ZONE_PUBLIQUE> SOA +time=2 +tries=1
```

Tester l'écoute BACK :

```bash
dig @<BACK_IP> <ZONE_INTERNE> SOA +time=2 +tries=1
```

Tester le forwarding via BACK :

```bash
dig @<BACK_IP> www.redhat.com A +time=3 +tries=1
```

Vérifier qu'un client non autorisé n'accède pas à la récursion :

```bash
dig @<FRONT_IP> www.redhat.com A +time=2 +tries=1
```

Le comportement attendu dépend de la politique FRONT : réponse locale ou forwarding contrôlé, mais jamais récursion ouverte non maîtrisée.

## 6. Vérification DNS Authoritative

Tester le service sur BACK :

```bash
dig @<BACK_IP> <ZONE> SOA +time=2 +tries=1
```

Tester la VIP :

```bash
dig @<VIP_BACK_IP> <ZONE> SOA +time=2 +tries=1
```

Vérifier Keepalived :

```bash
systemctl status keepalived --no-pager
ip addr show
journalctl -u keepalived -n 100 --no-pager
```

## 7. Rollback

Lister les sauvegardes :

```bash
ls -ltr /var/backups/binddns/
```

Restaurer manuellement la dernière sauvegarde :

```bash
BACKUP_DIR="$(ls -td /var/backups/binddns/* | head -1)"

cp -a "${BACKUP_DIR}/named.conf" /etc/named.conf
cp -a "${BACKUP_DIR}/named" /etc/
cp -a "${BACKUP_DIR}/named" /var/ 2>/dev/null || true

restorecon -Rv /etc/named.conf /etc/named /var/named /var/log/named

named-checkconf -z /etc/named.conf
systemctl restart named
rndc status
```

## 8. Critères d'acceptation

```bash
named-checkconf -z /etc/named.conf
systemctl is-active named
rndc status
dig @<DNS_IP> <ZONE> SOA
```

Tous les contrôles doivent être OK avant clôture du changement.


    ---

    [← Retour à l'index](./index.md)

## Industrialisation des zones

```bash
./src/dnsAuthoritativeDeploy.sh <node> --render-only
./src/dnsProxyDeploy.sh <node> --render-only
./tests/dns-validation/check-zone-sources.sh
./tests/dns-validation/check-zone-indexes.sh
```

---

[← Retour à l'index](./index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
