// DNSForge managed proxy-forwarder external forward zone.
zone "{{ zone_name }}" {
    type forward;
    forward {{ FORWARD_POLICY }};
    forwarders { {{ FORWARDERS }} };
};
