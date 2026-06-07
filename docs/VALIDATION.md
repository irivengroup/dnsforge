ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](./index.md) | [Architecture](./ARCHITECTURE.md) | [Déploiement](./DEPLOYMENT.md) | [Exploitation](./OPERATIONS.md) | [Sécurité](./SECURITY.md) | [Troubleshooting](./TROUBLESHOOTING.md) | [Checklist](./PRODUCTION-CHECKLIST.md)

# Validation complète

## Objectif

La v4.0 ajoute une suite de validation centralisée permettant de contrôler le projet, les rendus, les sources de zones, la documentation et certains prérequis système.

## Lancer tous les contrôles

Depuis la racine du projet :

```bash
./tests/run-all.sh
```

## Préparer un rendu avant validation BIND

Proxy :

```bash
./src/dnsProxyDeploy.sh <node> --render-only
```

Authoritative :

```bash
./src/dnsAuthoritativeDeploy.sh <node> --render-only
```

Puis :

```bash
./tests/run-all.sh
```

## Audit de rendu

```bash
./tests/render/check-render-settings.sh
./tests/render/check-render-proxy.sh <node>
./tests/render/check-render-authoritative.sh <node>
./tests/render/check-render-paths.sh
./tests/render/check-render-no-placeholders.sh
```

## Contrôles unitaires disponibles

Documentation :

```bash
./tests/documentation/check-doc-navigation.sh
```

Style BIND :

```bash
./tests/style/check-bind-template-format.sh
```

Sources de zones :

```bash
./tests/dns-validation/check-zone-sources.sh
```

Index générés :

```bash
./tests/dns-validation/check-zone-indexes.sh
```

Zones master côté proxy :

```bash
./tests/dns-validation/check-proxy-master-zones.sh
```

Configuration BIND rendue :

```bash
./tests/dns-validation/check-rendered-bind-config.sh
```

Fichiers de zones rendus :

```bash
./tests/dns-validation/check-rendered-zone-files.sh
```

Baseline sécurité :

```bash
./tests/security/check-security-baseline.sh
```

Absence de noms serveurs codés en dur dans le code :

```bash
./tests/security/check-no-hardcoded-hostnames.sh
```

SELinux :

```bash
./tests/system/check-selinux-state.sh
```

Firewalld :

```bash
./tests/system/check-firewalld-state.sh
```

RNDC :

```bash
./tests/system/check-rndc.sh
```

## Séquence recommandée avant production

```bash
./src/dnsAuthoritativeDeploy.sh <node> --render-only
./src/dnsProxyDeploy.sh <node> --render-only

./tests/run-all.sh

sudo ./src/dnsAuthoritativeDeploy.sh <node>
sudo ./src/dnsProxyDeploy.sh <node>

named-checkconf -z /etc/named.conf
rndc status
dig @<DNS_IP> <ZONE> SOA
```

---

[← Retour à l'index](./index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
