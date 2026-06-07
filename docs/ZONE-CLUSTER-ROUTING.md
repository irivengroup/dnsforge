ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](./index.md) | [Architecture](./ARCHITECTURE.md) | [Déploiement](./DEPLOYMENT.md) | [Exploitation](./OPERATIONS.md) | [Sécurité](./SECURITY.md) | [Troubleshooting](./TROUBLESHOOTING.md) | [Checklist](./PRODUCTION-CHECKLIST.md)

# Routing DNS par zone vers clusters authoritative

## Objectif

La v5.2 permet de router chaque zone proxy vers un cluster authoritative précis.

## Déclaration inventaire

```bash
AUTH_CLUSTER_A_BACK_IP=("192.0.2.10")
AUTH_CLUSTER_B_BACK_IP=("192.0.2.20" "192.0.2.21")
```

## Exemple secondary

```bind
primaries {
        {{ AUTH_CLUSTER_A_PRIMARIES_BIND }}
};

allow-notify {
        {{ AUTH_CLUSTER_A_ALLOW_NOTIFY_BIND }}
};
```

## Exemple forward

```bind
forwarders {
        {{ AUTH_CLUSTER_A_BIND_LIST }}
};
```

## Test

```bash
./tests/integration/check-zone-cluster-routing.sh
```

---

[← Retour à l'index](./index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
