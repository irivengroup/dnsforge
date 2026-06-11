ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

# Guide d'exploitation

## Cycle standard

```text
validate -> render -> initialize -> zone
```

## Commandes

```bash
./bin/dnsforge validate proxy proxy01 --type forwarder
./bin/dnsforge render proxy proxy01 --type hybrid
./bin/dnsforge initialize proxy proxy01 --type forwarder --dry-run
./bin/dnsforge zone list
./bin/dnsforge audit
```



---

Copyright
© IRIVEN Group — All Rights Reserved

