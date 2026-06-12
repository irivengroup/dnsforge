# DNSForge initialize flow

Profile selection is performed only by `install/install.sh`.

Examples:

```bash
sudo ./install/install.sh --profile authoritative
sudo ./install/install.sh --profile proxy-forwarder
sudo ./install/install.sh --profile proxy-hybrid
```

The installer deploys `/etc/dnsforge/setup.conf` from the matching packaged profile template. The administrator must edit this file before BIND takeover.

Initialization is profile-neutral at CLI level and always consumes the existing `setup.conf`:

```bash
sudo dnsforge initialize
sudo dnsforge initialize --render-only
sudo dnsforge initialize --apply
```

`dnsforge initialize` determines the runtime profile from `ROLE` and, for proxy nodes, `PROXY_TYPE` in `/etc/dnsforge/setup.conf`.
