ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](../index.md) | [Architecture](../ARCHITECTURE.md) | [Déploiement](../DEPLOYMENT.md) | [Exploitation](../OPERATIONS.md) | [Sécurité](../SECURITY.md) | [Troubleshooting](../TROUBLESHOOTING.md) | [Checklist](../PRODUCTION-CHECKLIST.md)

# Installer la supervision

## Objectif

Installer les artefacts de supervision générés par le projet.

## 1. Générer le rendu

```bash
./src/dnsProxyDeploy.sh <node> --render-only
```

ou :

```bash
./src/dnsAuthoritativeDeploy.sh <node> --render-only
```

## 2. Déployer le nœud

```bash
sudo ./src/dnsProxyDeploy.sh <node>
```

ou :

```bash
sudo ./src/dnsAuthoritativeDeploy.sh <node>
```

## 3. Vérifier le statistics-channel

```bash
ss -lntup | grep ':8053'
curl http://<ADM_IP>:8053/json/v1/server
```

## 4. Installer bind_exporter

```bash
cp /opt/binddns/monitoring/prometheus/bind-exporter.service /etc/systemd/system/bind-exporter.service
systemctl daemon-reload
systemctl enable --now bind-exporter
systemctl status bind-exporter --no-pager
```

## 5. Tester les métriques

```bash
curl http://<ADM_IP>:9119/metrics
```

## 6. Intégrer Prometheus

```bash
cat /opt/binddns/monitoring/prometheus/prometheus-scrape-bind.yml
promtool check config /etc/prometheus/prometheus.yml
systemctl reload prometheus
```

## 7. Intégrer Telegraf

```bash
cp /opt/binddns/monitoring/telegraf/telegraf-binddns.conf /etc/telegraf/telegraf.d/
telegraf --test --config /etc/telegraf/telegraf.d/telegraf-binddns.conf
systemctl restart telegraf
```

## 8. Validation

```bash
./tests/monitoring/check-statistics-channel.sh /etc
curl http://<ADM_IP>:8053/json/v1/server
curl http://<ADM_IP>:9119/metrics
```

---

[← Retour à l'index](../index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
