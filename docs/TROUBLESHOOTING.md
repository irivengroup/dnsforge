ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](./index.md) | [Architecture](./ARCHITECTURE.md) | [Déploiement](./DEPLOYMENT.md) | [Exploitation](./OPERATIONS.md) | [Sécurité](./SECURITY.md) | [Troubleshooting](./TROUBLESHOOTING.md) | [Checklist](./PRODUCTION-CHECKLIST.md)

# Troubleshooting


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

## 1. REFUSED

Diagnostic :

```bash
dig @<DNS_IP> <ZONE> SOA +time=2 +tries=1
journalctl -u named -n 100 --no-pager
grep -Rni refused /var/log/named /var/log/messages 2>/dev/null
```

Causes fréquentes :

- mauvaise vue BIND ;
- ACL incorrecte ;
- interface cible incorrecte ;
- recursion interdite.

Correction :

```bash
named-checkconf -p /etc/named.conf | less
rndc reconfig
```

## 2. SERVFAIL

Diagnostic :

```bash
dig @<DNS_IP> <NAME> A +cdflag
dig @<DNS_IP> <NAME> A +dnssec
journalctl -u named -n 200 --no-pager
```

Causes fréquentes :

- DNSSEC invalide ;
- forwarder indisponible ;
- zone mal chargée ;
- erreur de syntaxe.

Correction :

```bash
named-checkconf -z /etc/named.conf
rndc flush
rndc reconfig
```

## 3. NXDOMAIN inattendu

Diagnostic :

```bash
dig @<DNS_IP> <NAME> A +norecurse
dig @<DNS_IP> <ZONE> SOA
grep -Rni '<NAME>' /var/named /etc/named 2>/dev/null
```

Correction :

```bash
named-checkzone <ZONE> /var/named/master/<view>/<ZONE>.zone
rndc reload <ZONE>
```

## 4. Échec AXFR/IXFR

Diagnostic :

```bash
dig @<AUTHORITATIVE_BACK_IP> <ZONE> AXFR
dig @<AUTHORITATIVE_BACK_IP> <ZONE> AXFR -y <TSIG_KEY_NAME>:<TSIG_SECRET>
grep -RniE 'transfer|xfr|tsig|denied' /var/log/named /var/log/messages 2>/dev/null
```

Causes :

- clé TSIG différente ;
- ACL transfer incorrecte ;
- firewall ;
- mauvaise IP source.

Correction :

```bash
grep -Rni 'allow-transfer\|primaries\|masters\|key' /etc/named
rndc reconfig
```

## 5. RNDC ne répond pas

Diagnostic :

```bash
rndc status
ss -lntup | grep ':953'
grep -Rni 'controls\|rndc' /etc/named
```

Correction :

```bash
restorecon -Rv /etc/named.conf /etc/named
systemctl restart named
rndc status
```

## 6. Keepalived / VIP absente

Diagnostic :

```bash
systemctl status keepalived --no-pager
journalctl -u keepalived -n 100 --no-pager
ip addr show
firewall-cmd --list-all 2>/dev/null || true
```

Correction :

```bash
systemctl restart keepalived
ip addr show <INTERFACE>
```

## 7. SELinux bloque named

Diagnostic :

```bash
getenforce
ausearch -m avc -ts recent
journalctl -t setroubleshoot --since today --no-pager
```

Correction :

```bash
restorecon -Rv /etc/named.conf /etc/named /var/named /var/log/named
setsebool -P named_write_master_zones on
systemctl restart named
```


    ---

    [← Retour à l'index](./index.md)

---

[← Retour à l'index](./index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
