// DNSForge managed proxy-hybrid internal stub zone.
zone "{{ zone_name }}" {
    type stub;
    masters { {{ MASTERS }} };
    file "{{ ZONE_FILE }}";
    allow-query { recursive_clients; localhost; };
    recursion no;
};
