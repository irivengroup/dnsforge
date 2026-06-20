ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](../index.md) | [Architecture](../ARCHITECTURE.md) | [Déploiement](../DEPLOYMENT.md) | [Exploitation](../OPERATIONS.md) | [Sécurité](../SECURITY.md) | [Troubleshooting](../TROUBLESHOOTING.md) | [Checklist](../PRODUCTION-CHECKLIST.md)

# Failover DNS Proxy sans VIP

## Objectif

Valider que la plateforme continue de résoudre les noms lorsque l'un des DNS Proxy est indisponible.

## 1. Identifier les deux proxys

```bash
find src/settings/dns-proxy -maxdepth 1 -type f -name '*.env' -print
```

Récupérer les IPs dans les inventaires :

```bash
grep -E 'BIND_EXTERNET_NICNAME|BIND_INTRANET_NICNAME|BIND_ADMIN_NICNAME' src/settings/dns-proxy/*.env
```

## 2. Tester les deux proxys

```bash
dig @<DNS1_IP> <ZONE> SOA +time=2 +tries=1
dig @<DNS2_IP> <ZONE> SOA +time=2 +tries=1
```

ou :

```bash
DNS1=<DNS1_IP> DNS2=<DNS2_IP> TEST_ZONE=<ZONE> ./tests/proxy-ha/check-proxy-pair-smoke.sh
```

## 3. Simuler la perte du premier proxy

Sur le premier proxy :

```bash
sudo systemctl stop named
```

Depuis un poste de test :

```bash
dig @<DNS1_IP> <ZONE> SOA +time=2 +tries=1
dig @<DNS2_IP> <ZONE> SOA +time=2 +tries=1
```

Le premier peut échouer ; le second doit répondre.

## 4. Remettre le premier proxy

```bash
sudo systemctl start named
sudo systemctl status named --no-pager
rndc status
```

## 5. Vérifier les logs

```bash
journalctl -u named -n 100 --no-pager
tail -n 100 /var/log/named/default.log
tail -n 100 /var/log/named/security.log
```

## 6. Validation finale

```bash
dig @<DNS1_IP> <ZONE> SOA
dig @<DNS2_IP> <ZONE> SOA
```

## 7. Rollback

Aucun rollback réseau n'est nécessaire, car il n'y a pas de VIP.

Si une modification de configuration a causé l'incident :

```bash
ls -ltr /var/backups/binddns/
cp -a /var/backups/binddns/<backup>/named.conf /etc/named.conf
cp -a /var/backups/binddns/<backup>/named /etc/
restorecon -Rv /etc/named.conf /etc/named /var/named /var/log/named
systemctl restart named
```

---

[← Retour à l'index](../index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
