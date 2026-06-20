ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](./index.md) | [Architecture](./ARCHITECTURE.md) | [Déploiement](./DEPLOYMENT.md) | [Exploitation](./OPERATIONS.md) | [Sécurité](./SECURITY.md) | [Troubleshooting](./TROUBLESHOOTING.md) | [Checklist](./PRODUCTION-CHECKLIST.md)

# Monitoring natif BindDNS

## Objectif

La v5.7 ajoute un monitoring natif exploitable sans plateforme externe obligatoire.

## Outils

```text
/opt/binddns/monitoring/check-binddns-health.sh
/opt/binddns/monitoring/collect-rndc-stats.sh
/opt/binddns/monitoring/export-binddns-metrics-text.sh
```

## Healthcheck

```bash
DNS_SERVER=<DNS_IP> ADM_SERVER=<BIND_ADMIN_IP> TEST_ZONE=<ZONE> \
  /opt/binddns/monitoring/check-binddns-health.sh
```

Contrôles :

```text
- systemd named actif ;
- rndc status ;
- dig SOA ;
- statistics-channel HTTP JSON.
```

## Collecte rndc stats

```bash
/opt/binddns/monitoring/collect-rndc-stats.sh
```

## Export texte Prometheus simple

```bash
DNS_SERVER=<DNS_IP> ADM_SERVER=<BIND_ADMIN_IP> TEST_ZONE=<ZONE> \
  /opt/binddns/monitoring/export-binddns-metrics-text.sh
```

## Systemd timer

Installer :

```bash
cp /opt/binddns/monitoring/systemd/binddns-healthcheck.* /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now binddns-healthcheck.timer
systemctl list-timers | grep binddns
```

## Tests

```bash
./tests/monitoring/check-native-monitoring-tools.sh
./tests/monitoring/check-native-monitoring-render.sh
```

---

[← Retour à l'index](./index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
