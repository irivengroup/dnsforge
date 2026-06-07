ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](./index.md) | [Architecture](./ARCHITECTURE.md) | [Déploiement](./DEPLOYMENT.md) | [Exploitation](./OPERATIONS.md) | [Sécurité](./SECURITY.md) | [Troubleshooting](./TROUBLESHOOTING.md) | [Checklist](./PRODUCTION-CHECKLIST.md)

# Sauvegarde et restauration

## Objectif

La v4.9 ajoute des outils dédiés pour sauvegarder et restaurer une configuration BindDNS complète.

## Outils

```text
src/tools/backup-binddns.sh
src/tools/restore-binddns.sh
src/tools/list-backups.sh
```

## Créer une sauvegarde

```bash
sudo ./src/tools/backup-binddns.sh
```

Sortie attendue :

```text
/var/backups/binddns/<timestamp>.tar.gz
```

## Lister les sauvegardes

```bash
sudo ./src/tools/list-backups.sh
```

## Contenu sauvegardé

```text
/etc/named.conf
/etc/named/
/var/named/
/var/log/named/
/etc/keepalived/
/etc/binddns-release
```

## Restaurer

```bash
sudo ./src/tools/restore-binddns.sh /var/backups/binddns/<timestamp>.tar.gz
```

La restauration exécute ensuite :

```bash
restorecon -Rv /etc/named.conf /etc/named /var/named /var/log/named /etc/keepalived
named-checkconf -z /etc/named.conf
systemctl restart named
rndc status
```

## Sauvegarde vers un emplacement spécifique

```bash
sudo BACKUP_ROOT=/backup/binddns ./src/tools/backup-binddns.sh
```

## Tests

```bash
./tests/backup/check-backup-tools.sh
./tests/backup/check-backup-dry-run.sh
```

---

[← Retour à l'index](./index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
