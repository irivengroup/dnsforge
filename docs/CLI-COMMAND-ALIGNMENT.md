# DNSForge CLI Command Alignment

This document defines the active CLI contract enforced by tests.

The test suite validates that every exposed parser form below is both parseable and dispatched by `DnsForgeCommandDispatcher`.
Any new command, subcommand, or option must be added to `tests/cli/test_cli_dispatch_alignment.py`.

## Global option

```bash
dnsforge --project-root <path> <command>
```

## Core

```bash
dnsforge validate
dnsforge validate proxy [node] [--type forwarder|hybrid]
dnsforge validate authoritative [node]

dnsforge render
dnsforge render proxy [node] [--type forwarder|hybrid]
dnsforge render authoritative [node]

dnsforge deploy [--target-root <path>] [--dry-run]
dnsforge deploy proxy [node] [--type forwarder|hybrid] [--target-root <path>] [--dry-run]
dnsforge deploy authoritative [node] [--target-root <path>] [--dry-run]

dnsforge initialize [--render-only] [--apply] [--dry-run]
dnsforge initialize proxy [node] [--type forwarder|hybrid] [--render-only] [--apply] [--dry-run]
dnsforge initialize authoritative [node] [--render-only] [--apply] [--dry-run]
```

Bare `validate`, `render`, `deploy`, and `initialize` resolve the role from `setup.conf`.

## Zone

```bash
dnsforge zone list
dnsforge zone get --name <zone>
dnsforge zone show [name]
dnsforge zone show --zone <zone> [--version <int>]
dnsforge zone history <zone>
dnsforge zone diff --zone <zone> --from <version> --to <version>
dnsforge zone rollback --zone <zone> --version <version>
dnsforge zone create --name <zone> --type master|secondary|forward --views <views> [--cluster <name>] [--disabled]
dnsforge zone edit <zone> --add <record> [--ttl <int>]
dnsforge zone edit <zone> --update <record> [--ttl <int>]
dnsforge zone edit <zone> --delete <record>
dnsforge zone enable --name <zone>
dnsforge zone disable --name <zone>
dnsforge zone delete --name <zone>
```

## Audit and profile

```bash
dnsforge audit [--strict]
dnsforge profile audit
```

## Security

```bash
dnsforge security [--setup-file <path>] show
dnsforge security [--setup-file <path>] audit
dnsforge security [--setup-file <path>] history
dnsforge security [--setup-file <path>] rollback [--version <version>]
```

## Status and diagnostics

```bash
dnsforge status [--setup-file <path>]
dnsforge health [--setup-file <path>]
dnsforge doctor [--setup-file <path>]
```

## Backup, restore, migration

```bash
dnsforge backup [--backup-root <path>] create [--setup-file <path>] [--dry-run]
dnsforge backup [--backup-root <path>] list
dnsforge restore --backup <archive.tar.gz> [--target-root <path>] [--dry-run]
dnsforge migrate --to proxy-forwarder|proxy-hybrid [--setup-file <path>] [--dry-run]
```

## Cluster

```bash
dnsforge cluster [--setup-file <path>] init [--setup-file <path>] [--dry-run]
dnsforge cluster [--setup-file <path>] status [--setup-file <path>]
dnsforge cluster [--setup-file <path>] validate [--setup-file <path>]
dnsforge cluster [--setup-file <path>] validate-security [--setup-file <path>]
dnsforge cluster [--setup-file <path>] sync [--setup-file <path>] [--dry-run]
```

## ACL

```bash
dnsforge acl [--state-file <path>] list
dnsforge acl [--state-file <path>] show <name>
dnsforge acl [--state-file <path>] create <name>
dnsforge acl [--state-file <path>] delete <name>
dnsforge acl [--state-file <path>] add-network <name> <network>
dnsforge acl [--state-file <path>] remove-network <name> <network>
```

## View

```bash
dnsforge view [--state-file <path>] list
dnsforge view [--state-file <path>] create <name>
dnsforge view [--state-file <path>] delete <name>
dnsforge view [--state-file <path>] attach-zone <name> <zone>
```

## DNSSEC

```bash
dnsforge dnssec [--setup-file <path>] status
dnsforge dnssec [--setup-file <path>] validate
dnsforge dnssec [--setup-file <path>] rotate-ksk
dnsforge dnssec [--setup-file <path>] rotate-zsk
dnsforge dnssec [--setup-file <path>] check-expiry
```

## RPZ

```bash
dnsforge rpz [--setup-file <path>] status
dnsforge rpz [--setup-file <path>] enable
dnsforge rpz [--setup-file <path>] update
dnsforge rpz [--setup-file <path>] test <domain>
```
