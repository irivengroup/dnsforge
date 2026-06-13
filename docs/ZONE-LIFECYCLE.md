# DNSForge Zone Lifecycle Commands

DNSForge keeps `dnsforge zone list` as the primary zone inventory command.

## Inventory

```bash
dnsforge zone list
```

Lists every configured zone.

```bash
dnsforge zone list --enabled
```

Lists enabled/active zones only.

## Lifecycle

```bash
dnsforge zone create <zone> [--type master|secondary|stub|forward|hint|rpz|catalog|reverse-master|reverse-secondary] [--views internal,external] [--profile authoritative|proxy-forwarder|proxy-hybrid] [--cluster <name>] [--disabled]
dnsforge zone show <zone>
dnsforge zone edit <zone> --add <record> [--ttl <seconds>]
dnsforge zone edit <zone> --update <record> [--ttl <seconds>]
dnsforge zone edit <zone> --delete <record>
dnsforge zone disable <zone>
dnsforge zone enable <zone>
dnsforge zone status <zone>
dnsforge zone backup <zone>
dnsforge zone delete <zone>
```

## History, diff and restore

```bash
dnsforge zone history <zone>
dnsforge zone diff <zone> --id <ID>
dnsforge zone history diff <zone> --id1 <ID1> --id2 <ID2>
dnsforge zone restore <zone> --id <ID>
```

Backward-compatible forms remain supported where they already existed:

```bash
dnsforge zone get --name <zone>
dnsforge zone show --zone <zone> --version <ID>
dnsforge zone diff --zone <zone> --from <ID1> --to <ID2>
dnsforge zone rollback --zone <zone> --version <ID>
```
