ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](../index.md) | [Architecture](../ARCHITECTURE.md) | [Déploiement](../DEPLOYMENT.md) | [Exploitation](../OPERATIONS.md) | [Sécurité](../SECURITY.md) | [Troubleshooting](../TROUBLESHOOTING.md) | [Checklist](../PRODUCTION-CHECKLIST.md)

# Activer et contrôler DNSSEC sur une zone publique

## 1. Générer le catalogue

```bash
./src/tools/generate-zone-catalog.sh
```

## 2. Contrôler la déclaration

```bash
grep -Rni 'dnssec-policy\|inline-signing' native BIND view directories managed by DNSForgegenerated/external/master
```

## 3. Déployer

```bash
sudo ./src/dnsAuthoritativeDeploy.sh <node>
sudo ./src/dnsProxyDeploy.sh <node>
```

## 4. Vérifier

```bash
dig @<SERVER> <ZONE> SOA +dnssec
dig @<SERVER> <ZONE> DNSKEY +dnssec
rndc dnssec -status <ZONE>
rndc signing -list <ZONE>
```

## 5. Publication DS

Ne publier le DS chez le parent qu'après validation complète de la chaîne.

---

[← Retour à l'index](../index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
