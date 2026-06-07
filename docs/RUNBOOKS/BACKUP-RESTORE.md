ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](../index.md) | [Architecture](../ARCHITECTURE.md) | [Déploiement](../DEPLOYMENT.md) | [Exploitation](../OPERATIONS.md) | [Sécurité](../SECURITY.md) | [Troubleshooting](../TROUBLESHOOTING.md) | [Checklist](../PRODUCTION-CHECKLIST.md)

# Runbook sauvegarde/restauration

## 1. Sauvegarder

```bash
sudo ./src/tools/backup-binddns.sh
```

## 2. Lister

```bash
sudo ./src/tools/list-backups.sh
```

## 3. Restaurer

```bash
sudo ./src/tools/restore-binddns.sh /var/backups/binddns/<timestamp>.tar.gz
```

## 4. Valider

```bash
named-checkconf -z /etc/named.conf
rndc status
systemctl status named --no-pager
dig @<DNS_IP> <ZONE> SOA
```

Côté authoritative :

```bash
systemctl status keepalived --no-pager
ip addr show
dig @<VIP_BACK_IP> <ZONE> SOA
```

## 5. Contrôler les logs

```bash
journalctl -u named -n 100 --no-pager
tail -n 100 /var/log/named/default.log
```

---

[← Retour à l'index](../index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
