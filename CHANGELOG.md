# Changelog

## 14.7.0

### Added
- Configuration Compliance Engine for rendered-versus-deployed BIND configuration verification.
- `dnsforge config fingerprint` to compute stable configuration fingerprints.
- `dnsforge config verify` and `dnsforge config drift` to detect manual drift.
- `dnsforge config baseline show|rebuild` to inspect expected rendered configuration resources.
- `dnsforge config repair --preview` to generate a safe remediation plan without applying changes.

### Changed
- Compliance checks use rendered DNSForge state as the expected baseline and native BIND paths as the deployed target.

## 14.6.3

- Added stable export of BIND interface diagnostics for supervision and CI integration.
- Added canonical diagnostic schema `dnsforge.bind-interface-diagnostics.v1`.
- Added `dnsforge network export --output <file> [--format json|text]`.

## 14.6.2

- Integrated BIND interface diagnostics into `dnsforge status`.
- Added network topology warnings to `dnsforge doctor`.
- Documented day-two BIND interface observability.
- Preserved NIC-based setup generation and runtime-only IP resolution.

## 14.6.1

- Added `dnsforge network preview` and `dnsforge network audit` to expose NIC-to-IP resolution before BIND rendering or initialize.
- Added structured JSON/text diagnostics for `BIND_EXTRANET_IP`, `BIND_INTRANET_IP`, `BIND_ADMIN_IP`, `DNS_LISTEN_ON`, and `BIND_ADMIN_LISTEN_ON`.
- Preserved NIC-based setup.conf design with no legacy runtime IP aliases.

## 14.6.0

- Added auditable BIND interface resolution metadata.
- Exposed runtime-only `BIND_*_RESOLVED_FROM` keys.
- Exposed `BIND_INTERFACE_AUDIT` for operator support and validation traces.
- Preserved NIC-based setup.conf semantics without legacy IP aliases.

## 14.5.9

- Removed the remaining legacy NIC compatibility aliases `BIND_EXTERNET_NICNAME` and `BIND_EXTERNAL_NICNAME` from runtime resolution.
- Added validator guardrails that reject removed network aliases (`FRONT_IP`, `BACK_IP`, `ADM_IP`, `BIND_EXTERNET_NICNAME`, `BIND_EXTERNAL_NICNAME`) instead of silently accepting ambiguous configuration.
- Hardened runtime BIND listener rendering by deduplicating loopback/admin addresses and always regenerating canonical `BIND_EXTRANET_IP`, `BIND_INTRANET_IP`, `BIND_ADMIN_IP`, `DNS_LISTEN_ON` and `BIND_ADMIN_LISTEN_ON`.
- Added regression tests for complete network alias removal and runtime listener deduplication.

## 14.5.7 - Canonical Resolved BIND Interface IPs

- Added canonical runtime keys `BIND_EXTRANET_IP`, `BIND_INTRANET_IP` and `BIND_ADMIN_IP`.
- Preserved legacy rendered aliases `BIND_EXTRANET_IP`, `BIND_INTRANET_IP` and `BIND_ADMIN_IP` for migration and older templates.
- Kept generated `setup.conf` NIC-based and free from legacy IP variables.
- Updated interface discovery documentation and tests.


## 14.5.6 - BIND Extranet NIC Naming

- Renamed `BIND_EXTERNET_NICNAME` to `BIND_EXTRANET_NICNAME` across generated setup profiles, validators, interface resolution, tests and documentation.
- Kept deprecated `BIND_EXTERNET_NICNAME` as read-only migration compatibility input; generated `setup.conf` now emits only `BIND_EXTRANET_NICNAME`.
- Preserved legacy `BIND_EXTERNAL_NICNAME` compatibility alias where it already existed.

# Changelog

## 14.7.0

### Added
- Configuration Compliance Engine for rendered-versus-deployed BIND configuration verification.
- `dnsforge config fingerprint` to compute stable configuration fingerprints.
- `dnsforge config verify` and `dnsforge config drift` to detect manual drift.
- `dnsforge config baseline show|rebuild` to inspect expected rendered configuration resources.
- `dnsforge config repair --preview` to generate a safe remediation plan without applying changes.

### Changed
- Compliance checks use rendered DNSForge state as the expected baseline and native BIND paths as the deployed target.

## 14.6.3

- Added stable export of BIND interface diagnostics for supervision and CI integration.
- Added canonical diagnostic schema `dnsforge.bind-interface-diagnostics.v1`.
- Added `dnsforge network export --output <file> [--format json|text]`.

## 14.5.8

- Removed legacy rendered IP aliases `FRONT_IP`, `BACK_IP` and `ADM_IP`.
- Runtime BIND rendering now uses only `BIND_EXTRANET_IP`, `BIND_INTRANET_IP` and `BIND_ADMIN_IP`.
- Kept `setup.conf` NIC-based and aligned resolver, validator, documentation and tests with canonical runtime keys.

## 14.5.5 - Distribution-aware setup defaults

- Fix SetupProfileGenerator type aliases without relying on typing.TypeAlias for Python 3.9 compatibility.
- Derive DNSSEC_KEY_DIRECTORY from the detected native BIND layout instead of hard-coding /var/named/dnssec.
- Add BindLayout.dnssec_key_dir for Red Hat, Debian/Ubuntu and SUSE profile generation.
- Keep profile setup resources removed and verify no code consumes dnsforge.infrastructure.profile.resources.

## v14.5.4 - Setup Profile mypy/resource cleanup

- Fix SetupProfileGenerator type aliases for Python 3.9/mypy compatibility.
- Remove obsolete static profile resources from the delivered package.
- Keep setup.conf generation fully dynamic through layered dictionaries.
- Remove package-data declarations for legacy profile resource templates.


## 14.5.2

- Refactored SetupProfileGenerator around five composable setup dictionaries: common_setup, proxy_common_setup, autoritative_setup, hybrid_setup and forwader_setup.
- Preserved generated setup.conf output while removing hard-coded full-line construction from the generator.
- Kept BIND NIC discovery semantics and Bandit-safe implementation intact.

## 14.5.0

- Replaced setup.conf BIND network IP variables with NIC-name variables: BIND_EXTRANET_NICNAME, BIND_INTRANET_NICNAME and BIND_ADMIN_NICNAME.
- Added runtime interface discovery so the DNSForge agent resolves BIND addresses locally and supports one-NIC, two-NIC and three-NIC deployments.
- Added duplicate filtering for generated BIND listen-on and administration bindings.
- Introduced dynamic setup.conf profile generation and updated installation to generate setup.conf from profile policy instead of copying static role files.
- Kept legacy FRONT_IP, BACK_IP and ADM_IP as migration fallbacks without emitting them in new setup.conf files.

## 14.4.0

- Added Agent Trust Policy & Rotation.
- Added policy-driven enrollment evaluation.
- Added auditable token/certificate rotation history.
- Added Manager API and CLI endpoints for trust policies and rotations.
- Kept v14.3.0 Agent Trust Framework APIs backward compatible.

## 14.3.0

### Added

