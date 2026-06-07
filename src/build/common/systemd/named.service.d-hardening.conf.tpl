[Service]
NoNewPrivileges=true
PrivateTmp=true
ProtectHome=true
ProtectSystem=full
ReadWritePaths=/var/named /var/log/named /run/named /var/run/named
CapabilityBoundingSet=CAP_NET_BIND_SERVICE CAP_SETUID CAP_SETGID CAP_CHOWN CAP_DAC_OVERRIDE
RestrictRealtime=true
LockPersonality=true
MemoryDenyWriteExecute=true
