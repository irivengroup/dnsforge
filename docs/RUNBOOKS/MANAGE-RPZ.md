ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](../index.md) | [Architecture](../ARCHITECTURE.md) | [Déploiement](../DEPLOYMENT.md) | [Exploitation](../OPERATIONS.md) | [Sécurité](../SECURITY.md) | [Troubleshooting](../TROUBLESHOOTING.md) | [Checklist](../PRODUCTION-CHECKLIST.md)

# Gérer la RPZ


## Objectif

Ajouter, supprimer ou tester une règle RPZ sur les DNS Proxy.

## 1. Vérifier l'état actuel

```bash
grep -Rni 'response-policy\|rpz' /etc/named
ls -l /var/named/rpz/
named-checkzone rpz.local /var/named/rpz/rpz.local.zone
```

## 2. Ajouter un domaine bloqué

```bash
vi /var/named/rpz/rpz.local.zone
```

Ajouter :

```dns
blocked.example.net.        CNAME .
```

Incrémenter le serial SOA.

## 3. Valider

```bash
named-checkzone rpz.local /var/named/rpz/rpz.local.zone
```

## 4. Recharger

```bash
rndc reload rpz.local IN internal
```

ou, si nécessaire :

```bash
rndc reconfig
```

## 5. Tester

```bash
dig @<BACK_IP> blocked.example.net A +time=2 +tries=1
tail -n 50 /var/log/named/rpz.log
```

## 6. Rollback

Supprimer l'entrée ajoutée, incrémenter le serial, puis :

```bash
named-checkzone rpz.local /var/named/rpz/rpz.local.zone
rndc reload rpz.local IN internal
```


    ---

    [← Retour à l'index](../index.md)

---

[← Retour à l'index](../index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
