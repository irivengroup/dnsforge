zone "{{ ZONE_NAME }}" {

        type secondary;

        file "/var/named/secondary/{{ VIEW_NAME }}/{{ ZONE_NAME }}.zone";

        primaries {
                {{ AUTHORITATIVE_BACK_IP_PRIMARIES_BIND }}
        };

        allow-notify {
                {{ AUTHORITATIVE_BACK_IP_ALLOW_NOTIFY_BIND }}
        };

        allow-transfer {
                none;
        };
};