- Agent Trust Framework for DNSForge Manager.
- Explicit DDD aggregates: TrustedAgent, AgentCertificate and EnrollmentRequest.
- Manager trust API endpoints: `/trust/enroll`, `/trust/approve`, `/trust/revoke`, `/trust/rotate-token`.
- Manager CLI commands: `dnsforge-manager trust list`, `enrollments`, `enroll`, `approve`, `revoke`, `rotate-token`.
- JSON trust repository retained as the default persistence adapter.

### Preserved

- DNSForge remains the local BIND management agent.
- DNSForge Manager remains the central orchestrator.
- Central Inventory v14.2.0 remains intact.
- No `dist/` directory is included in release archives.

## 14.2.0 - Central Inventory

- Added Manager Central Inventory as the source of truth for Sites, Clusters, Agents, Environments and Agent Status.
- Added DDD inventory aggregates and application service.
- Added JSON default persistence and optional PostgreSQL persistence for `sites`, `clusters`, `agents`, `environments` and `agent_status`.
- Added Manager API routes under `/inventory/*`.
- Added Manager CLI commands under `dnsforge-manager inventory`.
- Added agent registration metadata and readiness aggregation with READY, WARNING and FAILED states.
- Added Central Inventory and Agent Registration documentation and tests.


## 14.0.0 - Innovation Branch

- Opens the DNSForge 14.x innovation branch.
- Keeps 13.0.x as maintenance-only baseline.
- Adds innovation branch documentation.
- No BIND behavior change in this foundation release.

# Changelog

## 14.7.0

### Added
- Configuration Compliance Engine for rendered-versus-deployed BIND configuration verification.
- `dnsforge config fingerprint` to compute stable configuration fingerprints.
- `dnsforge config verify` and `dnsforge config drift` to detect manual drift.
- `dnsforge config baseline show|rebuild` to inspect expected rendered configuration resources.
- `dnsforge config repair --preview` to generate a safe remediation plan without applying changes.

### Changed
- Compliance checks use rendered DNSForge state as the expected baseline and native BIND paths as the deployed target.

## 14.6.3

- Added stable export of BIND interface diagnostics for supervision and CI integration.
- Added canonical diagnostic schema `dnsforge.bind-interface-diagnostics.v1`.
- Added `dnsforge network export --output <file> [--format json|text]`.

## 14.5.8

- Removed legacy rendered IP aliases `FRONT_IP`, `BACK_IP` and `ADM_IP`.
- Runtime BIND rendering now uses only `BIND_EXTRANET_IP`, `BIND_INTRANET_IP` and `BIND_ADMIN_IP`.
- Kept `setup.conf` NIC-based and aligned resolver, validator, documentation and tests with canonical runtime keys.

## 14.5.5 - Distribution-aware setup defaults

- Fix SetupProfileGenerator type aliases without relying on typing.TypeAlias for Python 3.9 compatibility.
- Derive DNSSEC_KEY_DIRECTORY from the detected native BIND layout instead of hard-coding /var/named/dnssec.
- Add BindLayout.dnssec_key_dir for Red Hat, Debian/Ubuntu and SUSE profile generation.
- Keep profile setup resources removed and verify no code consumes dnsforge.infrastructure.profile.resources.

## 14.0.0 - Maintenance Release Verification

- Added maintenance release verification documentation for the 13.0.x branch.
- Added a release verification gate that confirms GA, operational, platform, upgrade and release-hygiene checks remain wired.
- Kept feature freeze: no DNS, Manager, DNSBeat or DNSSync functional changes.
- Rebuilt distribution artifacts for version 14.0.0.

## 13.0.3 - Maintenance CI Runtime Stabilization

- Removed redundant full pytest execution from CI when the coverage gate already runs the non-live test suite.
- Kept live BIND validation isolated in its dedicated enterprise smoke step.
- Removed duplicated product hardening gate invocations from the workflow.
- Documented the 13.0.x CI runtime strategy.

## 13.0.2 - Maintenance CI Closure

- Keep the 13.0.x maintenance branch under feature freeze.
- Clarify CI coverage closure by separating live BIND smoke validation from the coverage gate.
- Keep live named and generated BIND validation as dedicated enterprise validation steps.
- Preserve the 90% coverage threshold for product code.
- Rebuild distribution artifacts for 13.0.2.

# DNSForge v13.0.0 - Production GA

## 13.0.1 - Maintenance Baseline

- Establishes the 13.0.x maintenance branch baseline after Production GA.
- No functional DNS changes.
- Keeps the GA gates, product gates, release hygiene and platform certification policy intact.
- Adds production maintenance policy documentation.


- Declared DNSForge Production General Availability after operational, platform, upgrade and GA readiness gates.
- Added GA release notes and production GA checklist.
- Kept feature freeze: no new DNS or Manager behavior in this release.
- Rebuilt release artifacts for version 13.0.0.

# DNSForge v12.10.4 - GA Readiness

- Added GA readiness gate.
- Added documentation/code parity checker.
- Added CLI/API parity checker.
- Added conservative dead-code audit gate.
- Added performance baseline documentation.
- Integrated GA readiness into CI and product gate.

# Changelog

## 14.7.0

### Added
- Configuration Compliance Engine for rendered-versus-deployed BIND configuration verification.
- `dnsforge config fingerprint` to compute stable configuration fingerprints.
- `dnsforge config verify` and `dnsforge config drift` to detect manual drift.
- `dnsforge config baseline show|rebuild` to inspect expected rendered configuration resources.
- `dnsforge config repair --preview` to generate a safe remediation plan without applying changes.

### Changed
- Compliance checks use rendered DNSForge state as the expected baseline and native BIND paths as the deployed target.

## 14.6.3

- Added stable export of BIND interface diagnostics for supervision and CI integration.
- Added canonical diagnostic schema `dnsforge.bind-interface-diagnostics.v1`.
- Added `dnsforge network export --output <file> [--format json|text]`.

## 14.5.8

- Removed legacy rendered IP aliases `FRONT_IP`, `BACK_IP` and `ADM_IP`.
- Runtime BIND rendering now uses only `BIND_EXTRANET_IP`, `BIND_INTRANET_IP` and `BIND_ADMIN_IP`.
- Kept `setup.conf` NIC-based and aligned resolver, validator, documentation and tests with canonical runtime keys.

## 14.5.5 - Distribution-aware setup defaults

- Fix SetupProfileGenerator type aliases without relying on typing.TypeAlias for Python 3.9 compatibility.
- Derive DNSSEC_KEY_DIRECTORY from the detected native BIND layout instead of hard-coding /var/named/dnssec.
- Add BindLayout.dnssec_key_dir for Red Hat, Debian/Ubuntu and SUSE profile generation.
- Keep profile setup resources removed and verify no code consumes dnsforge.infrastructure.profile.resources.

## 12.10.3 - Operational Acceptance Sprint 3
- Extended readiness checks with JSON output contract.
- Added Manager node readiness integration.
- Hardened operational readiness gate v2.

## 12.10.2 - Operational Acceptance Sprint 2

- Added operational guide, runbooks, go-live checklist and security baseline.
- Added operational readiness gate.
- Integrated operational readiness into Product Gate and CI.

## 12.10.1 - Operational Readiness Coverage Gate Fix

