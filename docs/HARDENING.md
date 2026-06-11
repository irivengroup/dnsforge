ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](./index.md) | [Architecture](./ARCHITECTURE.md) | [Déploiement](./DEPLOYMENT.md) | [Exploitation](./OPERATIONS.md) | [Sécurité](./SECURITY.md) | [Troubleshooting](./TROUBLESHOOTING.md) | [Checklist](./PRODUCTION-CHECKLIST.md)

# Durcissement Red Hat / BIND

## Objectif

La v4.6 ajoute un socle de durcissement applicable aux serveurs DNS Red Hat/RHEL-like.

Le durcissement couvre :

- permissions fichiers ;
- SELinux ;
- firewalld ;
- systemd hardening ;
- contrôle des capacités Linux ;
- validation de configuration BIND ;
- absence de secrets et de noms serveurs codés en dur.

## Fichier systemd hardening

Le projet génère un exemple non appliqué automatiquement :

```text
/opt/binddns/hardening/systemd/named.service.d-hardening.conf
```

Il provient de :

```text
BindLayout.systemd_override_dir + Python hardening generation
```

## Pourquoi non appliqué automatiquement

Le hardening systemd peut casser certaines installations BIND selon :

```text
- version Red Hat ;
- chemins runtime spécifiques ;
- politiques SELinux ;
- options DNSSEC ;
- plugins ou exporters locaux.
```

Il est donc livré comme profil contrôlé, à appliquer volontairement après test.

## Appliquer le hardening systemd

```bash
mkdir -p /etc/systemd/system/named.service.d
cp /opt/binddns/hardening/systemd/named.service.d-hardening.conf \
   /etc/systemd/system/named.service.d/hardening.conf

systemctl daemon-reload
systemctl restart named
systemctl status named --no-pager
```

## Vérifier les propriétés systemd

```bash
systemctl show named \
    -p NoNewPrivileges \
    -p PrivateTmp \
    -p ProtectHome \
    -p ProtectSystem \
    -p CapabilityBoundingSet \
    -p ReadWritePaths
```

## Rollback systemd hardening

```bash
rm -f /etc/systemd/system/named.service.d/hardening.conf
systemctl daemon-reload
systemctl restart named
```

## Permissions attendues

```bash
stat -c '%U:%G %a %n' /etc/named.conf
find /etc/named -maxdepth 2 -type f -exec stat -c '%U:%G %a %n' {} \;
find /var/named -maxdepth 2 -type d -exec stat -c '%U:%G %a %n' {} \;
```

Politique attendue :

```text
/etc/named.conf       root:named 640
/etc/named/*          root:named 640 pour fichiers, 750 pour dossiers
/var/named/*          named:named
/var/log/named        named:named 750
```

## SELinux

```bash
getenforce
sestatus
restorecon -nRv /etc/named.conf /etc/named /var/named /var/log/named
ausearch -m avc -ts recent
```

Correction :

```bash
restorecon -Rv /etc/named.conf /etc/named /var/named /var/log/named
setsebool -P named_write_master_zones on
```

## Firewalld

```bash
systemctl is-active firewalld || true
firewall-cmd --list-all 2>/dev/null || true
```

Ports attendus selon rôle :

```text
53/tcp, 53/udp    DNS
953/tcp           RNDC sur ADM
8053/tcp          statistics-channel sur ADM
vrrp              authoritative uniquement si Keepalived actif
```

## Tests projet

```bash
./tests/security/check-hardening-source.sh
./tests/security/check-file-permissions-policy.sh
./tests/security/check-runtime-hardening.sh
```

## Tests complets

```bash
./tests/run-all.sh
```

---

[← Retour à l'index](./index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
