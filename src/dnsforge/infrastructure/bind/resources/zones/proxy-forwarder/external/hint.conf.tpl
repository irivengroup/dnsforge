// DNSForge managed proxy-forwarder external hint zone.
zone "." {
    type hint;
    file "{{ ZONE_FILE }}";
};
