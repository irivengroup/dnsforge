ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

# Gestion des enregistrements DNS

```bash
dnsforge zone show example.com
dnsforge zone edit example.com --add A:www:192.168.10.10
dnsforge zone edit example.com --add AAAA:www:2001:db8::10
dnsforge zone edit example.com --add MX:10:mail.example.com.
dnsforge zone edit example.com --update A:www:192.168.10.10:192.168.10.15
dnsforge zone edit example.com --delete A:www
dnsforge zone edit example.com --add A:api:192.168.10.20 --ttl 300
```

---
Copyright
© IRIVEN Group — All Rights Reserved
