ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](../index.md) | [Architecture](../ARCHITECTURE.md) | [Déploiement](../DEPLOYMENT.md) | [Exploitation](../OPERATIONS.md) | [Sécurité](../SECURITY.md) | [Troubleshooting](../TROUBLESHOOTING.md) | [Checklist](../PRODUCTION-CHECKLIST.md)

# Exécuter la validation complète

## Objectif

Exécuter tous les contrôles projet avant déploiement ou audit.

## 1. Générer les rendus

```bash
./src/dnsAuthoritativeDeploy.sh <node> --render-only
./src/dnsProxyDeploy.sh <node> --render-only
```

## 2. Lancer la validation complète

```bash
./tests/run-all.sh
```

## 3. Contrôler les erreurs

Si un test échoue, relancer uniquement ce test :

```bash
./tests/dns-validation/check-zone-sources.sh
./tests/security/check-security-baseline.sh
```

## 4. Corriger puis relancer

```bash
./tests/run-all.sh
```

## 5. Déployer après validation

```bash
sudo ./src/dnsAuthoritativeDeploy.sh <node>
sudo ./src/dnsProxyDeploy.sh <node>
```

---

[← Retour à l'index](../index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
