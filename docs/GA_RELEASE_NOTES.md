# DNSForge 13.0.0 Production GA Release Notes

DNSForge 13.0.0 is the Production General Availability release for the DNSForge agent and DNSForge Manager foundation.

## Release position

This release is a stabilization and certification release. It does not introduce new DNS behavior. The objective is to freeze the production baseline after the v12 operational acceptance, platform certification, upgrade certification and GA readiness work.

## Production scope

DNSForge remains the local BIND administration agent installed on every managed DNS server. It is responsible for rendering, validating, deploying and rolling back local BIND configuration and data.

DNSForge Manager remains the centralized orchestration layer. DNSBeat and DNSSync are Manager submodules. Manager does not edit BIND configuration directly; all changes are routed through DNSForge agents.

## GA validation gates

The GA baseline requires the following gates to pass:

- Ruff formatting and linting
- MyPy type checking
- Bandit security scan
- Coverage policy at 90 percent or higher
- Product Gate at 100/100
- Operational Readiness Gate
- Platform Support Gate
- Upgrade and Migration Certification Gate
- Enterprise CI Validation Gate
- Documentation Parity Gate
- CLI/API Parity Gate
- Dead Code Audit Gate
- Release Gate
- Clean Release Gate

## Certified minimum platforms

DNSForge 13.0.0 keeps the supported minimum platform policy defined during v12:

- RHEL, Rocky Linux and AlmaLinux 8+
- Ubuntu 22.04+
- Debian 10+
- SLES 12+

## Upgrade baseline

The release keeps the certified upgrade paths introduced before GA:

- 11.x to 12.x family
- 12.0.x to 13.0.0
- proxy-forwarder to proxy-hybrid
- proxy-hybrid to proxy-forwarder

## Operational baseline

Production acceptance requires successful execution of:

- `dnsforge readiness`
- `dnsforge readiness --json`
- `dnsforge validate`
- `dnsforge doctor`
- backup, restore, history and rollback runbooks
- disaster recovery runbook
- Manager change workflow runbook

## Security baseline

The GA release keeps the secure CLI policy:

- all DNSForge CLI commands require root or sudo;
- only `dnsforge version` is non-privileged;
- Manager does not modify BIND files directly;
- DNSBeat is read-only;
- DNSSync orchestrates synchronization through DNSForge agents.

## Maintenance branch

Production fixes for this baseline should target the `13.0.x` maintenance line.
