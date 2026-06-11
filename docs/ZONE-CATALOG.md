ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](./index.md) | [Architecture](./ARCHITECTURE.md) | [Déploiement](./DEPLOYMENT.md) | [Exploitation](./OPERATIONS.md) | [Sécurité](./SECURITY.md) | [Troubleshooting](./TROUBLESHOOTING.md) | [Checklist](./PRODUCTION-CHECKLIST.md)

# Catalogue central des zones

## Objectif

La v5.5 ajoute un catalogue central des zones :

```text
/etc/dnsforge/zones.yml
```

Il permet de générer des zones proxy `master`, `secondary` et `forward`, y compris en split-horizon sur plusieurs vues.

## Générer

```bash
./src/tools/generate-zone-catalog.sh
```

## Tester

```bash
./tests/catalog/check-zone-catalog-generate.sh
./tests/catalog/check-zone-catalog-render.sh
```

## Rendu

Le catalogue génère dans :

```text
native BIND view directories managed by DNSForgegenerated/<view>/<type>/
```

puis le moteur existant crée :

```text
src/render/dns-proxy/<node>/etc/named/views/<view>/<type>/
```

## Bénéfices

```text
- source de vérité unique ;
- split-horizon contrôlé ;
- routing par cluster authoritative ;
- CI/CD plus simple ;
- moins de fichiers maintenus à la main.
```

---

[← Retour à l'index](./index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
