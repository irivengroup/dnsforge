ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](../index.md) | [Architecture](../ARCHITECTURE.md) | [Déploiement](../DEPLOYMENT.md) | [Exploitation](../OPERATIONS.md) | [Sécurité](../SECURITY.md) | [Troubleshooting](../TROUBLESHOOTING.md) | [Checklist](../PRODUCTION-CHECKLIST.md)

# Rollover DNSSEC

## Objectif

Décrire une procédure de rotation DNSSEC contrôlée.

## 1. Vérifier l'état

```bash
rndc dnssec -status <ZONE>
rndc signing -list <ZONE>
dig @<PEER_AUTHORITATIVE_ADDRESSES> <ZONE> SOA +dnssec
```

## 2. Vérifier la politique

```bash
grep -Rni 'dnssec-policy' /etc/named
cat /etc/named/dnssec/dnssec-policy.conf
```

## 3. Déclencher ou accompagner le rollover

Avec une politique BIND moderne, le rollover est piloté par la policy. Surveiller :

```bash
rndc dnssec -status <ZONE>
ls -l <layout-data-dir>/dnssec
journalctl -u named -f
```

## 4. Contrôler les signatures

```bash
dig @<PEER_AUTHORITATIVE_ADDRESSES> <ZONE> DNSKEY +dnssec
dig @<PEER_AUTHORITATIVE_ADDRESSES> <ZONE> SOA +dnssec
delv @<PEER_AUTHORITATIVE_ADDRESSES> <ZONE> SOA
```

## 5. Publication DS

Avant publication DS :

```bash
dig @<PEER_AUTHORITATIVE_ADDRESSES> <ZONE> DNSKEY +dnssec
```

Après publication DS chez le parent :

```bash
dig <ZONE> DS +dnssec
delv <ZONE> SOA
```

## 6. Rollback

Avant publication DS, désactiver DNSSEC sur la zone et redéployer.

Après publication DS, ne jamais rollback sans coordination avec le parent DNS.

---

[← Retour à l'index](../index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
