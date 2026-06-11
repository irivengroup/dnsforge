zone "{{ zone_name }}" {
    type forward;
    forward only;
    forwarders { {{ forwarders }}; };
};
