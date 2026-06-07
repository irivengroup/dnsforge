ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](./index.md) | [Architecture](./ARCHITECTURE.md) | [Déploiement](./DEPLOYMENT.md) | [Exploitation](./OPERATIONS.md) | [Sécurité](./SECURITY.md) | [Troubleshooting](./TROUBLESHOOTING.md) | [Checklist](./PRODUCTION-CHECKLIST.md)

# Disaster Recovery

## Objectif

Décrire la reprise d'un service DNS après perte ou corruption d'un nœud.

## Scénario 1 — Perte d'un DNS Proxy

1. Réinstaller le système.
2. Installer le projet.
3. Restaurer la dernière sauvegarde ou redéployer depuis inventaire.

```bash
sudo ./src/tools/restore-binddns.sh /var/backups/binddns/<backup>.tar.gz
```

ou :

```bash
sudo ./src/dnsProxyDeploy.sh <node>
```

Validation :

```bash
named-checkconf -z /etc/named.conf
rndc status
dig @<PROXY_IP> <ZONE> SOA
```

## Scénario 2 — Perte d'un authoritative

1. Vérifier que le pair et la VIP répondent.
2. Restaurer le nœud perdu.
3. Redémarrer BIND et Keepalived.

```bash
sudo ./src/tools/restore-binddns.sh /var/backups/binddns/<backup>.tar.gz
systemctl status named --no-pager
systemctl status keepalived --no-pager
```

Validation VIP :

```bash
ip addr show
dig @<VIP_BACK_IP> <ZONE> SOA
```

## Scénario 3 — Corruption de zone

Restaurer depuis sauvegarde :

```bash
sudo ./src/tools/list-backups.sh
sudo ./src/tools/restore-binddns.sh /var/backups/binddns/<backup>.tar.gz
```

Ou restaurer uniquement depuis Git/source, puis redéployer :

```bash
./src/dnsAuthoritativeDeploy.sh <node> --render-only
sudo ./src/dnsAuthoritativeDeploy.sh <node>
```

## Scénario 4 — Erreur DNSSEC

Avant publication DS, rollback possible par configuration.

Après publication DS, coordonner avec le parent DNS avant toute désactivation.

Commandes :

```bash
rndc dnssec -status <ZONE>
rndc signing -list <ZONE>
dig <ZONE> SOA +dnssec
delv <ZONE> SOA
```

## Critères de reprise

```text
[ ] named actif
[ ] named-checkconf OK
[ ] rndc status OK
[ ] zones critiques répondent
[ ] transferts TSIG OK
[ ] RPZ OK côté proxy
[ ] Keepalived/VIP OK côté authoritative
[ ] monitoring OK
```

---

[← Retour à l'index](./index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
