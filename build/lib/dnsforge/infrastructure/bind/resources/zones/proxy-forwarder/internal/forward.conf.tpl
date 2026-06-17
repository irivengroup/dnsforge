// DNSForge managed proxy-forwarder internal forward zone.
zone "{{ zone_name }}" {
    type forward;
    forward {{ FORWARD_POLICY }};
    forwarders { {{ FORWARDERS }} };
};
