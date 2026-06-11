ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](../index.md) | [Architecture](../ARCHITECTURE.md) | [Déploiement](../DEPLOYMENT.md) | [Exploitation](../OPERATIONS.md) | [Sécurité](../SECURITY.md) | [Troubleshooting](../TROUBLESHOOTING.md) | [Checklist](../PRODUCTION-CHECKLIST.md)

# Supprimer une zone

## 1. Identifier les fichiers source

```bash
find src/dnsforge/infrastructure/build -path '*/zones/*' -type f | grep '<ZONE>'
```

## 2. Archiver les fichiers

```bash
mkdir -p /tmp/binddns-zone-removal
mv <ZONE_FILES> /tmp/binddns-zone-removal/
```

## 3. Regénérer

```bash
./src/dnsAuthoritativeDeploy.sh <node> --render-only
./src/dnsProxyDeploy.sh <node> --render-only
```

## 4. Vérifier que les index ne référencent plus la zone

```bash
grep -R '<ZONE>' src/render || true
```

## 5. Déployer

```bash
sudo ./src/dnsAuthoritativeDeploy.sh <node>
sudo ./src/dnsProxyDeploy.sh <node>
```

## 6. Tester

```bash
dig @<DNS_IP> <ZONE> SOA +time=2 +tries=1
```

---

[← Retour à l'index](../index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
