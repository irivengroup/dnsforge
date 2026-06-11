[Unit]
Description=Run BindDNS healthcheck periodically

[Timer]
OnBootSec=2min
OnUnitActiveSec=1min
Unit=binddns-healthcheck.service

[Install]
WantedBy=timers.target
