ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](./index.md) | [Architecture](./ARCHITECTURE.md) | [Déploiement](./DEPLOYMENT.md) | [Exploitation](./OPERATIONS.md) | [Sécurité](./SECURITY.md) | [Troubleshooting](./TROUBLESHOOTING.md) | [Checklist](./PRODUCTION-CHECKLIST.md)

# Baseline sécurité


## Objectif

Cette baseline récapitule les exigences de sécurité attendues dans la configuration générée.

## 1. Pas de secrets codés en dur

```bash
grep -R 'CHANGE_ME\|REPLACE_' src/settings
grep -R 'TSIG_SECRET=.*CHANGE_ME\|RNDC_SECRET=.*CHANGE_ME' src/settings
```

## 2. TSIG obligatoire pour transferts

```bash
grep -Rni 'key "{{ TSIG_KEY_NAME }}"\|allow-transfer' src/dnsforge/infrastructure/build src/render
```

Test :

```bash
dig @<AUTHORITATIVE_BACK_IP> <ZONE> AXFR
dig @<AUTHORITATIVE_BACK_IP> <ZONE> AXFR -y <TSIG_KEY_NAME>:<TSIG_SECRET>
```

Sans TSIG : refus attendu. Avec TSIG : transfert autorisé si ACL correcte.

## 3. RNDC limité à ADM

```bash
grep -Rni 'controls' src/render
ss -lntup | grep ':953'
rndc -s <ADM_IP> status
```

## 4. Récursion contrôlée

```bash
named-checkconf -p /etc/named.conf | grep -E 'recursion|allow-recursion|allow-query-cache'
```

## 5. RRL actif

```bash
named-checkconf -p /etc/named.conf | grep -A8 'rate-limit'
```

## 6. Anti-amplification

```bash
named-checkconf -p /etc/named.conf | grep -E 'minimal-any|minimal-responses'
```

## 7. DNSSEC validation

```bash
named-checkconf -p /etc/named.conf | grep dnssec-validation
dig @<BACK_IP> dnssec-failed.org A +dnssec
```

## 8. RPZ côté proxy

```bash
grep -Rni 'response-policy\|rpz.local' /etc/named /var/named/rpz
dig @<BACK_IP> malware.example.invalid A
```

## 9. SELinux

```bash
getenforce
restorecon -nRv /etc/named.conf /etc/named /var/named /var/log/named
ausearch -m avc -ts recent
```

## 10. Firewalld

```bash
systemctl is-active firewalld || true
firewall-cmd --list-all 2>/dev/null || true
```


    ---

    [← Retour à l'index](./index.md)

---

[← Retour à l'index](./index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
