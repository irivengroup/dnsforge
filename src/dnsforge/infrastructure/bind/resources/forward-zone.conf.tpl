zone "{{ zone_name }}" {
    type forward;
    forward {{ FORWARD_POLICY }};
    forwarders { {{ forwarders }} };
};
