ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](./index.md) | [Architecture](./ARCHITECTURE.md) | [Déploiement](./DEPLOYMENT.md) | [Exploitation](./OPERATIONS.md) | [Sécurité](./SECURITY.md) | [Troubleshooting](./TROUBLESHOOTING.md) | [Checklist](./PRODUCTION-CHECKLIST.md)

# DNSSEC Enterprise

## Objectif

La v5.6 renforce DNSSEC pour les zones publiques issues du catalogue.

## Politique enterprise

```text
TemplateRegistry + BindConfigFactory DNSSEC generation
```

Elle inclut :

```text
- KSK séparée ;
- ZSK avec rollover périodique ;
- NSEC3 ;
- CDS/CDNSKEY via SHA-256 ;
- fenêtres de validité et de refresh RRSIG.
```

## Zone publique catalogue

Une zone publique master générée reçoit :

```bind
dnssec-policy "{ DNSSEC_POLICY_NAME }";

inline-signing yes;
```

## Générer

```bash
./src/tools/generate-zone-catalog.sh
```

## Tester

```bash
./tests/dnssec/check-dnssec-enterprise-templates.sh
./tests/dnssec/check-catalog-public-dnssec.sh
./tests/dnssec/check-dnssec-enterprise-render.sh
```

## Runtime

```bash
./tests/dnssec/check-runtime-public-zone-dnssec.sh <ZONE> <SERVER>
```

Commandes manuelles :

```bash
dig @<SERVER> <ZONE> SOA +dnssec
dig @<SERVER> <ZONE> DNSKEY +dnssec
delv @<SERVER> <ZONE> SOA
rndc dnssec -status <ZONE>
rndc signing -list <ZONE>
```

---

[← Retour à l'index](./index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
