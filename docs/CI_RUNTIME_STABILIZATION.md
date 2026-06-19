# DNSForge 13.0.x CI Runtime Stabilization

DNSForge 13.0.x is a maintenance branch. The CI must remain blocking, but it must avoid running the same expensive test surface multiple times.

## Policy

The workflow keeps three distinct validation surfaces:

1. Static and product gates: Ruff, MyPy, Bandit, release gates, product gates and GA gates.
2. Non-live pytest coverage gate: all non-live tests with coverage enforcement at `90%`.
3. Enterprise live BIND smoke tests: generated BIND configuration validation and live `named` startup checks.

The live BIND tests are intentionally isolated from coverage. They depend on host BIND packages, runtime permissions and local confinement profiles, while the coverage gate measures deterministic Python product behavior.

## Maintenance rule

No DNS feature may be added in the 13.0.x branch. CI changes must only improve reliability, determinism or runtime without lowering gates.