- Added `dnsforge readiness` as the first operational acceptance command.
- Added DDD readiness domain/application structures with platform, Python, BIND tools, initialization, backup and history checks.
- Added `ReadinessApi` under `dnsforge.interfaces.api` and aligned API coverage contracts.
- Regenerated `docs/COMMANDS.md` from the real CLI parser.

## 12.9.0 - Upgrade & Migration Certification

- Added upgrade/migration certification gates and documentation.


## 12.7.6 - Live Named Runtime Isolation

- Isolated live `named` smoke runtime from host RNDC, statistics, logging, PID and session-key resources.
- Rewrote smoke-test listen ports to non-privileged CI ports while preserving real BIND startup validation.
- Kept distribution-aware BIND layout handling and generated configuration validation intact.

# v12.7.4 - Live Named Smoke Distro Path Fix

- Fixed the live BIND smoke test to derive its relocation root from the rendered distro BindLayout instead of hardcoding /etc/bind.
- The live smoke test now renders the profile for the detected host BIND layout while generated-layout validation still covers RedHat, Debian and SUSE.


## 12.7.4 - Live Named Smoke Distro Path Fix

- Fixed the live BIND smoke test to derive its relocation root from the rendered distro BindLayout instead of hardcoding /etc/bind.
- The test now renders the live profile for the detected host layout while keeping all static generated-layout validations across RedHat, Debian and SUSE.

# v12.7.3 - Live Named Smoke AppArmor Path Fix

- Move the generated live named smoke-test tree under /etc/bind when available so Ubuntu/AppArmor-confined BIND can read the generated configuration.
- Keep POSIX readability/traversal hardening and clean up the temporary tree after the smoke test.
- Preserve the real BIND startup smoke validation without weakening the assertion.

# v12.7.1 - Live Named Smoke Permission Fix

- Fix live named smoke test on sudo-driven CI by making the generated temporary BIND tree traversable/readable before BIND drops privileges.
- Preserve enterprise validation gates without weakening generated BIND checks.


## v12.7.0 - CI Enterprise Validation

- Added enterprise validation gate for real BIND checks, Manager-Agent workflows, disaster recovery, catalog zones, DNSSEC lifecycle and Manager security coverage.
- Added live BIND smoke test support when the named binary is available.
- Added Manager-Agent integration tests proving Manager routes changes through DNSSync and DNSForge Agent clients only.
- Added docs/ENTERPRISE_CI_VALIDATION.md.

# v12.6.1 - Release Hygiene Fix

- Applied Ruff formatting to Manager persistence workflow files.
- Rebuilt release artifacts and preserved Manager persistence behavior.

# v12.6.0 - Manager Persistence & PostgreSQL Readiness

- Added Manager persistence repository boundaries.
- Kept JSON as the default Manager backend.
- Added JSON-backed change request persistence with local locking.
- Added PostgreSQL readiness contracts and schema migrations.
- Added Manager persistence documentation and tests.

# DNSForge v12.5.0 - Manager Operational Workflows

- Added Manager change request lifecycle.
- Added approval/apply/rollback workflow gates.
- Enforced DNSSync dry-run hash and DNSBeat health blocking before apply.
- Preserved DNSForge Agent local-only BIND modification boundary.

# DNSForge v12.4.0 - Coverage Hardening

- Added blocking coverage gate at 90%.
- Extended coverage configuration to include DNSForge Agent and DNSForge Manager.
- Documented coverage measurement policy.
- Updated CI coverage command from 60% to 90%.
- Kept DNS feature freeze; no DNS behavior changes.

## v12.3.2 - Agent DDD Alignment

- Moved DNSForge Agent API facades from `dnsforge.api` to `dnsforge.interfaces.api`.
- Removed the legacy top-level `dnsforge.api` package.
- Updated API coverage tooling, docs and tests to enforce the DDD interface boundary.
- Preserved CLI/API parity and the secure CLI privilege rule.

## v12.3.1 - Manager DDD Cleanup

- Removed legacy Manager facade packages created during the v12.3.0 DDD transition.
- Consolidated Manager imports to canonical DDD paths only: domain, application, infrastructure, interfaces.
- Updated Manager tests and documentation to reject reintroduction of pre-DDD package roots.
- Preserved DNSForge local-agent responsibility and Manager/DNSBeat/DNSSync boundaries.

## v12.3.0 - Manager DDD Refactor

- Refactored DNSForge Manager into DDD layers aligned with the DNSForge agent: domain, application, infrastructure and interfaces.
- Preserved legacy Manager import paths as compatibility facades to avoid regressions.
- Kept DNSBeat and DNSSync as Manager sub-modules while moving their models/use cases into DDD boundaries.
- Added docs/MANAGER_DDD.md.
- Preserved the product boundary: DNSForge agents remain the only components allowed to modify BIND.

## v12.2.0 - Manager Security & Agent Trust

- Added Manager agent trust model with pending approval, fingerprinting, revocation and token rotation.
- Enforced RBAC permissions on Manager node, trust, DNSBeat and audit operations.
- Added Manager audit repository for security-sensitive operations.
- Hardened DNSSync with approved dry-run plan hashes before apply/rollback.
- Kept DNSBeat strictly read-only.
- Added docs/MANAGER_SECURITY.md.

## v12.1.0 - Manager API & Node Lifecycle

- Added Manager API lifecycle foundation.
- Added persistent JSON node inventory backend.
- Added node registration tokens and status lifecycle.
- Added DNSSync dry-run/apply/rollback workflow modes.
- Added DNSBeat node health status fields.
- Added RBAC admin/operator/viewer roles.

## 11.4.0 - Product Hardening & Contract Stabilization

- Added product hardening gates for CLI, API, event, service and release coverage.
- Added stable CLI compatibility documentation and public contract declarations.
- Added centralized output formatter contracts for JSON/table output.
- Added future DNSForge Manager contract scaffolding without changing DNS engine behaviour.
- Preserved the secure CLI privilege rule: every command requires root/sudo except `dnsforge version`.

## 11.3.2 - Secure CLI / Build Tool Separation

- Keep all CLI commands privileged except `dnsforge version`.
- Add `tools/generate_commands_doc.py` for CI/build-time COMMANDS.md generation without invoking the privileged CLI.
- Update release checks to point to the build tool instead of the CLI command.
- Regenerate docs/COMMANDS.md and rebuild distribution artifacts.

## 11.3.1 - Sync Consolidation

- Consolidated sync provider boundaries under `dnsforge.application.sync`.
- Removed duplicate `sync_foundation` application package.
- Kept `dnsforge sync providers` unchanged for CLI compatibility.
- Updated tests and architecture documentation.

## 11.3.0 - Enterprise Operations

- Added local job foundation with `dnsforge job list|show|run|cancel|history`.
- Added `dnsforge health score` for NOC-oriented health scoring.
- Added unified `dnsforge report generate` with JSON, YAML and HTML output.
- Added `dnsforge drift audit` for rendered-vs-target configuration drift detection.
- Added `dnsforge events tail` over the local audit event repository.
- Added metrics and sync provider foundations for DNSBeat and DNSSync preparation.
- Added DNSSEC policy show/apply commands.
- Regenerated command documentation from the CLI parser.

## 11.2.2 - Release Hardening

