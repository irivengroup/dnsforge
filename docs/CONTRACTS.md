# DNSForge Public Contracts

DNSForge v11.4.0 introduces explicit contracts used by the future DNSForge Manager and companion products.

## API contract

The public API contract is declared in `dnsforge.contracts.api_contracts` and maps functional domains to internal API facades.

## Event contract

The required event contract is declared in `dnsforge.contracts.event_contracts`. Critical operations must publish stable event names for DNSBeat, DNSSync and DNSForge Manager integrations.

## RBAC contract

RBAC definitions start in `dnsforge.contracts.rbac_contracts`. They are contract-only in v11.4.0 and contain no authentication or authorization engine yet.
