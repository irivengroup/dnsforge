ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](../index.md) | [Architecture](../ARCHITECTURE.md) | [Déploiement](../DEPLOYMENT.md) | [Exploitation](../OPERATIONS.md) | [Sécurité](../SECURITY.md) | [Troubleshooting](../TROUBLESHOOTING.md) | [Checklist](../PRODUCTION-CHECKLIST.md)

# Déploiement production sécurisé

## 1. Générer le rendu

```bash
./src/dnsProxyDeploy.sh <node> --render-only
```

ou :

```bash
./src/dnsAuthoritativeDeploy.sh <node> --render-only
```

## 2. Exécuter le gate

```bash
./src/tools/deployment/preflight-production-gate.sh src/render/dns-proxy/<node>
```

## 3. Voir le diff

```bash
./src/tools/deployment/diff-rendered-config.sh src/render/dns-proxy/<node>
```

## 4. Sauvegarder

```bash
sudo ./src/tools/backup-binddns.sh
```

## 5. Appliquer

```bash
sudo ./src/dnsProxyDeploy.sh <node>
```

## 6. Valider

```bash
named-checkconf -z /etc/named.conf
rndc status
dig @<DNS_IP> <ZONE> SOA
```

## 7. Rollback

```bash
sudo ./src/tools/deployment/rollback-latest.sh
```

---

[← Retour à l'index](../index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
