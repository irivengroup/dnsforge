# DNSForge Zone Template Registry

DNSForge renders zone declarations through a strict registry keyed by:

```text
(server_profile, scope/view, zone_type)
```

Supported profiles:

- `authoritative`
- `proxy-forwarder`
- `proxy-hybrid`

Supported scopes:

- `internal`
- `external`

Supported zone types are defined in `ZoneType`:

- `master`
- `secondary`
- `stub`
- `forward`
- `hint`
- `rpz`
- `catalog`
- `reverse-master`
- `reverse-secondary`

The allowed combinations are enforced by:

```text
src/dnsforge/domain/zone/policy_validator.py
```

The template registry is enforced by:

```text
src/dnsforge/domain/zone/template_registry.py
```

Template files live under:

```text
src/dnsforge/infrastructure/bind/resources/zones/<profile>/<scope>/<zone_type>.conf.tpl
```

Any zone template file must be registered. Any registered zone template must match an allowed policy combination.

Invalid combinations, such as `master` on a `proxy-forwarder` profile or `rpz` in the `external` scope, are rejected before rendering or persistence.