- Added `tools/release_check.py` to validate version synchronization, generated command documentation, dist artifact naming, and forbidden generated artifacts inside release outputs.
- Added a pre-commit configuration for Ruff formatting/linting and the DNSForge source release gate.
- Extended CI with release consistency checks before and after package build.
- Synchronized `VERSION`, `pyproject.toml`, and `dnsforge.__version__`.

## 11.2.1 - CLI/API Parity Guard

- Added the DNSForge CLI/API parity contract.
- Added `MigrationApi` to the internal API facade.
- Added release tests protecting all local top-level CLI command domains.
- Added a guard ensuring the local CLI dispatcher does not depend on `dnsforge.api`.
- Documented that DNSForge Manager/API layers are optional adapters and cannot replace local CLI operations.

## 11.2.0 - API Foundation

- Added stable internal API facades for zones, DNSSEC, catalog, cluster and disaster recovery.
- Added synchronous EventBus and append-only AuditEventRepository.
- Added docs/API.md and docs/ARCHITECTURE.md for future DNSForge Manager integration.
- Added JSON output support for selected operational commands.
- Regenerated docs/COMMANDS.md from the runtime CLI parser.

## 11.0.5 - Orphan command hardening

## 11.1.2 - Cluster Consistency Hardening

- Hardened `dnsforge cluster audit` with structured audit reports.
- Added `dnsforge cluster audit --format json` for automation and CI/CD consumption.
- Added peer manifest, catalog serial, zone checksum, SOA serial checksum and drift findings to cluster audit output.
- Preserved authoritative-only cluster enforcement and non-zero exit on critical findings.


- Hardened previously shallow security history rollback by replacing the placeholder response with validated rollback markers.
- Added regression coverage for security history, rollback marker creation and invalid rollback references.
- Added backup/restore safety tests for absolute paths, path traversal and safe relative archive members.
- Preserved generated command documentation, transactional proxy migration and release archive hygiene.

## 11.1.1 - Catalog Self-Healing

- Added `dnsforge catalog repair` to self-heal catalog zone publications from active authoritative zones.
- Catalog repair now adds missing catalog members, removes stale members, and rewrites the catalog zone file.
- Added targeted tests for catalog repair and CLI parser alignment.

## 11.1.0 - Production Readiness

- Added generic `FilesystemTransactionManager` for critical filesystem operations.
- Added real BIND validation hooks for deployed trees: `named-checkconf`, `named-checkzone`, `rndc status`, `rndc reload`.
- Added `dnsforge cluster audit` for authoritative cluster consistency checks.
- Added `dnsforge audit zone <zone>` for per-zone integrity checks.
- Added `dnsforge disaster snapshot|restore|verify` for full-node disaster recovery snapshots.
- Added internal `dnsforge.api` facade to prepare DNSForge Manager/API adapters.
- Extended CLI, transaction and disaster recovery tests.

## 11.0.4 - Generated command reference

- Added `dnsforge generate commands-doc` to generate `docs/COMMANDS.md` from the live argparse CLI tree.
- Regenerated `docs/COMMANDS.md` from the code instead of maintaining command inventory manually.
- Extended CLI dispatch alignment tests to cover the documentation generation command.
- Preserved transactional proxy migration introduced in 11.0.3.

## 11.0.2 - CLI alignment and proxy migration deploy

- Audited command parser/dispatcher alignment for exposed CLI forms.
- Enhanced `dnsforge migrate` so proxy-forwarder/proxy-hybrid migration renders and deploys the complete BIND layout for the target proxy mode.
- Added `--target-root` and `--reason` handling for real migrations.
- Added migration regression tests for setup rewrite, render, deploy, dry-run and authoritative refusal.
- Preserved release archive hygiene and `dist/` release artifacts.

## 11.0.1 - Release packaging policy

- Keeps `dist/` in DNSForge release archives after a clean build.
- Adds source/release repository hygiene modes to `tools/clean.py`.
- CI now cleans transient artifacts before build and verifies release artifacts after build.
- Updates packaging policy to exclude caches, build directories and egg metadata while shipping the wheel and source archive.

## 11.0.0 - DNSSync boundary preparation

- Isolated authoritative synchronization logic into `domain/application/infrastructure/sync`.
- Kept `dnsforge cluster diff/sync/peers` as stable orchestration commands.
- Preserved sync manifest, checksum, SOA serial and drift detection behavior.

# DNSForge 10.9.5

## Cluster sync hardening

- Added SHA-256 checksums to authoritative cluster sync manifests.
- Added SOA serial discovery for local zone files.
- Added drift detection for zone checksum and SOA serial checksum mismatches.
- Added PEER_AUTHORITATIVE_ADDRESSES fallback when CLUSTER_PEERS is not set.
- Preserved CI workflow and repository hygiene gates.


- Added repository hygiene gate for Python/build/cache artifacts.
- Fixed catalog zone rendering so generated BIND configuration no longer contains unresolved template placeholders.
- Removed build/cache artifacts from release archive.

# DNSForge 10.9.3

- Added authoritative-only cluster sync commands: `cluster peers`, `cluster diff`, `cluster sync --dry-run`, `cluster sync`.
- Added cluster sync planning and outbound sync manifests.
- Added peer drift detection for zones, DNSSEC state, and peer reachability.
- Preserved CI workflow and removed Python cache artifacts from release tree.

# Changelog

## 14.7.0

### Added
- Configuration Compliance Engine for rendered-versus-deployed BIND configuration verification.
- `dnsforge config fingerprint` to compute stable configuration fingerprints.
- `dnsforge config verify` and `dnsforge config drift` to detect manual drift.
- `dnsforge config baseline show|rebuild` to inspect expected rendered configuration resources.
- `dnsforge config repair --preview` to generate a safe remediation plan without applying changes.

### Changed
- Compliance checks use rendered DNSForge state as the expected baseline and native BIND paths as the deployed target.

## 14.6.3

- Added stable export of BIND interface diagnostics for supervision and CI integration.
- Added canonical diagnostic schema `dnsforge.bind-interface-diagnostics.v1`.
- Added `dnsforge network export --output <file> [--format json|text]`.

## 14.5.8

- Removed legacy rendered IP aliases `FRONT_IP`, `BACK_IP` and `ADM_IP`.
- Runtime BIND rendering now uses only `BIND_EXTRANET_IP`, `BIND_INTRANET_IP` and `BIND_ADMIN_IP`.
- Kept `setup.conf` NIC-based and aligned resolver, validator, documentation and tests with canonical runtime keys.

## 14.5.5 - Distribution-aware setup defaults

- Fix SetupProfileGenerator type aliases without relying on typing.TypeAlias for Python 3.9 compatibility.
- Derive DNSSEC_KEY_DIRECTORY from the detected native BIND layout instead of hard-coding /var/named/dnssec.
- Add BindLayout.dnssec_key_dir for Red Hat, Debian/Ubuntu and SUSE profile generation.
- Keep profile setup resources removed and verify no code consumes dnsforge.infrastructure.profile.resources.

## 12.8.0 - Enterprise CI Matrix Hardening

- Added minimum supported platform certification policy.
- Added platform support gate for RHEL/Rocky/Alma 8+, Ubuntu 22.04+, Debian 10+, and SLES 12+.
- Documented enterprise CI matrix hardening around minimum versions instead of latest-only OS targets.
- Integrated platform support checks into product and enterprise validation gates.

