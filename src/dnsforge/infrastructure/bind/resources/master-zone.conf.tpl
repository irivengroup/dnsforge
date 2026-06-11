zone "{{ zone_name }}" {
    type master;
    file "{{ MASTER_ZONE_FILE }}";
    allow-query { any; };
    allow-transfer { zone_transfer_clients; };
    also-notify { {{ ALSO_NOTIFY }} };
    notify explicit;
    check-names warn;
    update-policy { grant {{ UPDATE_KEY_NAME }} zonesub any; };
};
