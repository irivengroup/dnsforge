ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](./index.md) | [Architecture](./ARCHITECTURE.md) | [Déploiement](./DEPLOYMENT.md) | [Exploitation](./OPERATIONS.md) | [Sécurité](./SECURITY.md) | [Troubleshooting](./TROUBLESHOOTING.md) | [Checklist](./PRODUCTION-CHECKLIST.md)

# Checklist de production


Les exemples ci-dessous utilisent des noms de nœuds d'inventaire à titre d'exemple. Le code projet ne doit pas dépendre de ces noms : les scripts chargent toujours les valeurs depuis `src/settings/`.

Avant toute opération, se placer à la racine du projet :

```bash
cd /opt/binddns-enterprise
```

Vérifier l'arborescence :

```bash
tree -L 3
```

Vérifier les scripts :

```bash
ls -l src/dnsProxyDeploy.sh src/dnsAuthoritativeDeploy.sh
```

## Checklist avant mise en production

Exécuter les commandes suivantes et conserver les sorties dans le dossier de changement.

## 1. Inventaires

```bash
find src/settings -type f -name '*.env' -print
grep -R 'CHANGE_ME\|REPLACE_' src/settings
```

Attendu : aucun placeholder en production.

## 2. Rendu

```bash
./src/dnsProxyDeploy.sh <node> --render-only
./src/dnsAuthoritativeDeploy.sh <node> --render-only
find src/render -type f | sort
```

## 3. Style templates

```bash
./tests/style/check-bind-template-format.sh
```

## 4. Documentation

```bash
./tests/documentation/check-doc-navigation.sh
```

## 5. Déploiement dry-run

```bash
./src/dnsProxyDeploy.sh <node> --dry-run
./src/dnsAuthoritativeDeploy.sh <node> --dry-run
```

## 6. Services

```bash
systemctl is-active named
systemctl is-enabled named
systemctl status named --no-pager
```

Côté authoritative :

```bash
systemctl is-active keepalived
systemctl is-enabled keepalived
systemctl status keepalived --no-pager
```

## 7. Configuration

```bash
named-checkconf -z /etc/named.conf
rndc status
```

## 8. Réseau

```bash
ss -lntup | grep -E ':53|:953|:8053'
ss -lnuap | grep ':53'
ip -brief addr
ip route
```

## 9. Firewall

```bash
systemctl is-active firewalld || true
firewall-cmd --list-all 2>/dev/null || true
```

## 10. SELinux

```bash
getenforce
restorecon -nRv /etc/named.conf /etc/named /var/named /var/log/named
```

## 11. DNS

```bash
dig @<DNS_IP> <ZONE> SOA +time=2 +tries=1
dig @<DNS_IP> <ZONE> NS +time=2 +tries=1
dig @<DNS_IP> <HOSTNAME> A +time=2 +tries=1
```

## 12. Transferts

```bash
dig @<AUTHORITATIVE_BACK_IP> <ZONE> AXFR -y <TSIG_KEY_NAME>:<TSIG_SECRET>
dig @<AUTHORITATIVE_BACK_IP> <ZONE> AXFR
```

Le second test doit être refusé.

## 13. Logs

```bash
journalctl -u named -n 200 --no-pager
grep -RniE 'error|failed|denied|servfail|tsig' /var/log/named /var/log/messages 2>/dev/null || true
```

## 14. RPZ

```bash
grep -Rni 'response-policy\|rpz' /etc/named /var/named/rpz
named-checkzone rpz.local /var/named/rpz/rpz.local.zone
dig @<BACK_IP> malware.example.invalid A
```

## 15. Baseline sécurité

```bash
./tests/dns-proxy/validation/check-security-options.sh /etc
```

## Validation finale

```text
[ ] Inventaires validés
[ ] Secrets remplacés
[ ] Templates formatés
[ ] Rendu généré
[ ] named-checkconf OK
[ ] named-checkzone OK
[ ] RNDC OK
[ ] SELinux OK
[ ] Firewall OK
[ ] DNS OK
[ ] AXFR protégé par TSIG
[ ] RPZ active côté proxy
[ ] RRL actif
[ ] DNSSEC validation active
[ ] RNDC limité à ADM
[ ] Logs sans erreur bloquante
[ ] Rollback identifié
```


    ---

    [← Retour à l'index](./index.md)

---

[← Retour à l'index](./index.md)


## Production Gate v5.9

```bash
./src/tools/deployment/preflight-production-gate.sh <render-root>
./src/tools/deployment/diff-rendered-config.sh <render-root>
sudo ./src/tools/backup-binddns.sh
```

Rollback :

```bash
sudo ./src/tools/deployment/rollback-latest.sh
```


---

Copyright
© IRIVEN Group — All Rights Reserved


## RPZ

```text
[ ] RPZ activé uniquement sur les proxies récursifs
[ ] Aucun serveur autoritatif n'utilise RPZ
```
