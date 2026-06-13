ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

# Rendu Python natif

## Objectif

La v8.6 introduit un rendu Python natif pour produire l'arborescence de configuration BIND.

Le moteur Bash historique reste disponible, mais la commande suivante ne passe plus par les scripts Bash :

```bash
dnsforge render proxy <node> --type forwarder
dnsforge render proxy <node> --type hybrid
dnsforge render authoritative <node>
```

## Arborescence générée

Proxy :

```text
src/render/dns-proxy/<node>/
├── etc/
│   ├── named.conf
│   └── named/
└── var/
    └── named/
```

Authoritative :

```text
src/render/dns-authoritative/<node>/
```

## Modes proxy

```text
forwarder : aucun fichier local-zone/master généré
hybrid    : local-zones + zone-routing + var/named/master
```



---

Copyright
© IRIVEN Group — All Rights Reserved

