ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](./index.md) | [Architecture](./ARCHITECTURE.md) | [Déploiement](./DEPLOYMENT.md) | [Exploitation](./OPERATIONS.md) | [Sécurité](./SECURITY.md) | [Troubleshooting](./TROUBLESHOOTING.md) | [Checklist](./PRODUCTION-CHECKLIST.md)

# RPZ - Response Policy Zone


## Objectif

La RPZ permet d'appliquer une politique de filtrage DNS sur les nœuds DNS Proxy. Elle ne doit pas être activée sur les serveurs autoritaires globaux.

## Implémentation v4.2

La RPZ est implémentée côté DNS Proxy uniquement.

Le fragment :

```text
src/build/dns-proxy/templates/50-rpz.conf.j2
```

est rendu vers :

```text
/etc/named/rpz/50-rpz.conf
```

puis inclus dans la vue récursive interne :

```bind
include "/etc/named/rpz/50-rpz.conf";
include "/etc/named/rpz/rpz-zone.conf";
```

## Emplacement

Sources :

```text
src/build/dns-proxy/templates/rpz-zone.conf.j2
src/build/dns-proxy/templates/rpz.local.zone.j2
```

Rendu :

```text
src/render/dns-proxy/<node>/etc/named/rpz/rpz-zone.conf
src/render/dns-proxy/<node>/var/named/rpz/<RPZ_ZONE_NAME>.zone
```

Système cible :

```text
/etc/named/rpz/rpz-zone.conf
/var/named/rpz/<RPZ_ZONE_NAME>.zone
```

## Variables

```bash
ENABLE_RPZ="yes"
RPZ_ZONE_NAME="rpz.local"
RPZ_POLICY="recursive-only yes"
RPZ_LOGGING="yes"
```

## Générer le rendu

```bash
./src/dnsProxyDeploy.sh <node> --render-only
```

## Vérifier la configuration générée

```bash
grep -Rni 'response-policy\|rpz' src/render/dns-proxy/<node>/etc/named
cat src/render/dns-proxy/<node>/var/named/rpz/rpz.local.zone
```

## Déployer

```bash
sudo ./src/dnsProxyDeploy.sh <node>
```

## Recharger uniquement la RPZ

```bash
named-checkzone rpz.local /var/named/rpz/rpz.local.zone
rndc reload rpz.local IN internal
```

Si la zone est déclarée hors vue dans votre variante de configuration :

```bash
rndc reload rpz.local
```

## Ajouter un domaine bloqué

Éditer :

```bash
vi /var/named/rpz/rpz.local.zone
```

Ajouter :

```dns
bad.example.net.        CNAME .
```

Incrémenter le serial SOA, puis valider :

```bash
named-checkzone rpz.local /var/named/rpz/rpz.local.zone
rndc reload rpz.local IN internal
```

Tester :

```bash
dig @<BACK_IP> bad.example.net A
```

## Supprimer un domaine

```bash
vi /var/named/rpz/rpz.local.zone
named-checkzone rpz.local /var/named/rpz/rpz.local.zone
rndc reload rpz.local IN internal
```

## Logs

```bash
tail -f /var/log/named/rpz.log
journalctl -u named -f
```

## Validation sécurité

```bash
grep -Rni 'response-policy' /etc/named
dig @<BACK_IP> malware.example.invalid A
```

La RPZ doit s'appliquer uniquement au chemin récursif interne, pas à l'autoritaire global.


    ---

    [← Retour à l'index](./index.md)

---

[← Retour à l'index](./index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
