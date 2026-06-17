// DNSForge managed proxy-hybrid internal reverse-master zone.
zone "{{ zone_name }}" {
    type master;
    file "{{ ZONE_FILE }}";
    allow-query { recursive_clients; localhost; };
    allow-transfer { zone_transfer_clients; };
    allow-update { none; };
    also-notify { {{ ALSO_NOTIFY }} };
    notify explicit;
    check-names warn;
    check-integrity yes;
    check-mx warn;
    check-wildcard yes;
};