## 12.0.0 - Manager Foundation

- Added DNSForge Manager foundation package.
- Added DNSBeat and DNSSync as Manager sub-modules.
- Added product boundary documentation.
- Preserved DNSForge as the only local BIND execution agent.


## 10.9.2 - Authoritative HA / Keepalived cluster

- Added authoritative-only HA cluster validation for 2+ nodes.
- Added `dnsforge cluster render --reason` and `dnsforge cluster apply --reason`.
- Added Keepalived rendering with VIP, VRID, priority, interface and unicast peers.
- Added `dnsforge audit cluster`.
- Kept proxies outside cluster membership; proxies use peer authoritative addresses.


## 10.9.1 - Distributed topology cleanup

- Replace `AUTHORITATIVE_BACK_IP` with `PEER_AUTHORITATIVE_ADDRESSES`.
- Add `PEER_PROXY_ADDRESSES` for future proxy synchronization.
- Remove obsolete proxy VIP variables from profile templates.
- Restrict cluster governance to authoritative DNS servers only.
- Keep proxy nodes outside the HA cluster model; proxies consume authoritative IP/VIP addresses only.

# 10.8.4

- Added CI zero-skip enforcement with `DNSFORGE_FORBID_SKIPS=1`.
- Added consolidated GitHub Actions quality report.
- Kept local BIND-tool skips for developer workstations without `named-checkconf`/`named-checkzone`.
- Cleaned release build artifacts before wheel generation.

# 10.8.3

- Enforced strict BIND validation tooling in GitHub Actions.
- Local developer runs may still skip BIND validation when `named-checkconf`/`named-checkzone` are absent.
- Added regression coverage ensuring missing BIND tools fail under `GITHUB_ACTIONS=true`.

# Changelog

## 14.7.0

### Added
- Configuration Compliance Engine for rendered-versus-deployed BIND configuration verification.
- `dnsforge config fingerprint` to compute stable configuration fingerprints.
- `dnsforge config verify` and `dnsforge config drift` to detect manual drift.
- `dnsforge config baseline show|rebuild` to inspect expected rendered configuration resources.
- `dnsforge config repair --preview` to generate a safe remediation plan without applying changes.

### Changed
- Compliance checks use rendered DNSForge state as the expected baseline and native BIND paths as the deployed target.

## 14.6.3

- Added stable export of BIND interface diagnostics for supervision and CI integration.
- Added canonical diagnostic schema `dnsforge.bind-interface-diagnostics.v1`.
- Added `dnsforge network export --output <file> [--format json|text]`.

## 14.5.8

- Removed legacy rendered IP aliases `FRONT_IP`, `BACK_IP` and `ADM_IP`.
- Runtime BIND rendering now uses only `BIND_EXTRANET_IP`, `BIND_INTRANET_IP` and `BIND_ADMIN_IP`.
- Kept `setup.conf` NIC-based and aligned resolver, validator, documentation and tests with canonical runtime keys.

## 14.5.5 - Distribution-aware setup defaults

- Fix SetupProfileGenerator type aliases without relying on typing.TypeAlias for Python 3.9 compatibility.
- Derive DNSSEC_KEY_DIRECTORY from the detected native BIND layout instead of hard-coding /var/named/dnssec.
- Add BindLayout.dnssec_key_dir for Red Hat, Debian/Ubuntu and SUSE profile generation.
- Keep profile setup resources removed and verify no code consumes dnsforge.infrastructure.profile.resources.

## 12.8.0 - Enterprise CI Matrix Hardening

- Added minimum supported platform certification policy.
- Added platform support gate for RHEL/Rocky/Alma 8+, Ubuntu 22.04+, Debian 10+, and SLES 12+.
- Documented enterprise CI matrix hardening around minimum versions instead of latest-only OS targets.
- Integrated platform support checks into product and enterprise validation gates.

## 10.8.2
- Require explicit --reason on zone mutating operations.
- Enforce minimum reason length for zone and config changes.
- Add audit detection for legacy zone history entries without a valid reason.

## 10.8.0

- Added node configuration governance for `/etc/dnsforge/setup.conf`.
- Added `dnsforge config show|validate|diff|history|apply|rollback`.
- Added `dnsforge audit config`.
- Added configuration snapshots with mandatory reason for apply/rollback.
- Preserved GitHub CI and wheel packaging.

## 10.7.2

- Added strict zone lifecycle governance: draft -> active -> deprecated -> retired.
- `dnsforge zone create` now defaults to draft lifecycle.
- `dnsforge zone list --enabled` now lists only enabled active zones.
- Added `dnsforge zone retire <zone|--name>` before deletion.
- `dnsforge zone delete` now requires retired lifecycle.
- Added `dnsforge audit zones` for zone governance metadata, lifecycle consistency and reverse coverage checks.
- Preserved canonical history commands: `zone get`, `zone show --version`, `zone diff --from --to`, `zone rollback --version`.

## 10.7.1

- Reconciled zone lifecycle CLI with existing canonical commands.
- Removed inferior duplicate zone restore/history-diff/diff --id forms.
- Preserved canonical commands: zone get --name, zone show --zone --version, zone diff --zone --from --to, zone rollback --zone --version.
- Added zone catalog governance metadata and zone/record search.
- Kept GitHub CI workflow and removed Python cache artifacts from release tree.

## 10.7.0

- Added complete zone lifecycle command set: list --enabled, status, backup, diff --id, history diff, restore --id.
- Kept zone list as the primary zone inventory command.
- Added CLI/parser alignment tests for the complete zone lifecycle.
- Restored GitHub Actions CI workflow preservation.

## 10.6.9

- Added `install/upgrade.sh` for controlled DNSForge upgrades.
- Added `install/uninstall.sh` for safe uninstall and explicit purge flows.
- Added tests for install, upgrade and uninstall entrypoints.
- Ensured BIND packages are never removed unless `--purge --remove-bind` is explicitly requested.
- Removed Python cache artifacts from release trees.


## 10.6.4 - Zone Transaction Engine

- Added atomic zone change planning for forward/reverse mutations.
- Added rollback-on-persistence-failure for zone catalog commits.
- Added post-commit history snapshots only after successful catalog writes.
- Added transaction regression tests for failed commits and forward/reverse consistency.

# 10.6.0

- Split render and deploy as first-class application commands.
- Added `dnsforge deploy` for applying previously rendered native BIND trees.
- `dnsforge initialize` now orchestrates one-shot `backup -> render -> deploy -> lock`.
- Added deploy tests ensuring deployment does not create the initialization lock.

# 10.5.25

- Added advisory `mypy` CI gate.
- Added project-level mypy configuration for Python 3.9+.
- Added typing CI documentation.

# 10.5.0

- Reoriented `dnsforge initialize` as a BIND configuration takeover/deployment command.
- Removed package installation from the Python initialize/configure application service.
- Added complete BIND configuration backup using move + tar.gz before applying rendered files.
- Added BIND prerequisite validation: `named-checkconf`, `rndc`, `systemctl`.
- Made `/etc/dnsforge/setup.conf` the preferred node source of truth, with legacy per-role env files only as fallback.
- Updated initialize documentation to reflect install/ vs initialize responsibilities.

