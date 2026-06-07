ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](../index.md) | [Architecture](../ARCHITECTURE.md) | [Déploiement](../DEPLOYMENT.md) | [Exploitation](../OPERATIONS.md) | [Sécurité](../SECURITY.md) | [Troubleshooting](../TROUBLESHOOTING.md) | [Checklist](../PRODUCTION-CHECKLIST.md)

# Appliquer le durcissement systemd

## Objectif

Appliquer progressivement le profil de durcissement systemd fourni par le projet.

## 1. Générer le rendu

```bash
./src/dnsProxyDeploy.sh <node> --render-only
```

ou :

```bash
./src/dnsAuthoritativeDeploy.sh <node> --render-only
```

## 2. Déployer normalement

```bash
sudo ./src/dnsProxyDeploy.sh <node>
```

ou :

```bash
sudo ./src/dnsAuthoritativeDeploy.sh <node>
```

## 3. Installer le drop-in systemd

```bash
mkdir -p /etc/systemd/system/named.service.d

cp /opt/binddns/hardening/systemd/named.service.d-hardening.conf \
   /etc/systemd/system/named.service.d/hardening.conf
```

## 4. Recharger systemd

```bash
systemctl daemon-reload
systemctl restart named
```

## 5. Valider BIND

```bash
systemctl status named --no-pager
named-checkconf -z /etc/named.conf
rndc status
dig @<DNS_IP> <ZONE> SOA
```

## 6. Vérifier les propriétés

```bash
systemctl show named \
    -p NoNewPrivileges \
    -p PrivateTmp \
    -p ProtectHome \
    -p ProtectSystem \
    -p CapabilityBoundingSet \
    -p ReadWritePaths
```

## 7. Rollback

```bash
rm -f /etc/systemd/system/named.service.d/hardening.conf
systemctl daemon-reload
systemctl restart named
rndc status
```

---

[← Retour à l'index](../index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
