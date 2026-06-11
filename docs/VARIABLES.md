ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](./index.md) | [Architecture](./ARCHITECTURE.md) | [Déploiement](./DEPLOYMENT.md) | [Exploitation](./OPERATIONS.md) | [Sécurité](./SECURITY.md) | [Troubleshooting](./TROUBLESHOOTING.md) | [Checklist](./PRODUCTION-CHECKLIST.md)

# Variables


## Objectif

Ce document décrit le périmètre, les principes de conception, les procédures d'exploitation et les points de contrôle associés au composant traité.

## Périmètre

Le projet vise des plateformes Red Hat / RHEL-like utilisant BIND, SELinux, systemd et éventuellement firewalld. Les rôles DNS sont séparés entre proxy DNS et autoritaire global.

## Principes d'exploitation

- Les configurations finales sont générées depuis `src/dnsforge/infrastructure/templates/` et `src/settings/`.
- Les secrets ne doivent pas être versionnés en clair.
- Les rendus dans `src/render/` sont des artefacts générés.
- Les déploiements doivent être validés avant redémarrage de service.
- Toute modification de zone doit être accompagnée de tests `named-checkconf`, `named-checkzone` et `dig`.

## Procédure standard

```bash
./src/dnsProxyDeploy.sh <node> --dry-run
./src/dnsProxyDeploy.sh <node> --render-only
./src/dnsProxyDeploy.sh <node> --validate-only
./src/dnsProxyDeploy.sh <node>
```

Pour le rôle autoritaire :

```bash
./src/dnsAuthoritativeDeploy.sh <node> --dry-run
./src/dnsAuthoritativeDeploy.sh <node>
```

## Validation

Contrôles minimum :

```bash
named-checkconf -z /etc/named.conf
rndc status
dig @<dns-ip> <zone> SOA
```

## Rollback

Chaque déploiement crée une sauvegarde sous :

```text
/var/backups/binddns/<timestamp>/
```

La restauration consiste à réappliquer la sauvegarde puis relancer les contrôles.

## Points d'attention

- Ne pas exposer directement le rôle autoritaire aux clients externes.
- Utiliser TSIG pour les échanges inter-serveurs.
- Garder RNDC limité au réseau d'administration.
- Appliquer les contextes SELinux après copie.
- Si firewalld est actif, vérifier les services et ports ouverts.

---

[← Retour à l'index](./index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