## v10.4

- Ajout commandes sécurité : `security history/rollback`, `acl`, `view`, `dnssec`, `rpz`, `cluster validate-security`.
- Ajout de `docs/SECURITY-COMMANDS.md`.

## v10.3

- `dnsforge configure` devient `dnsforge initialize`.
- Suppression de l'option publique `--skip-install`.
- Installation automatique de BIND via `install/install.sh` si absent.
- Ajout de `LinuxDistribution`, `OsReleaseReader`, `PackageManager`.

## v10.2

- Suppression définitive de `src/libs`.
- Portage des responsabilités Bash vers modules Python natifs.
- Ajout de `BooleanSetting`, `AddressListParser`, `CommandRunner`, `AtomicFileWriter`, `BackupFile`, `ServiceManager`, `BindTools`.
- Ajout de `docs/BASH-LIBS-MIGRATION.md`.

## v10.1

- `dnsforge zone show <zone>` affiche explicitement la version active courante.
- `dnsforge zone show --zone <zone> --version N` affiche une version historique.
- `dnsforge zone history <zone>` indique la version courante.
- Suppression définitive de `src/settings` du livrable.
- Configuration opérateur déportée vers `/etc/dnsforge/setup.conf`.
- Les anciens modèles statiques de profil sont remplacés par la génération dynamique.

## v10.0

- Ajout Zone History / Diff / Rollback.
- Snapshots filesystem automatiques avant modification des zones.
- Commandes `zone history`, `zone show --version`, `zone diff`, `zone rollback`.

## v9.9

- Ajout du domaine `cluster`.
- Ajout de `dnsforge cluster init/status/validate/render/apply/sync`.
- Support proxy cluster avec VIP Keepalived.
- Support authoritative cluster en modèle Primary/Secondary.
- Ajout des variables cluster dans les templates `setup.conf`.
- Ajout de `docs/CLUSTER.md`.

## v9.8

- Ajout de `dnsforge status`.
- Ajout de `dnsforge health`.
- Ajout de `dnsforge doctor`.
- Ajout de `dnsforge backup create/list`.
- Ajout de `dnsforge restore`.
- Ajout de `dnsforge migrate --to proxy-forwarder|proxy-hybrid`.
- Migration lourde proxy <-> authoritative interdite.

## v9.7

- Ajout du domaine `security`.
- Ajout des profils `standard`, `hardened`, `enterprise`, `paranoid`.
- Ajout de `dnsforge security show` et `dnsforge security audit`.
- Injection des options BIND de sécurité : DNS Cookies, RRL, minimal responses, qname minimization, serve-stale.
- Ajout de `docs/SECURITY.md`.

## v9.6

- Ajout de `dnsforge zone show`.
- Ajout de `dnsforge zone edit` avec `--add`, `--update`, `--delete`.
- Ajout du modèle `DnsRecord`.
- Extension du catalogue avec `records`.

## v9.5

- Ajout du modèle `ConfigurationProfile`.
- Ajout de `ProfileSettingsValidator`.
- Ajout de `ProfileAuditor`.
- Ajout de la commande `dnsforge profile audit`.
- Durcissement des règles par profil : authoritative, proxy-forwarder, proxy-hybrid.
- Ajout de `docs/CONFIGURATION-PROFILES.md`.

## v9.4

- Intégration des variables présentes dans `src/settings` dans les templates `setup.conf`.
- Modèles complets par profil : authoritative, proxy-forwarder, proxy-hybrid.
- Le manifeste historique de couverture des variables est remplacé par des tests de génération dynamique.
- Ajout de `docs/SETUP-CONF-TEMPLATES.md`.

## v9.3

- Ajout de `install/install.sh`.
- Installation sous `/opt/dnsforge`.
- Création de `/etc/dnsforge`.
- Création des liens `/opt/dnsforge/settings` et `/opt/dnsforge/src/settings` vers `/etc/dnsforge`.
- Exposition globale de `/usr/local/bin/dnsforge`.
- Ajout des templates `setup.conf` par profil.
- Installation centralisée via `install/install.sh`.
- Ajout de `docs/INSTALLATION.md`.

## v9.2

- Intégration du dossier `build` dans `src/dnsforge/infrastructure/templates`.
- Déplacement du catalogue vers `src/dnsforge/infrastructure/templates/catalog/zones.yml`.
- Mise à jour de `ProjectPaths.build_root` et `ProjectPaths.catalog_file`.
- Suppression de l'ancien dossier `src/dnsforge/infrastructure/templates`.
- Correction du dossier racine dans l'archive ZIP : `ZoneForge-DNSaaS-v9.2`.

## v9.1

- Suppression du répertoire legacy du livrable produit.
- Suppression des derniers helpers legacy du package Python.
- Ajout de la commande `dnsforge audit`.
- Ajout de `ProductAuditor` et `ProductAuditReport`.
- Ajout du guide d'exploitation `docs/OPERATING-GUIDE.md`.
- Durcissement de la cohérence produit Python.

## v9.0

- Finalisation de la bascule produit vers Python.
- Suppression des références Python vers les anciens entrypoints Bash.
- Archivage des anciens scripts Bash sous `legacy/bash/`.
- Nettoyage de `ProjectPaths` pour retirer les helpers legacy.
- Ajout du test `check-dnsforge-product-python.sh`.
- Ajout de la documentation `PYTHON-PRODUCT-V9.md`.

## v8.9

- `dnsforge initialize` devient natif Python.
- Ajout de `ConfigureService`.
- Ajout de `PackageInstaller`, `FileInstaller`, `FirewalldManager`, `SELinuxManager`, `SystemdManager`.
- `configure` n'appelle plus les scripts Bash historiques.
- Les scripts Bash historiques sont déplacés vers `legacy/bash/`.
- Ajout de la documentation `PYTHON-CONFIGURE-NATIVE.md`.

## v8.8

- Ajout de `ConfigurePlan` et `ConfigureStep`.
- Ajout de `ConfigurePlanner`.
- Ajout de l'option `--dry-run` à `dnsforge initialize`.
- `dnsforge initialize --dry-run` produit un plan Python sans exécuter le moteur Bash.
- Documentation `PYTHON-CONFIGURE-PLAN.md`.

## v8.7

- Migration de `dnsforge zone` vers Python natif.
- Ajout du modèle `ZoneDefinition` et `ZoneType`.
- Ajout de l'adaptateur `ZoneCatalog`.
- Ajout des commandes `zone list/get/create/disable/enable/delete`.
- Ajout de la documentation `PYTHON-ZONE-MANAGER.md`.

## v8.6

- Ajout du rendu Python natif via `dnsforge render`.
- Ajout de `BindRenderTree` et `BindConfigFactory`.
- Ajout du modèle `ProxyRenderProfile`.
- Support natif des sorties `forwarder` et `hybrid`.
- Conservation du moteur Bash historique pour `configure`.

## v8.5

