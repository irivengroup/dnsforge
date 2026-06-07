ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

[Accueil](./index.md) | [Architecture](./ARCHITECTURE.md) | [Déploiement](./DEPLOYMENT.md) | [Exploitation](./OPERATIONS.md) | [Sécurité](./SECURITY.md) | [Troubleshooting](./TROUBLESHOOTING.md) | [Checklist](./PRODUCTION-CHECKLIST.md)

# Monitoring

## Objectif

La v4.4 ajoute les artefacts nécessaires à la supervision des DNS BIND :

- statistics-channel BIND ;
- modèle systemd pour bind_exporter ;
- configuration scrape Prometheus ;
- configuration Telegraf HTTP ;
- notes de dashboard Grafana ;
- tests de cohérence monitoring.

## Statistics channel BIND

La configuration BIND expose les statistiques sur l'interface d'administration :

```bind
statistics-channels {

        inet <ADM_IP> port 8053
        allow {
                admin_clients;
        };
};
```

Vérifier sur un serveur :

```bash
grep -Rni 'statistics-channels' /etc/named
ss -lntup | grep ':8053'
curl http://<ADM_IP>:8053/json/v1/server
```

## Artefacts générés

Après rendu :

```bash
./src/dnsProxyDeploy.sh <node> --render-only
```

ou :

```bash
./src/dnsAuthoritativeDeploy.sh <node> --render-only
```

Contrôler :

```bash
find src/render -path '*/opt/binddns/monitoring/*' -type f -print
```

Fichiers attendus :

```text
opt/binddns/monitoring/prometheus/bind-exporter.service
opt/binddns/monitoring/prometheus/prometheus-scrape-bind.yml
opt/binddns/monitoring/telegraf/telegraf-binddns.conf
opt/binddns/monitoring/grafana/binddns-dashboard-notes.md
```

## Prometheus bind_exporter

Le fichier généré :

```text
/opt/binddns/monitoring/prometheus/bind-exporter.service
```

peut être installé ainsi :

```bash
cp /opt/binddns/monitoring/prometheus/bind-exporter.service /etc/systemd/system/bind-exporter.service
systemctl daemon-reload
systemctl enable --now bind-exporter
systemctl status bind-exporter --no-pager
```

Tester :

```bash
curl http://<ADM_IP>:9119/metrics
```

## Prometheus scrape config

Inclure le fichier :

```text
/opt/binddns/monitoring/prometheus/prometheus-scrape-bind.yml
```

dans la configuration Prometheus.

Validation :

```bash
promtool check config /etc/prometheus/prometheus.yml
systemctl reload prometheus
```

## Telegraf

Copier :

```bash
cp /opt/binddns/monitoring/telegraf/telegraf-binddns.conf /etc/telegraf/telegraf.d/
telegraf --test --config /etc/telegraf/telegraf.d/telegraf-binddns.conf
systemctl restart telegraf
```

## Métriques importantes

Surveiller :

```text
- named up/down ;
- RNDC status ;
- QPS ;
- SERVFAIL ;
- NXDOMAIN ;
- transferts AXFR/IXFR ;
- erreurs TSIG ;
- erreurs DNSSEC ;
- événements RPZ ;
- état Keepalived côté authoritative ;
- disponibilité VIP authoritative.
```

## Tests

```bash
./tests/monitoring/check-monitoring-templates.sh
./tests/monitoring/check-rendered-monitoring.sh
./tests/monitoring/check-statistics-channel.sh /etc
```

---

[← Retour à l'index](./index.md)


---

Copyright
© IRIVEN Group — All Rights Reserved
