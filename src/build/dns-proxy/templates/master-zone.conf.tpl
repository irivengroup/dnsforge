zone "{{ ZONE_NAME }}" {

        type master;

        file "/var/named/master/{{ VIEW_NAME }}/{{ ZONE_NAME }}.zone";

        allow-query {
                {{ ALLOW_QUERY_ACL }};
        };

        allow-transfer {
                none;
        };

        allow-update {
                none;
        };

        notify no;
};
