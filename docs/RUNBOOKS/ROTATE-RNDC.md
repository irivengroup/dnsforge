ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](../index.md) | [Architecture](../ARCHITECTURE.md) | [Déploiement](../DEPLOYMENT.md) | [Exploitation](../OPERATIONS.md) | [Sécurité](../SECURITY.md) | [Troubleshooting](../TROUBLESHOOTING.md) | [Checklist](../PRODUCTION-CHECKLIST.md)

# Rotation RNDC


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

## 1. Générer un secret

```bash
rndc-confgen -a -A hmac-sha256
```

## 2. Mettre à jour l'inventaire du nœud

```bash
vi src/settings/<role>/<node>.env
```

## 3. Déployer

```bash
sudo ./src/dnsProxyDeploy.sh <node>
# ou
sudo ./src/dnsAuthoritativeDeploy.sh <node>
```

## 4. Tester

```bash
rndc status
```


    ---

    [← Retour à l'index](../index.md)

---

[← Retour à l'index](../index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
