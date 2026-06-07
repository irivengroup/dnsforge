ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](./index.md) | [Architecture](./ARCHITECTURE.md) | [Déploiement](./DEPLOYMENT.md) | [Exploitation](./OPERATIONS.md) | [Sécurité](./SECURITY.md) | [Troubleshooting](./TROUBLESHOOTING.md) | [Checklist](./PRODUCTION-CHECKLIST.md)

# Multi-VIP authoritative

## Objectif

La v5.1 valide concrètement le rendu multi-VIP côté DNS Proxy.

## Inventaire proxy

```bash
AUTHORITATIVE_BACK_IP=("192.0.2.10" "192.0.2.20")
```

## Test d'intégration

```bash
./tests/integration/check-proxy-multivip-render.sh
```

## Rendu attendu

```bind
forwarders {
        192.0.2.10;
        192.0.2.20;
};
```

```bind
primaries {
        192.0.2.10 key "xfr-shared-key";
        192.0.2.20 key "xfr-shared-key";
};
```

```bind
allow-notify {
        192.0.2.10;
        192.0.2.20;
};
```

---

[← Retour à l'index](./index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