- Ajout d'un vrai package Python `src/dnsforge`.
- Suppression du point d’entrée historique `bin/dnsforge`; le wheel expose désormais le console script `dnsforge`.
- Ajout du modèle domaine `DnsRole`, `ProxyType`, `ProxySettings`, `AuthoritativeSettings`.
- Ajout de la validation Python des settings proxy/authoritative.
- Ajout de la commande `configure` en remplacement conceptuel de `deploy`.
- Conservation du moteur Bash existant via une couche legacy contrôlée.
- Ajout de la documentation `docs/PYTHON-MIGRATION.md`.

## v8.2

- README restauré comme document de présentation produit.
- Suppression des sections `Exploitation` et `Validation` du README.
- Ajout de la section `Authors`.
- Maintien du lien vers `docs/index.md` et de l'image d'architecture.

## v8.1

- Ajout des tests qualité documentaire.
- Validation des liens Markdown locaux.
- Validation des en-têtes et pieds de page de la documentation.
- Validation du périmètre produit du README.
- Validation de la structure contextuelle de `docs/index.md`.

## v8.0

- README réécrit comme document de présentation produit.
- Documentation opérationnelle recentrée dans `docs/`.
- `docs/index.md` restructuré par contexte : Présentation, Déploiement, Exploitation, Sécurité, Référence.
- Image d'architecture explicitement référencée dans le README.
- Renommage documentaire `Zone Lifecycle` vers `Gestion des Zones`.
- Références alignées sur `zone-manager.sh`.

## v7.3

- Ajout de `docs/images/zoneforge-dnsaas-architecture.png`.
- Insertion de l’image d’architecture dans le README.

## v7.2


- Suppression de l'ancienne bibliothèque de validation séparée.
- Réalignement des scripts et tests sur `lib-settings-validate.sh`.
- Ajout du test `check-validation-library-consolidation.sh`.
- Ajout de la documentation `VALIDATION-LIBRARY.md`.

## v7.1

- RPZ interdit sur les nœuds `dns-authoritative`.
- Ajout du test `check-rpz-authoritative-forbidden.sh`.
- Ajout du test `check-rpz-authoritative-render-clean.sh`.
- Documentation RPZ alignée sur les bonnes pratiques DNS.
- Checklist production mise à jour.

ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

## v6.5


- Ajout de `src/tools/rndc-secret.sh`.
- `RNDC_KEY_NAME` vaut `rndc-key` par défaut.
- `RNDC_SECRET` est généré automatiquement si absent.
- Suppression de l'obligation de déclarer RNDC dans les settings.
- Ajout de tests de génération et rotation RNDC.

## v6.4

- Remplacement de l’implémentation Python du lifecycle par Bash/AWK.
- Suppression de la dépendance runtime Python pour le CRUD des zones.
- Tests CRUD/disable/enable/delete fiabilisés.

## v6.3

- Ajout de `src/tools/zone-manager.sh`.
- CRUD zone dans le catalogue central.
- Support disable/enable via `disabled_zones`.
- Tests positifs et négatifs du lifecycle.

## v6.2


- Validation stricte proxy et authoritative.
- Tests positifs et négatifs de validation.

## v6.1


- Normalisation universelle des listes.
- `PEER_AUTHORITATIVE_ADDRESSES` et `AUTH_CLUSTER_*_BACK_IP` acceptent espace, virgule et point-virgule.
- Abandon du format tableau Bash pour les listes IP.

## v6.0

- Renommage de `src/inventories/` en `src/settings/`.
- Renommage de `tests/fixtures/inventories/` en `tests/fixtures/settings/`.
- Adaptation des scripts de déploiement.
- Adaptation des tests, runbooks et docs.
- Ajout de `docs/SETTINGS.md`.
- Ajout de `tests/settings/check-settings-layout.sh`.

## v5.9

- Ajout Production Gate.
- Ajout diff live vs rendu.
- Ajout rollback latest.
- Tests de garde-fous de déploiement.

## v5.8

- HA DNS Proxy optionnelle.
- Mode par défaut conservé : DNS1/DNS2 sans VIP.
- Ajout templates Keepalived proxy.
- Ajout healthcheck proxy HA.
- Tests HA proxy optionnelle.

## v5.7

- Ajout des scripts natifs de monitoring.
- Ajout de healthcheck DNS/RNDC/statistics-channel.
- Ajout de collecte `rndc stats`.
- Ajout d'un export métriques texte.
- Ajout timer systemd healthcheck.

## v5.6

- Ajout de la politique DNSSEC enterprise.
- DNSSEC automatique sur zones publiques master du catalogue.
- Tests DNSSEC enterprise templates/render/catalog.
- Runbook DNSSEC zone publique.

## v5.5

- Ajout de `src/dnsforge/infrastructure/templates/catalog/zones.yml`.
- Ajout du générateur de catalogue de zones.
- Génération split-horizon master/secondary/forward.
- Tests catalog generate/render.

## v5.3

- Ajout des ACL par zone.
- Ajout de la vue partner.
- Ajout des zones partner master/secondary/forward.
- Test d'intégration `check-zone-acl-render.sh`.

## v5.2

- Clusters authoritative nommés.
- Routing secondary/forward par cluster.
- Indexation récursive des zones.
- Test d'intégration zone-to-cluster.

## v5.1

- Rendu multi-lignes robuste via Perl pour variables BIND.
- Fixtures et tests d'intégration multi-VIP.
- Validation forwarders, primaries, allow-notify.

## v5.0

- Alignement des paramètres d'inventaire avec le code.
- `PEER_AUTHORITATIVE_ADDRESSES` supporte plusieurs VIP/IPs.
- Ajout de `lib-settings.sh`.
- Rendu BIND multi-forwarders, multi-primaries et multi-allow-notify.
- Ajout des tests d'inventaire.
- Mise à jour de `docs/INVENTORIES.md`.

## v4.9

- Ajout de `backup-binddns.sh`.
- Ajout de `restore-binddns.sh`.
- Ajout de `list-backups.sh`.
- Ajout des tests backup.
- Mise à jour de `BACKUP-RESTORE.md` et `DISASTER-RECOVERY.md`.
- Ajout du runbook backup/restore.

## v4.8

- Retrait de la génération HTML du cycle actif.
- Ajout du socle DNSSEC Enterprise optionnel.
- Ajout des templates DNSSEC policy/options.
- Ajout du template de zone authoritative signée.
- Ajout des tests DNSSEC.
- Mise à jour de `docs/DNSSEC.md`.
- Ajout du runbook `DNSSEC-ROLLOVER.md`.

## v4.7

- Ajout de `src/tools/build-doc-site.sh`.
- Ajout de `src/tools/build-doc-site.py`.
- Ajout du répertoire `site/`.
- Ajout des tests de génération et liens HTML.
- Ajout de `docs/DOC-SITE.md`.
- Ajout du runbook `BUILD-DOC-SITE.md`.

## v4.6

- Ajout du profil systemd hardening pour named.
- Ajout des tests de durcissement.
- Ajout de `docs/HARDENING.md`.
- Ajout du runbook `APPLY-HARDENING.md`.

## v4.5

- Formalisation de la HA DNS Proxy sans VIP.
- Ajout de `docs/DNS-PROXY-HA.md`.
- Ajout du runbook `FAILOVER-PROXY.md`.
- Ajout des tests `tests/proxy-ha/check-proxy-ha-design.sh` et `check-proxy-pair-smoke.sh`.

