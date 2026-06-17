// DNSForge managed proxy-hybrid internal hint zone.
zone "." {
    type hint;
    file "{{ ZONE_FILE }}";
};
