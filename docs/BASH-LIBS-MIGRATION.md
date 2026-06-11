ZoneForge DNSaaS
Plateforme de Déploiement et de Configuration DNS as a Service

# Migration des anciennes libs Bash

Depuis v10.2, `src/libs` est supprimé.

Modules Python de remplacement :

```text
src/dnsforge/domain/settings/boolean.py
src/dnsforge/infrastructure/bind/bind_tools.py
src/dnsforge/infrastructure/network/address_parser.py
src/dnsforge/infrastructure/runtime/command_runner.py
src/dnsforge/infrastructure/runtime/file_ops.py
src/dnsforge/infrastructure/system/service_manager.py
```

## Ancien inventaire détecté
- `src/libs/lib-bind.sh` : install_bind_packages, install_keepalived_package
- `src/libs/lib-firewall.sh` : is_firewalld_active, configure_proxy_firewall, configure_authoritative_firewall
- `src/libs/lib-inventory.sh` : normalize_authoritative_back_ips, normalize_authoritative_clusters, validate_settings_no_legacy_placeholders, validate_inventory_no_legacy_placeholders
- `src/libs/lib-logging.sh` : log_info, log_ok, log_warn, log_error
- `src/libs/lib-network.sh` : normalize_list, is_ipv4, validate_ip_list, build_bind_ip_list, build_bind_tsig_list
- `src/libs/lib-permissions.sh` : apply_bind_permissions
- `src/libs/lib-render.sh` : render_file, render_common_proxy, render_common_authoritative, render_monitoring_assets, render_hardening_assets, render_dnssec_assets, render_proxy_ha_assets
- `src/libs/lib-rndc.sh` : rndc_default_key_name, generate_rndc_secret_value, rndc_secret_file_for_node, ensure_rndc_secret, rotate_rndc_secret
- `src/libs/lib-selinux.sh` : apply_selinux_contexts
- `src/libs/lib-settings-validate.sh` : settings_fatal, require_setting, reject_placeholder_setting, require_ipv4_setting, require_ipv4_cidr_or_ipv4_setting, require_ip_list_setting, require_secret_setting, validate_boolean_setting, validate_role_setting, validate_dns_proxy_settings_strict, validate_dns_authoritative_settings_strict, require_var, validate_common_inventory, validate_proxy_inventory, validate_authoritative_inventory, validate_rendered_config
- `src/libs/lib-zone-index.sh` : generate_zone_index, copy_zone_data_files, generate_proxy_zone_indexes, generate_authoritative_zone_indexes

---
Copyright
© IRIVEN Group — All Rights Reserved
