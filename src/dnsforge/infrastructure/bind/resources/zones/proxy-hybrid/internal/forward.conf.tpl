// DNSForge managed proxy-hybrid internal forward zone.
zone "{{ zone_name }}" {
    type forward;
    forward {{ FORWARD_POLICY }};
    forwarders { {{ FORWARDERS }} };
};
