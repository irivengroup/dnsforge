ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](../index.md) | [Architecture](../ARCHITECTURE.md) | [Déploiement](../DEPLOYMENT.md) | [Exploitation](../OPERATIONS.md) | [Sécurité](../SECURITY.md) | [Troubleshooting](../TROUBLESHOOTING.md) | [Checklist](../PRODUCTION-CHECKLIST.md)

# Exploiter les healthchecks BindDNS

## 1. Tester manuellement

```bash
DNS_SERVER=<DNS_IP> ADM_SERVER=<BIND_ADMIN_IP> TEST_ZONE=<ZONE> \
  /opt/binddns/monitoring/check-binddns-health.sh
```

## 2. Collecter les statistiques BIND

```bash
/opt/binddns/monitoring/collect-rndc-stats.sh
ls -ltr /var/log/named/stats/
```

## 3. Exporter les métriques texte

```bash
/opt/binddns/monitoring/export-binddns-metrics-text.sh
```

## 4. Activer le timer

```bash
cp /opt/binddns/monitoring/systemd/binddns-healthcheck.* /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now binddns-healthcheck.timer
```

## 5. Diagnostic

```bash
journalctl -u binddns-healthcheck.service -n 50 --no-pager
systemctl list-timers | grep binddns
```

---

[← Retour à l'index](../index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
