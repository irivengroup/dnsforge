[Unit]
Description=Prometheus exporter for BIND DNS statistics
After=network-online.target named.service
Wants=network-online.target

[Service]
Type=simple
User=nobody
Group=nobody
ExecStart=/usr/local/bin/bind_exporter \
        --bind.stats-url=http://{{ ADM_IP }}:8053/ \
        --web.listen-address={{ ADM_IP }}:9119

Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
