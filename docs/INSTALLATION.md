ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

# Installation système

```bash
sudo ./install/install.sh --profile authoritative
sudo ./install/install.sh --profile proxy-forwarder
sudo ./install/install.sh --profile proxy-hybrid
```

L'installation crée :

```text
/opt/dnsforge
/etc/dnsforge
/opt/dnsforge/settings -> /etc/dnsforge

/usr/local/bin/dnsforge
```

Le fichier opérateur initial est :

```text
/etc/dnsforge/setup.conf
```

Après édition :

```bash```

Puis :

```bash
dnsforge validate proxy proxy01 --type forwarder
dnsforge render proxy proxy01 --type forwarder
dnsforge initialize --dry-run
dnsforge initialize
```

---
Copyright
© IRIVEN Group — All Rights Reserved
