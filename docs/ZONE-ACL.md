ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](./index.md) | [Architecture](./ARCHITECTURE.md) | [Déploiement](./DEPLOYMENT.md) | [Exploitation](./OPERATIONS.md) | [Sécurité](./SECURITY.md) | [Troubleshooting](./TROUBLESHOOTING.md) | [Checklist](./PRODUCTION-CHECKLIST.md)

# ACL par vue et par zone

## Objectif

La v5.3 ajoute un cloisonnement plus fin des zones DNS via des ACL par zone et une vue partenaire optionnelle.

## Variables d'inventaire

```bash
ZONE_ACL_PUBLIC="any;"
ZONE_ACL_INTERNAL="recursive_clients;"
ZONE_ACL_PARTNER="partner_clients;"
PARTNER_ALLOWED_CLIENTS="203.0.113.0/24; localhost;"
```

## Vue partenaire

```bind
view "partner" {

        match-clients {
                partner_clients;
        };

        recursion no;

        include "/etc/named/views/partner/secondary/zones.index.conf";
};
```

## Arborescence

```text
src/build/dns-proxy/zones/partner/
├── master/
├── secondary/
└── forward/
```

## Validation

```bash
./tests/integration/check-zone-acl-render.sh
```

---

[← Retour à l'index](./index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
