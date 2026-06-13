# DNSForge configuration governance

`/etc/dnsforge/setup.conf` is the node source of truth. DNSForge governs it with history, diff, validation, apply and rollback commands.

## Commands

```bash
sudo dnsforge config show
sudo dnsforge config validate
sudo dnsforge config diff
sudo dnsforge config diff --id <ID>
sudo dnsforge config diff --id1 <ID1> --id2 <ID2>
sudo dnsforge config history
sudo dnsforge config apply --reason "<change reason>"
sudo dnsforge config rollback --id <ID> --reason "<rollback reason>"
sudo dnsforge audit config
```

`--reason` is mandatory for `apply` and `rollback` because both commands change the node runtime state.

## Apply pipeline

`config apply` executes:

1. validate `setup.conf`;
2. snapshot current `setup.conf`;
3. render BIND configuration according to the active profile;
4. deploy the rendered tree;
5. validate and reload through the existing deployment service.

## History location

Configuration snapshots are stored under the DNSForge backup root in `config-history/`.
