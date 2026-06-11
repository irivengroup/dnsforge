ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](./index.md) | [Architecture](./ARCHITECTURE.md) | [Déploiement](./DEPLOYMENT.md) | [Exploitation](./OPERATIONS.md) | [Sécurité](./SECURITY.md) | [Troubleshooting](./TROUBLESHOOTING.md) | [Checklist](./PRODUCTION-CHECKLIST.md)

# DNSSEC Enterprise

## Objectif

La v4.8 ajoute un socle DNSSEC optionnel orienté entreprise.

Le projet fournit :

```text
src/dnsforge/infrastructure/build/common/dnssec/dnssec-policy.conf.j2
src/dnsforge/infrastructure/build/common/dnssec/dnssec-options.conf.j2
src/dnsforge/infrastructure/build/dns-authoritative/templates/master-zone-dnssec.conf.tpl
```

DNSSEC est prévu principalement pour les zones master portées par les nœuds authoritative. Les proxys continuent d'assurer la validation récursive via :

```bind
dnssec-validation auto;
```

## Variables

```bash
ENABLE_DNSSEC="no"
DNSSEC_POLICY_NAME="binddns-default"
DNSSEC_KEY_DIRECTORY="/var/named/dnssec"
DNSSEC_SIGNING_MODE="policy"
```

## Générer le rendu

```bash
./src/dnsAuthoritativeDeploy.sh <node> --render-only
```

Contrôler :

```bash
cat src/render/dns-authoritative/<node>/etc/named/dnssec/dnssec-policy.conf
cat src/render/dns-authoritative/<node>/etc/named/dnssec/dnssec-options.conf
ls -ld src/render/dns-authoritative/<node>/var/named/dnssec
```

## Activer DNSSEC sur une zone

Utiliser le template :

```text
src/dnsforge/infrastructure/build/dns-authoritative/templates/master-zone-dnssec.conf.tpl
```

La déclaration de zone doit contenir :

```bind
dnssec-policy "<POLICY_NAME>";

inline-signing yes;
```

## Déployer

```bash
sudo ./src/dnsAuthoritativeDeploy.sh <node>
```

## Vérifier la signature

```bash
rndc signing -list <ZONE>
rndc dnssec -status <ZONE>
dig @<AUTHORITATIVE_BACK_IP> <ZONE> SOA +dnssec
delv @<AUTHORITATIVE_BACK_IP> <ZONE> SOA
```

## Exporter le DS

Selon le mode de gestion choisi :

```bash
rndc dnssec -status <ZONE>
```

ou inspecter les clés générées dans :

```text
/var/named/dnssec
```

## Points d'attention

- Ne pas activer DNSSEC sans procédure de publication DS.
- Tester la zone en environnement de recette.
- Surveiller les expirations RRSIG.
- Documenter les rollovers KSK/ZSK.
- Prévoir rollback avant publication DS.

## Tests

```bash
./tests/dnssec/check-dnssec-templates.sh
./tests/dnssec/check-dnssec-render.sh
./tests/dnssec/check-runtime-dnssec.sh <ZONE>
```

---

[← Retour à l'index](./index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
