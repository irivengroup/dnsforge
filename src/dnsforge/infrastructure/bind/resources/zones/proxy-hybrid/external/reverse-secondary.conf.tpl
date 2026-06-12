// DNSForge managed proxy-hybrid external reverse-secondary zone.
zone "{{ zone_name }}" {
    type secondary;
    masters { {{ MASTERS }} };
    file "{{ ZONE_FILE }}";
    allow-query { any; };
    allow-transfer { none; };
    notify no;
    check-names warn;
};
