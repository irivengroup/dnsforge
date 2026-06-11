ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

# Commandes sécurité

```bash
dnsforge security audit
dnsforge security history
dnsforge security rollback --version <id>
dnsforge acl list
dnsforge acl show internal
dnsforge acl create internal
dnsforge acl add-network internal 10.0.0.0/8
dnsforge acl remove-network internal 10.0.0.0/8
dnsforge acl delete internal
dnsforge view list
dnsforge view create internal
dnsforge view attach-zone internal example.com
dnsforge view delete internal
dnsforge dnssec status
dnsforge dnssec validate
dnsforge dnssec rotate-ksk
dnsforge dnssec rotate-zsk
dnsforge dnssec check-expiry
dnsforge rpz status
dnsforge rpz enable
dnsforge rpz update
dnsforge rpz test bad-domain.test
dnsforge cluster validate-security
```

---
Copyright
© IRIVEN Group — All Rights Reserved
