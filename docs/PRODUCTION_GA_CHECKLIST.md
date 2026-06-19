# DNSForge Production GA Checklist

Use this checklist before declaring a DNSForge deployment production-ready.

## Release gates

- [ ] Ruff format check passes.
- [ ] Ruff lint check passes.
- [ ] MyPy passes for Agent and Manager sources.
- [ ] Bandit passes without blocking findings.
- [ ] Coverage is greater than or equal to 90 percent.
- [ ] Product Gate reports 100/100.
- [ ] GA Readiness Gate passes.
- [ ] Release Gate passes.
- [ ] Clean Release Gate passes.
- [ ] Wheel installation test passes.

## Platform certification

- [ ] Target OS is within the supported minimum matrix.
- [ ] BIND is installed and detected.
- [ ] `named-checkconf` is available.
- [ ] `named-checkzone` is available.
- [ ] `rndc` is available.
- [ ] Live BIND smoke validation is enabled where supported.

## Agent readiness

- [ ] `dnsforge readiness` reports READY or accepted WARNING state.
- [ ] `dnsforge readiness --json` returns the expected JSON contract.
- [ ] `dnsforge validate` passes.
- [ ] `dnsforge doctor` passes or documented warnings are accepted.
- [ ] Initial configuration lock behavior has been validated.

## DNS operations

- [ ] Zone create/edit/delete runbook has been tested.
- [ ] Zone history/diff/rollback runbook has been tested.
- [ ] DNSSEC lifecycle runbook has been tested where DNSSEC is enabled.
- [ ] Catalog zone sync/repair runbook has been tested where catalog zones are enabled.
- [ ] Cluster audit/sync runbook has been tested where clustering is enabled.

## Backup and recovery

- [ ] Backup repository exists and is writable.
- [ ] Restore procedure has been tested.
- [ ] Disaster snapshot procedure has been tested.
- [ ] Disaster restore procedure has been tested.
- [ ] Rollback procedure has been tested after a controlled change.

## Manager operations

- [ ] Manager inventory contains the expected DNSForge agents.
- [ ] Node approval workflow has been tested.
- [ ] Token rotation workflow has been tested.
- [ ] DNSSync dry-run has been tested before apply.
- [ ] DNSSync apply has been tested on a non-production change.
- [ ] DNSSync rollback plan is retained.
- [ ] DNSBeat health prevents apply when a node is unhealthy.
- [ ] RBAC has been tested for admin, operator and viewer roles.

## Security baseline

- [ ] Firewall rules match the documented port matrix.
- [ ] RNDC access is restricted.
- [ ] TSIG secrets are protected.
- [ ] ACL and views match the production access model.
- [ ] SELinux or AppArmor posture is documented.
- [ ] Manager never writes BIND files directly.
