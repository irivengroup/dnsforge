# DNSForge distributed topology

DNSForge distinguishes local node identity from distributed topology.

## Authoritative cluster scope

Cluster governance applies only to authoritative DNS servers. An authoritative deployment may expose one or more VIPs, for example two 2-node authoritative clusters exposing two VIP addresses.

Proxy nodes are not members of an authoritative HA cluster.

## Peer variables

`PEER_AUTHORITATIVE_ADDRESSES` replaces the legacy `AUTHORITATIVE_BACK_IP`. It contains authoritative server IP addresses or authoritative cluster VIP addresses consumed by proxies.

`PEER_PROXY_ADDRESSES` lists peer proxy addresses for future proxy synchronization workflows.

Obsolete proxy HA variables are intentionally not used anymore:

- `PROXY_VIP_FRONT_IP`
- `PROXY_KEEPALIVED_INTERFACE`

