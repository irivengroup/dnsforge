# DNSForge v14.4.0 — Agent Trust Policy & Rotation

DNSForge Manager extends the v14.3.0 Agent Trust Framework with policy-driven enrollment evaluation and auditable rotation history.

## Domain objects

- `AgentTrustPolicy`: enrollment constraints for profiles, sites and public key requirements.
- `AgentRotationRecord`: immutable audit trail for token and certificate rotations.

## Manager API

- `GET /trust/policies`
- `POST /trust/policies`
- `POST /trust/policies/evaluate`
- `GET /trust/rotations`
- `POST /trust/rotate-certificate`

Existing v14.3.0 APIs remain supported:

- `GET /trust/enrollments`
- `GET /trust/agents`
- `POST /trust/enroll`
- `POST /trust/approve`
- `POST /trust/revoke`
- `POST /trust/rotate-token`

## Manager CLI

```bash
dnsforge-manager trust policies
dnsforge-manager trust create-policy --policy-id authoritative-emea \
  --allowed-profile authoritative \
  --allowed-site emea \
  --require-public-key
dnsforge-manager trust rotations
dnsforge-manager trust rotate-certificate --fingerprint <fingerprint> --public-key <public-key>
```

## Security guarantees

- Stored tokens are never exposed by list operations.
- Rotation history stores token digests only, never clear tokens.
- Revoked agents cannot rotate tokens or certificates.
- JSON remains the default backend; PostgreSQL remains optional.
