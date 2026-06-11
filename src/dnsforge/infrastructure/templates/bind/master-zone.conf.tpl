zone "{{ zone_name }}" {
    type master;
    file "{{ MASTER_ZONE_FILE }}";
    allow-transfer { zone_transfer_clients; };
    update-policy { grant rndc-key zonesub any; };
};
