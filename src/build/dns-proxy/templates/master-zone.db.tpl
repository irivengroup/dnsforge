$TTL 3600

@       IN SOA  {{ PRIMARY_NS }}. {{ HOSTMASTER }}. (

                {{ SERIAL }}      ; serial
                3600              ; refresh
                900               ; retry
                1209600           ; expire
                300               ; negative cache ttl
)

        IN NS   {{ PRIMARY_NS }}.

{{ PRIMARY_NS_SHORT }}     IN A    {{ PRIMARY_NS_IP }}
