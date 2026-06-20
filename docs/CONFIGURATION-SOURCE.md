DNSForge
Plateforme Enterprise de déploiement et de configuration BIND

# Source de configuration

Depuis v10.1, le dossier `src/settings` n'existe plus.

La configuration opérateur est portée par :

```text
/etc/dnsforge/setup.conf
```

Le fichier `setup.conf` est généré dynamiquement par `SetupProfileGenerator` depuis des dictionnaires de profil composables. Le projet ne consomme plus `legacy profile resources/`.

Le lien applicatif reste :

```text
/opt/dnsforge/settings -> /etc/dnsforge
```

---
Copyright
© IRIVEN Group — All Rights Reserved
