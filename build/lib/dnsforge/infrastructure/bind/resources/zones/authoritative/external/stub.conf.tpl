// DNSForge managed authoritative external stub zone.
zone "{{ zone_name }}" {
    type stub;
    masters { {{ MASTERS }} };
    file "{{ ZONE_FILE }}";
    allow-query { any; };
    recursion no;
};
