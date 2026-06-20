# DNSForge v14.3.0 Agent Trust Framework

DNSForge Manager is the source of truth for agent trust while DNSForge remains the local BIND management agent.

## Domain aggregates

- `EnrollmentRequest`: pending agent onboarding request.
- `AgentCertificate`: certificate metadata and fingerprint binding.
- `TrustedAgent`: approved or revoked agent trust record.

## API

- `GET /trust/enrollments`
- `GET /trust/agents`
- `POST /trust/enroll`
- `POST /trust/approve`
- `POST /trust/revoke`
- `POST /trust/rotate-token`

## CLI

```bash
dnsforge-manager trust enroll --hostname dns01 --version 14.3.0 --profile authoritative --public-key '<pem>' --site emea --cluster c1
dnsforge-manager trust enrollments
dnsforge-manager trust approve --request-id <request-id>
dnsforge-manager trust list
dnsforge-manager trust revoke --fingerprint <fingerprint>
dnsforge-manager trust rotate-token --fingerprint <fingerprint>
```

## Security invariants

- Agents start as pending enrollment requests.
- Approval creates a trusted agent and returns a one-time token to the caller.
- Stored agent tokens are not exposed through list operations.
- Revocation removes the active token and marks the certificate as revoked.
- Token rotation is forbidden for revoked trusted agents.
