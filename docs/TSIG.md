ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](./index.md) | [Architecture](./ARCHITECTURE.md) | [Déploiement](./DEPLOYMENT.md) | [Exploitation](./OPERATIONS.md) | [Sécurité](./SECURITY.md) | [Troubleshooting](./TROUBLESHOOTING.md) | [Checklist](./PRODUCTION-CHECKLIST.md)

# TSIG

## Objectif

TSIG sécurise les échanges DNS serveur-à-serveur, notamment :

- AXFR ;
- IXFR ;
- NOTIFY.

Le secret TSIG doit être identique sur tous les nœuds participant à la même relation de transfert.

## Générer une clé TSIG

```bash
./src/tools/generate-tsig.sh xfr-shared-key
```

La commande crée un fichier sous :

```text
secrets/
```

Exemple de sortie attendue :

```text
TSIG_KEY_NAME="xfr-shared-key"
TSIG_SECRET="<secret-base64>"
```

## Mettre à jour les inventaires

Éditer les inventaires concernés :

```bash
vi src/settings/dns-proxy/<node>.env
vi src/settings/dns-authoritative/<node>.env
```

Définir :

```bash
TSIG_KEY_NAME="xfr-shared-key"
TSIG_SECRET="<secret-base64>"
```

## Vérifier les secrets

```bash
./src/tools/check-secrets.sh
```

## Déployer

Authoritative :

```bash
sudo ./src/dnsAuthoritativeDeploy.sh <node>
```

Proxy :

```bash
sudo ./src/dnsProxyDeploy.sh <node>
```

## Tester un transfert avec TSIG

```bash
dig @<AUTHORITATIVE_BACK_IP> <ZONE> AXFR -y <TSIG_KEY_NAME>:<TSIG_SECRET>
```

## Tester un transfert sans TSIG

```bash
dig @<AUTHORITATIVE_BACK_IP> <ZONE> AXFR
```

Résultat attendu : refus.

## Audit

```bash
grep -Rni 'key\|allow-transfer\|primaries' /etc/named
grep -Rni 'TSIG_SECRET\|TSIG_KEY_NAME' src/settings
```

---

[← Retour à l'index](./index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
