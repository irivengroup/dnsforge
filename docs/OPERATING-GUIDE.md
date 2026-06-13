ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

# Guide d'exploitation

## Cycle standard

```text
validate -> render -> initialize -> zone
```

## Commandes

```bash
dnsforge validate proxy proxy01 --type forwarder
dnsforge render proxy proxy01 --type hybrid
dnsforge initialize --dry-run
dnsforge zone list
dnsforge audit
```



---

Copyright
© IRIVEN Group — All Rights Reserved

