ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](./index.md) | [Architecture](./ARCHITECTURE.md) | [Déploiement](./DEPLOYMENT.md) | [Exploitation](./OPERATIONS.md) | [Sécurité](./SECURITY.md) | [Troubleshooting](./TROUBLESHOOTING.md) | [Checklist](./PRODUCTION-CHECKLIST.md)

# Audit de rendu

## Objectif

La v4.3 ajoute un audit de rendu complet. Le but est de vérifier que les commandes `--render-only` produisent une configuration complète, cohérente, lisible et directement copiable vers `/`.

## Lancer le rendu d'un proxy

```bash
./src/dnsProxyDeploy.sh <node> --render-only
```

## Lancer le rendu d'un authoritative

```bash
./src/dnsAuthoritativeDeploy.sh <node> --render-only
```

## Contrôler tous les inventaires

```bash
./tests/render/check-render-settings.sh
```

Cette commande :

```text
- rend tous les inventaires proxy ;
- rend tous les inventaires authoritative ;
- vérifie les chemins attendus ;
- vérifie l'absence de placeholders ;
- vérifie les zones.index.conf.
```

## Contrôler un proxy

```bash
./tests/render/check-render-proxy.sh <node>
```

## Contrôler un authoritative

```bash
./tests/render/check-render-authoritative.sh <node>
```

## Contrôler les chemins générés

```bash
./tests/render/check-render-paths.sh
```

Chemins attendus côté proxy :

```text
etc/named.conf
etc/named/conf.d/
etc/named/views/external/master/zones.index.conf
etc/named/views/external/secondary/zones.index.conf
etc/named/views/external/forward/zones.index.conf
etc/named/views/internal/master/zones.index.conf
etc/named/views/internal/secondary/zones.index.conf
etc/named/views/internal/forward/zones.index.conf
etc/named/views/internal/reverse/zones.index.conf
etc/named/rpz/50-rpz.conf
etc/named/rpz/rpz-zone.conf
var/named/rpz/
```

Chemins attendus côté authoritative :

```text
etc/named.conf
etc/named/conf.d/
etc/named/zones/external/master/zones.index.conf
etc/named/zones/internal/master/zones.index.conf
etc/named/zones/reverse/master/zones.index.conf
etc/keepalived/keepalived.conf
var/named/master/external/
var/named/master/internal/
var/named/master/reverse/
```

## Contrôler l'absence de placeholders

```bash
./tests/render/check-render-no-placeholders.sh
```

Le test échoue s'il reste :

```text
{ VARIABLE }
CHANGE_ME
REPLACE_
```

## Séquence recommandée avant déploiement

```bash
./tests/render/check-render-settings.sh
./tests/run-all.sh
```

Puis seulement :

```bash
sudo ./src/dnsAuthoritativeDeploy.sh <node>
sudo ./src/dnsProxyDeploy.sh <node>
```

---

[← Retour à l'index](./index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
