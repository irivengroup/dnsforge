# DNSForge Authoritative HA Cluster

DNSForge cluster support applies only to authoritative DNS servers.
Proxy forwarder and proxy hybrid nodes are not cluster members; they consume
`PEER_AUTHORITATIVE_ADDRESSES`, which may contain authoritative VIPs or standalone
authoritative IP addresses.

Supported commands:

```bash
dnsforge cluster status
dnsforge cluster validate
dnsforge cluster validate-security
dnsforge cluster render --reason "Render authoritative HA"
dnsforge cluster apply --reason "Apply authoritative HA"
dnsforge cluster sync --reason "Sync authoritative HA"
dnsforge audit cluster
```

A cluster may contain two or more authoritative nodes. Each cluster exposes one
`CLUSTER_VIP` through Keepalived. Multiple independent authoritative clusters can
therefore expose multiple VIPs to proxies.

Minimum authoritative setup variables:

```ini
ROLE="dns-authoritative"
NODE_NAME="auth01"
ENABLE_CLUSTER="yes"
CLUSTER_ROLE="authoritative"
CLUSTER_NAME="dns-prod-a"
CLUSTER_PEERS="10.10.10.11,10.10.10.12"
CLUSTER_VIP="10.10.10.100"
CLUSTER_INTERFACE="eth1"
CLUSTER_PRIORITY="150"
CLUSTER_VRID="53"
CLUSTER_AUTH_PASS="CHANGE_ME"
```
