# DNSForge Platform Support

DNSForge uses a minimum supported platform policy. The goal is to certify enterprise baseline versions rather than only the latest distribution releases.

## Minimum supported platforms

| Family | Minimum supported version | Notes |
| --- | --- | --- |
| RHEL / Rocky / Alma | 8+ | Red Hat compatible BIND layout and service model. |
| Ubuntu | 22.04 LTS+ | Debian-family BIND layout under `/etc/bind`. |
| Debian | 10+ | Debian-family BIND layout under `/etc/bind`. |
| SUSE / SLES | 12+ | SUSE-family BIND layout and service model. |

## Certification principle

The CI and release gates must validate the minimum platform contract as a product policy. Concrete runners may use containers, vendor images, or dedicated enterprise runners, but the supported baseline remains:

- RHEL / Rocky / Alma 8+
- Ubuntu 22.04 LTS+
- Debian 10+
- SUSE / SLES 12+

## DNSForge responsibility

DNSForge Agent remains responsible for local BIND deployment, validation, rendering, rollback and runtime checks on each managed server. DNSForge Manager, DNSBeat and DNSSync do not modify BIND files directly.
