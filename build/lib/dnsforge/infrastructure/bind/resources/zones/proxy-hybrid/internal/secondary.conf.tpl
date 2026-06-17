// DNSForge managed proxy-hybrid internal secondary zone.
zone "{{ zone_name }}" {
    type secondary;
    masters { {{ MASTERS }} };
    file "{{ ZONE_FILE }}";
    allow-query { recursive_clients; localhost; };
    allow-transfer { none; };
    notify no;
    check-names warn;
};
