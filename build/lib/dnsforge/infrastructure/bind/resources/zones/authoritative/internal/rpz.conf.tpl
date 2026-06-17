// DNSForge managed authoritative internal rpz zone.
zone "{{ zone_name }}" {
    type master;
    file "{{ ZONE_FILE }}";
    allow-query { localhost; admin_clients; };
    allow-transfer { none; };
    allow-update { none; };
    notify no;
};
