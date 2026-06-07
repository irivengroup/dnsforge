ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](../index.md) | [Architecture](../ARCHITECTURE.md) | [Déploiement](../DEPLOYMENT.md) | [Exploitation](../OPERATIONS.md) | [Sécurité](../SECURITY.md) | [Troubleshooting](../TROUBLESHOOTING.md) | [Checklist](../PRODUCTION-CHECKLIST.md)

# Restaurer un serveur


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

## 1. Réinstaller les paquets

```bash
dnf install -y bind bind-utils
```

Côté authoritative :

```bash
dnf install -y keepalived
```

## 2. Restaurer une sauvegarde

```bash
cp -a <BACKUP_DIR>/named.conf /etc/named.conf
cp -a <BACKUP_DIR>/named /etc/
cp -a <BACKUP_DIR>/named /var/
restorecon -Rv /etc/named.conf /etc/named /var/named /var/log/named
```

## 3. Valider

```bash
named-checkconf -z /etc/named.conf
systemctl enable --now named
rndc status
```


    ---

    [← Retour à l'index](../index.md)

---

[← Retour à l'index](../index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
