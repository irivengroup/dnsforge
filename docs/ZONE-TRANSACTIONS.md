# DNSForge Zone Transaction Engine

DNSForge applies zone mutations through an atomic change plan.

A single user action can affect several DNS artifacts. For example, adding an
`A` or `AAAA` record to a forward zone can create or update the matching reverse
zone and `PTR` record. DNSForge therefore prepares the full change in memory,
validates the resulting catalog, then commits once.

## Guarantees

- Forward and reverse changes are committed together.
- No partial catalog write is left behind when validation fails.
- A failed persistence attempt restores the previous catalog state.
- History snapshots are created only after a successful commit.
- Managed reverse zones are deleted automatically when their last managed `PTR`
  is removed.

## Impacted operations

- `dnsforge zone create`
- `dnsforge zone edit --add`
- `dnsforge zone edit --update`
- `dnsforge zone edit --delete`
- `dnsforge zone delete`

The transaction engine does not weaken DNS validation. Every resulting zone is
validated through the DNSForge zone policy matrix before it is persisted.
