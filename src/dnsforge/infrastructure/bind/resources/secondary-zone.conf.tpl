zone "{{ zone_name }}" {
    type secondary;
    masters { {{ masters }} };
    file "{{ SECONDARY_ZONE_FILE }}";
    allow-query { any; };
    allow-transfer { none; };
    notify no;
};