## v4.4

- Ajout des artefacts Prometheus / Telegraf / Grafana.
- Ajout du rendu `/opt/binddns/monitoring`.
- Ajout des tests monitoring.
- Mise à jour de `docs/MONITORING.md`.
- Ajout du runbook `SETUP-MONITORING.md`.

## v4.3

- Ajout de l'audit de rendu complet.
- Ajout de `tests/render/check-render-settings.sh`.
- Ajout de contrôles des chemins générés.
- Ajout de contrôles anti-placeholders dans `src/render`.
- Ajout de `docs/RENDER-AUDIT.md`.
- Ajout du runbook `RUN-RENDER-AUDIT.md`.

## v4.2

- Correction : `50-rpz.conf.j2` n'est plus orphelin.
- RPZ rendue sous `/etc/named/rpz/50-rpz.conf`.
- RPZ incluse dans la vue récursive interne.
- Ajout des tests `tests/project/check-template-usage.sh`, `check-rpz-coherence.sh`, `check-project-coherence.sh`.
- Ajout de `docs/PROJECT-COHERENCE.md`.

## v4.1

- Ajout de `src/tools/generate-tsig.sh`.
- Ajout de `src/tools/check-secrets.sh`.
- Ajout de la documentation `docs/SECRETS.md`.
- Mise à jour du runbook `ROTATE-TSIG`.
- Ajout du test `check-tsig-tooling.sh`.

## v4.0

- Ajout d'une suite de validation complète.
- Ajout de `tests/run-all.sh`.
- Ajout de contrôles BIND, zones, RPZ, RNDC, SELinux, firewalld, documentation et style.
- Ajout du document `docs/VALIDATION.md`.
- Ajout du runbook `RUNBOOKS/RUN-VALIDATION.md`.

## v3.9.1

- Ajout du support des zones `master` sur les DNS Proxy.
- Les proxys peuvent être autoritaires pour certaines zones locales.
- Ajout de `external/master` et `internal/master` côté proxy.
- Génération automatique des index `master/zones.index.conf`.
- Copie automatique des fichiers `.zone` proxy vers `/var/named/master/...`.
- Documentation et runbooks alignés.

## v3.9

- Industrialisation des zones.
- Génération automatique des `zones.index.conf`.
- Tests `dns-validation`.
- Runbooks `ADD-ZONE` et `REMOVE-ZONE` mis à jour.
- Archive régénérée avec dossier racine `binddns-enterprise-redhat-v3.9`.

# Changelog

## 14.7.0

### Added
- Configuration Compliance Engine for rendered-versus-deployed BIND configuration verification.
- `dnsforge config fingerprint` to compute stable configuration fingerprints.
- `dnsforge config verify` and `dnsforge config drift` to detect manual drift.
- `dnsforge config baseline show|rebuild` to inspect expected rendered configuration resources.
- `dnsforge config repair --preview` to generate a safe remediation plan without applying changes.

### Changed
- Compliance checks use rendered DNSForge state as the expected baseline and native BIND paths as the deployed target.

## 14.6.3

- Added stable export of BIND interface diagnostics for supervision and CI integration.
- Added canonical diagnostic schema `dnsforge.bind-interface-diagnostics.v1`.
- Added `dnsforge network export --output <file> [--format json|text]`.

## 14.5.8

- Removed legacy rendered IP aliases `FRONT_IP`, `BACK_IP` and `ADM_IP`.
- Runtime BIND rendering now uses only `BIND_EXTRANET_IP`, `BIND_INTRANET_IP` and `BIND_ADMIN_IP`.
- Kept `setup.conf` NIC-based and aligned resolver, validator, documentation and tests with canonical runtime keys.

## 14.5.5 - Distribution-aware setup defaults

- Fix SetupProfileGenerator type aliases without relying on typing.TypeAlias for Python 3.9 compatibility.
- Derive DNSSEC_KEY_DIRECTORY from the detected native BIND layout instead of hard-coding /var/named/dnssec.
- Add BindLayout.dnssec_key_dir for Red Hat, Debian/Ubuntu and SUSE profile generation.
- Keep profile setup resources removed and verify no code consumes dnsforge.infrastructure.profile.resources.

## 12.8.0 - Enterprise CI Matrix Hardening

- Added minimum supported platform certification policy.
- Added platform support gate for RHEL/Rocky/Alma 8+, Ubuntu 22.04+, Debian 10+, and SLES 12+.
- Documented enterprise CI matrix hardening around minimum versions instead of latest-only OS targets.
- Integrated platform support checks into product and enterprise validation gates.

## 10.8.2
- Require explicit --reason on zone mutating operations.
- Enforce minimum reason length for zone and config changes.
- Add audit detection for legacy zone history entries without a valid reason.

## 10.7.2

- Added strict zone lifecycle governance: draft -> active -> deprecated -> retired.
- `dnsforge zone create` now defaults to draft lifecycle.
- `dnsforge zone list --enabled` now lists only enabled active zones.
- Added `dnsforge zone retire <zone|--name>` before deletion.
- `dnsforge zone delete` now requires retired lifecycle.
- Added `dnsforge audit zones` for zone governance metadata, lifecycle consistency and reverse coverage checks.
- Preserved canonical history commands: `zone get`, `zone show --version`, `zone diff --from --to`, `zone rollback --version`.

## v3.6 complete

- Documentation complète avec `docs/index.md`.
- Liens retour vers l'index en tête et fin de document.
- Scripts de déploiement proxy et authoritative.
- Librairies communes : logging, rendu, validation, permissions, SELinux, firewall, bind.
- Templates BIND formatés et lisibles.
- Inventaires séparés par rôle.
- Tests smoke, validation, style et documentation.
- Mode ``.
- Modes `--dry-run`, `--render-only`, `--validate-only`, `--audit`, `--rollback latest`.


---

Copyright
© IRIVEN Group — All Rights Reserved

## v10.5.4 - Native BIND layout ownership

- Aligned DNSForge initialize with the product model: BIND deployment and complete BIND configuration management.
- Added OS-aware native BIND layout detection for Red Hat family, Debian/Ubuntu and SUSE.
- Removed runtime dependency on `/etc/dnsforge/generated/` and `/var/lib/dnsforge/`.
- Rendered modular BIND configuration into native layout paths: `/etc/named`, `/etc/bind`, `/var/named`, `/var/lib/bind`, `/var/lib/named`.
- Backup now moves the detected native BIND configuration and data paths before creating the tar.gz archive.
- Validation now targets the detected native `named.conf`.
- Systemd operations now use `named` or `bind9` according to the detected platform.
- Added native BIND layout tests.

## 10.9.0 - Catalog Zones Enterprise & Cluster Sync Foundation

- Added `dnsforge catalog status`.
- Added `dnsforge catalog enable --reason`.
- Added `dnsforge catalog disable --reason`.
- Added `dnsforge catalog sync --reason`.
- Added `dnsforge catalog list`.
- Added `dnsforge catalog validate`.
- Added `dnsforge audit catalog`.
- Added catalog state repository and publication service.
- Catalog sync now publishes active eligible zones only.
- Catalog mutations require Enterprise change reason.
- Catalog zone rendering uses the native BIND layout.
