ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](./index.md) | [Architecture](./ARCHITECTURE.md) | [Déploiement](./DEPLOYMENT.md) | [Exploitation](./OPERATIONS.md) | [Sécurité](./SECURITY.md) | [Troubleshooting](./TROUBLESHOOTING.md) | [Checklist](./PRODUCTION-CHECKLIST.md)

# Exploitation quotidienne


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

## 1. État du service

```bash
systemctl status named --no-pager
systemctl is-active named
systemctl is-enabled named
```

Voir les derniers événements :

```bash
journalctl -u named -n 100 --no-pager
```

Suivi temps réel :

```bash
journalctl -u named -f
```

## 2. Contrôles RNDC

Statut :

```bash
rndc status
```

Recharger la configuration après ajout ou suppression de zone :

```bash
rndc reconfig
```

Recharger toutes les zones :

```bash
rndc reload
```

Recharger une zone précise :

```bash
rndc reload <ZONE> IN <VIEW>
```

Exemple :

```bash
rndc reload example.net IN external
```

Vider le cache :

```bash
rndc flush
```

Vider le cache d'un nom précis :

```bash
rndc flushname www.example.net
```

Générer les statistiques :

```bash
rndc stats
cat /var/named/data/named_stats.txt
```

## 3. Validation configuration

Avant toute mise en production :

```bash
named-checkconf -z /etc/named.conf
```

Vérifier une zone master :

```bash
named-checkzone <ZONE> /var/named/master/<view>/<ZONE>.zone
```

Exemple :

```bash
named-checkzone example.net /var/named/master/external/example.net.zone
```

## 4. Logs utiles

Logs BIND dédiés :

```bash
tail -f /var/log/named/default.log
tail -f /var/log/named/security.log
tail -f /var/log/named/transfer.log
tail -f /var/log/named/resolver.log
```

Logs systemd :

```bash
journalctl -u named -f
```

Chercher les erreurs :

```bash
grep -RniE 'error|failed|denied|refused|servfail|tsig|transfer' /var/log/named /var/log/messages 2>/dev/null
```

## 5. Tests DNS usuels

SOA :

```bash
dig @<DNS_IP> <ZONE> SOA +norecurse
```

NS :

```bash
dig @<DNS_IP> <ZONE> NS +norecurse
```

A record :

```bash
dig @<DNS_IP> <HOSTNAME> A
```

Reverse :

```bash
dig @<DNS_IP> -x <IP_ADDRESS>
```

Trace :

```bash
dig +trace <ZONE>
```

DNSSEC :

```bash
dig @<DNS_IP> <ZONE> SOA +dnssec
```

## 6. Vérifier les sockets d'écoute

```bash
ss -lntup | grep ':53'
ss -lnuap | grep ':53'
ss -lntup | grep ':953'
ss -lntup | grep ':8053'
```

## 7. Sauvegarde rapide

```bash
mkdir -p /var/backups/binddns/manual-$(date +%Y%m%d-%H%M%S)

cp -a /etc/named.conf /etc/named /var/named /var/backups/binddns/manual-$(date +%Y%m%d-%H%M%S)/
```

## 8. Mise à jour contrôlée

```bash
dnf check-update bind bind-utils
dnf update -y bind bind-utils
named-checkconf -z /etc/named.conf
systemctl restart named
rndc status
```

## 9. Checklist quotidienne

```bash
systemctl is-active named
rndc status
named-checkconf -z /etc/named.conf
journalctl -u named --since today --no-pager | grep -iE 'error|failed|denied|servfail' || true
```


    ---

    [← Retour à l'index](./index.md)

---

[← Retour à l'index](./index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
