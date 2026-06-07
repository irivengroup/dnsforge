ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](../index.md) | [Architecture](../ARCHITECTURE.md) | [Déploiement](../DEPLOYMENT.md) | [Exploitation](../OPERATIONS.md) | [Sécurité](../SECURITY.md) | [Troubleshooting](../TROUBLESHOOTING.md) | [Checklist](../PRODUCTION-CHECKLIST.md)

# Rotation TSIG

## Objectif

Renouveler la clé TSIG utilisée pour les transferts DNS.

## 1. Générer une nouvelle clé

```bash
./src/tools/generate-tsig.sh xfr-shared-key
```

Conserver la sortie dans un coffre sécurisé.

## 2. Mettre à jour les inventaires

```bash
vi src/settings/dns-authoritative/<node>.env
vi src/settings/dns-proxy/<node>.env
```

Mettre à jour :

```bash
TSIG_KEY_NAME="xfr-shared-key"
TSIG_SECRET="<nouveau-secret>"
```

## 3. Vérifier qu'aucun placeholder ne reste

```bash
./src/tools/check-secrets.sh
```

## 4. Déployer les authoritative

```bash
sudo ./src/dnsAuthoritativeDeploy.sh <node>
```

## 5. Déployer les proxys

```bash
sudo ./src/dnsProxyDeploy.sh <node>
```

## 6. Tester

```bash
dig @<AUTHORITATIVE_BACK_IP> <ZONE> AXFR -y <TSIG_KEY_NAME>:<TSIG_SECRET>
dig @<AUTHORITATIVE_BACK_IP> <ZONE> AXFR
```

Le transfert sans TSIG doit échouer.

## 7. Rollback

Restaurer l'ancien secret dans les inventaires, puis redéployer dans le même ordre.

---

[← Retour à l'index](../index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
