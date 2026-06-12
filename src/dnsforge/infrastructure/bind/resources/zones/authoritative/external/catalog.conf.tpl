// DNSForge managed authoritative external catalog zone.
zone "{{ zone_name }}" {
    type master;
    file "{{ ZONE_FILE }}";
    allow-query { localhost; admin_clients; };
    allow-transfer { zone_transfer_clients; };
    allow-update { none; };
    notify explicit;
};
