ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](./index.md) | [Architecture](./ARCHITECTURE.md) | [Déploiement](./DEPLOYMENT.md) | [Exploitation](./OPERATIONS.md) | [Sécurité](./SECURITY.md) | [Troubleshooting](./TROUBLESHOOTING.md) | [Checklist](./PRODUCTION-CHECKLIST.md)

# Rôle DNS Authoritative


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

## Déploiement

```bash
./src/dnsAuthoritativeDeploy.sh <node> --dry-run
sudo ./src/dnsAuthoritativeDeploy.sh <node>
```

## Tests VIP

```bash
ip addr show
dig @<VIP_BACK_IP> <ZONE> SOA
```

## Vérification transferts

```bash
dig @<VIP_BACK_IP> <ZONE> AXFR -y <TSIG_KEY_NAME>:<TSIG_SECRET>
```


    ---

    [← Retour à l'index](./index.md)

---

[← Retour à l'index](./index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
