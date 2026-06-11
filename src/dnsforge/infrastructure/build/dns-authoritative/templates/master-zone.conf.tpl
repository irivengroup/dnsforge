zone "{{ ZONE_NAME }}" {

        type master;

        file "/var/named/master/{{ VIEW_NAME }}/{{ ZONE_NAME }}.zone";

        allow-query {
                transfer_clients;
        };

        allow-transfer {
                key "{{ TSIG_KEY_NAME }}";
        };

        also-notify {
                {{ PROXY_TRANSFER_CLIENTS }}
        };

        notify yes;
};
