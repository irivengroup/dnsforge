ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](./index.md) | [Architecture](./ARCHITECTURE.md) | [Déploiement](./DEPLOYMENT.md) | [Exploitation](./OPERATIONS.md) | [Sécurité](./SECURITY.md) | [Troubleshooting](./TROUBLESHOOTING.md) | [Checklist](./PRODUCTION-CHECKLIST.md)

# Firewalld


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

## État

```bash
systemctl is-active firewalld
firewall-cmd --list-all
```

## Règles DNS

```bash
firewall-cmd --permanent --add-service=dns
firewall-cmd --permanent --add-port=953/tcp
firewall-cmd --permanent --add-port=8053/tcp
firewall-cmd --reload
```

## VRRP

```bash
firewall-cmd --permanent --add-protocol=vrrp
firewall-cmd --reload
```


    ---

    [← Retour à l'index](./index.md)

---

[← Retour à l'index](./index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
