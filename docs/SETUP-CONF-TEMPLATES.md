DNSForge
Plateforme Enterprise de déploiement et de configuration BIND

# Modèles setup.conf

Les modèles `setup.conf` sont des ressources applicatives embarquées dans le corps Python du produit. Ils ne sont plus portés par `install/`.

Profils générés dynamiquement :

```text
authoritative
proxy-forwarder
proxy-hybrid
```

Les paramètres sont composés depuis :

```text
common_setup
proxy_common_setup
autoritative_setup
hybrid_setup
forwader_setup
```

---
Copyright
© IRIVEN Group — All Rights Reserved
