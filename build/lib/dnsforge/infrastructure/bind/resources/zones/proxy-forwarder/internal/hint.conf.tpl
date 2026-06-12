// DNSForge managed proxy-forwarder internal hint zone.
zone "." {
    type hint;
    file "{{ ZONE_FILE }}";
};
