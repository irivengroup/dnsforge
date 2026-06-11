DNSForge
Plateforme Enterprise de déploiement et de configuration BIND

# Contexte Templates dans le coeur DNSForge

## Changement

Le dossier historique :

```text
src/dnsforge/infrastructure/build/
```

est supprimé et remplacé par :

```text
src/dnsforge/infrastructure/bind/resources/
```

## Emplacement canonique du catalogue

```text
/etc/dnsforge/zones.yml
```

## Justification DDD

La génération BIND appartient au contexte infrastructure. Le service `TemplateService` adapte dynamiquement les chemins contenus dans les rendus selon le layout natif détecté : Red Hat/Rocky/Alma, Debian/Ubuntu ou SUSE/SLES. Aucun corpus statique `.j2` ou `.tpl` inutilisé ne doit être conservé sous `infrastructure/bind/resources`; les artefacts générés sont déclarés dans `TemplateRegistry`.

```text
src/dnsforge/
├── domain/
├── application/
├── infrastructure/
│   ├── bind/
│   ├── rendering/
│   └── templates/
└── interfaces/
```

Le dossier `build/` ne doit plus réapparaître dans `src/dnsforge/infrastructure`.

---

Copyright
© IRIVEN Group — All Rights Reserved
