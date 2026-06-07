ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](../index.md) | [Architecture](../ARCHITECTURE.md) | [Déploiement](../DEPLOYMENT.md) | [Exploitation](../OPERATIONS.md) | [Sécurité](../SECURITY.md) | [Troubleshooting](../TROUBLESHOOTING.md) | [Checklist](../PRODUCTION-CHECKLIST.md)

# Failover authoritative


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

## 1. Vérifier le nœud actif

```bash
ip addr show | grep <VIP_BACK_IP>
systemctl status keepalived --no-pager
```

## 2. Simuler une bascule

Sur le nœud actif :

```bash
systemctl stop keepalived
```

Sur le pair :

```bash
ip addr show | grep <VIP_BACK_IP>
dig @<VIP_BACK_IP> <ZONE> SOA
```

## 3. Retour nominal

```bash
systemctl start keepalived
systemctl status keepalived --no-pager
```


    ---

    [← Retour à l'index](../index.md)

---

[← Retour à l'index](../index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
