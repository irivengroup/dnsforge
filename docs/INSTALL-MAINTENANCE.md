# DNSForge install maintenance

DNSForge exposes three installation maintenance entrypoints:

```bash
sudo ./install/install.sh --profile authoritative
sudo ./install/upgrade.sh --source
sudo ./install/uninstall.sh
```

## Upgrade

Source-tree upgrade:

```bash
sudo ./install/upgrade.sh --source
```

Wheel upgrade:

```bash
sudo ./install/upgrade.sh --wheel dist/dnsforge-<version>-py3-none-any.whl
```

The upgrade script creates a backup under `/var/backups/dnsforge/upgrade/` before replacing the installed product.
It does not modify `/etc/dnsforge/setup.conf` except by backing it up.

## Uninstall

Default mode removes DNSForge binaries only and keeps:

- `/etc/dnsforge`
- native BIND configuration and data
- BIND packages
- DNSForge backups

```bash
sudo ./install/uninstall.sh
```

Purge mode removes DNSForge configuration after a final backup:

```bash
sudo ./install/uninstall.sh --purge
```

BIND packages are never removed unless explicitly requested:

```bash
sudo ./install/uninstall.sh --purge --remove-bind
```
