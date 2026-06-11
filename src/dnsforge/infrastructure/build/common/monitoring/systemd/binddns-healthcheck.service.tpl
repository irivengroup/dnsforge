[Unit]
Description=BindDNS healthcheck
After=network-online.target named.service
Wants=network-online.target

[Service]
Type=oneshot
Environment=DNS_SERVER={{ BACK_IP }}
Environment=ADM_SERVER={{ ADM_IP }}
Environment=TEST_ZONE=.
ExecStart=/opt/binddns/monitoring/check-binddns-health.sh
