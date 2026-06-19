# DNSForge Commands

Generated from the DNSForge CLI parser. Do not edit command entries manually.

## Global syntax

```bash
dnsforge [--project-root PROJECT_ROOT] <command> [options]
```

## Command inventory

### `dnsforge acl add-network`

```bash
dnsforge acl add-network [-h] name network
```

Options:

- `name` required:
- `network` required:

### `dnsforge acl create`

```bash
dnsforge acl create [-h] name
```

Options:

- `name` required:

### `dnsforge acl delete`

```bash
dnsforge acl delete [-h] name
```

Options:

- `name` required:

### `dnsforge acl list`

```bash
dnsforge acl list [-h]
```

### `dnsforge acl remove-network`

```bash
dnsforge acl remove-network [-h] name network
```

Options:

- `name` required:
- `network` required:

### `dnsforge acl show`

```bash
dnsforge acl show [-h] name
```

Options:

- `name` required:

### `dnsforge audit`

```bash
dnsforge audit [-h] [--strict] {zones,config,catalog,cluster,zone} ...
```

Options:

- `--strict`:

### `dnsforge audit catalog`

```bash
dnsforge audit catalog [-h]
```

### `dnsforge audit cluster`

```bash
dnsforge audit cluster [-h]
```

### `dnsforge audit config`

```bash
dnsforge audit config [-h]
```

### `dnsforge audit zone`

```bash
dnsforge audit zone [-h] name
```

Options:

- `name` required:

### `dnsforge audit zones`

```bash
dnsforge audit zones [-h]
```

### `dnsforge backup create`

```bash
dnsforge backup create [-h] [--setup-file SETUP_FILE] [--dry-run]
```

Options:

- `--setup-file SETUP_FILE` default='/etc/dnsforge/setup.conf':
- `--dry-run`:

### `dnsforge backup list`

```bash
dnsforge backup list [-h]
```

### `dnsforge catalog disable`

```bash
dnsforge catalog disable [-h] --reason REASON
```

Options:

- `--reason REASON` required:

### `dnsforge catalog enable`

```bash
dnsforge catalog enable [-h] --reason REASON
```

Options:

- `--reason REASON` required:

### `dnsforge catalog list`

```bash
dnsforge catalog list [-h] [--format {text,json}]
```

Options:

- `--format FORMAT` default='text' choices=text,json:

### `dnsforge catalog repair`

```bash
dnsforge catalog repair [-h] --reason REASON
```

Options:

- `--reason REASON` required:

### `dnsforge catalog status`

```bash
dnsforge catalog status [-h] [--format {text,json}]
```

Options:

- `--format FORMAT` default='text' choices=text,json:

### `dnsforge catalog sync`

```bash
dnsforge catalog sync [-h] --reason REASON
```

Options:

- `--reason REASON` required:

### `dnsforge catalog validate`

```bash
dnsforge catalog validate [-h]
```

### `dnsforge cluster apply`

```bash
dnsforge cluster apply [-h] [--setup-file SETUP_FILE] --reason REASON
                              [--dry-run]
```

Options:

- `--setup-file SETUP_FILE`:
- `--reason REASON` required:
- `--dry-run`:

### `dnsforge cluster audit`

```bash
dnsforge cluster audit [-h] [--setup-file SETUP_FILE]
                              [--format {text,json}]
```

Options:

- `--setup-file SETUP_FILE`:
- `--format FORMAT` default='text' choices=text,json:

### `dnsforge cluster diff`

```bash
dnsforge cluster diff [-h] [--setup-file SETUP_FILE]
```

Options:

- `--setup-file SETUP_FILE`:

### `dnsforge cluster init`

```bash
dnsforge cluster init [-h] [--setup-file SETUP_FILE] [--dry-run]
```

Options:

- `--setup-file SETUP_FILE`:
- `--dry-run`:

### `dnsforge cluster peers`

```bash
dnsforge cluster peers [-h] [--setup-file SETUP_FILE]
```

Options:

- `--setup-file SETUP_FILE`:

### `dnsforge cluster render`

```bash
dnsforge cluster render [-h] [--setup-file SETUP_FILE] --reason REASON
                               [--dry-run]
```

Options:

- `--setup-file SETUP_FILE`:
- `--reason REASON` required:
- `--dry-run`:

### `dnsforge cluster status`

```bash
dnsforge cluster status [-h] [--setup-file SETUP_FILE]
```

Options:

- `--setup-file SETUP_FILE`:

### `dnsforge cluster sync`

```bash
dnsforge cluster sync [-h] [--setup-file SETUP_FILE] --reason REASON
                             [--dry-run]
```

Options:

- `--setup-file SETUP_FILE`:
- `--reason REASON` required:
- `--dry-run`:

### `dnsforge cluster validate`

```bash
dnsforge cluster validate [-h] [--setup-file SETUP_FILE]
```

Options:

- `--setup-file SETUP_FILE`:

### `dnsforge cluster validate-security`

```bash
dnsforge cluster validate-security [-h] [--setup-file SETUP_FILE]
```

Options:

- `--setup-file SETUP_FILE`:

### `dnsforge config apply`

```bash
dnsforge config apply [-h] --reason REASON [--dry-run]
```

Options:

- `--reason REASON` required:
- `--dry-run`:

### `dnsforge config diff`

```bash
dnsforge config diff [-h] [--id ID] [--id1 ID1] [--id2 ID2]
```

Options:

- `--id ID`:
- `--id1 ID1`:
- `--id2 ID2`:

### `dnsforge config history`

```bash
dnsforge config history [-h]
```

### `dnsforge config rollback`

```bash
dnsforge config rollback [-h] --id ID --reason REASON [--dry-run]
```

Options:

- `--id ID` required:
- `--reason REASON` required:
- `--dry-run`:

### `dnsforge config show`

```bash
dnsforge config show [-h]
```

### `dnsforge config validate`

```bash
dnsforge config validate [-h]
```

### `dnsforge deploy`

```bash
dnsforge deploy [-h] [--target-root TARGET_ROOT] [--dry-run]
                       {proxy,authoritative} ...
```

Options:

- `--target-root TARGET_ROOT` default='/':
- `--dry-run`:

### `dnsforge deploy authoritative`

```bash
dnsforge deploy authoritative [-h] [--target-root TARGET_ROOT]
                                     [--dry-run]
                                     [node]
```

Options:

- `node`:
- `--target-root TARGET_ROOT`:
- `--dry-run`:

### `dnsforge deploy proxy`

```bash
dnsforge deploy proxy [-h] [--type {forwarder,hybrid}]
                             [--target-root TARGET_ROOT] [--dry-run]
                             [node]
```

Options:

- `node`:
- `--type PROXY_TYPE` choices=forwarder,hybrid:
- `--target-root TARGET_ROOT`:
- `--dry-run`:

### `dnsforge disaster restore`

```bash
dnsforge disaster restore [-h] --snapshot SNAPSHOT [--dry-run]
```

Options:

- `--snapshot SNAPSHOT` required:
- `--dry-run`:

### `dnsforge disaster snapshot`

```bash
dnsforge disaster snapshot [-h] --reason REASON
```

Options:

- `--reason REASON` required:

### `dnsforge disaster verify`

```bash
dnsforge disaster verify [-h] --snapshot SNAPSHOT
```

Options:

- `--snapshot SNAPSHOT` required:

### `dnsforge dnssec check-expiry`

```bash
dnsforge dnssec check-expiry [-h] [--warn-days WARN_DAYS]
```

Options:

- `--warn-days WARN_DAYS` default=30:

### `dnsforge dnssec disable`

```bash
dnsforge dnssec disable [-h] --zone ZONE --reason REASON
```

Options:

- `--zone ZONE` required:
- `--reason REASON` required:

### `dnsforge dnssec enable`

```bash
dnsforge dnssec enable [-h] --zone ZONE --reason REASON
```

Options:

- `--zone ZONE` required:
- `--reason REASON` required:

### `dnsforge dnssec policy apply`

```bash
dnsforge dnssec policy apply [-h]
                                    [--zsk-rotation-days ZSK_ROTATION_DAYS]
                                    [--ksk-rotation-days KSK_ROTATION_DAYS]
```

Options:

- `--zsk-rotation-days ZSK_ROTATION_DAYS` default=30:
- `--ksk-rotation-days KSK_ROTATION_DAYS` default=365:

### `dnsforge dnssec policy show`

```bash
dnsforge dnssec policy show [-h]
```

### `dnsforge dnssec rotate-ksk`

```bash
dnsforge dnssec rotate-ksk [-h] --zone ZONE --reason REASON
```

Options:

- `--zone ZONE` required:
- `--reason REASON` required:

### `dnsforge dnssec rotate-zsk`

```bash
dnsforge dnssec rotate-zsk [-h] --zone ZONE --reason REASON
```

Options:

- `--zone ZONE` required:
- `--reason REASON` required:

### `dnsforge dnssec sign`

```bash
dnsforge dnssec sign [-h] --zone ZONE --reason REASON
```

Options:

- `--zone ZONE` required:
- `--reason REASON` required:

### `dnsforge dnssec status`

```bash
dnsforge dnssec status [-h] [--zone ZONE]
```

Options:

- `--zone ZONE`:

### `dnsforge dnssec validate`

```bash
dnsforge dnssec validate [-h] [--zone ZONE]
```

Options:

- `--zone ZONE`:

### `dnsforge doctor`

```bash
dnsforge doctor [-h] [--setup-file SETUP_FILE]
```

Options:

- `--setup-file SETUP_FILE` default='/etc/dnsforge/setup.conf':

### `dnsforge drift audit`

```bash
dnsforge drift audit [-h] [--target-root TARGET_ROOT]
```

Options:

- `--target-root TARGET_ROOT` default='/':

### `dnsforge events tail`

```bash
dnsforge events tail [-h] [--limit LIMIT] [--category CATEGORY]
```

Options:

- `--limit LIMIT` default=20:
- `--category CATEGORY`:

### `dnsforge generate commands-doc`

```bash
dnsforge generate commands-doc [-h] [--output OUTPUT]
```

Options:

- `--output OUTPUT` default='docs/COMMANDS.md':

### `dnsforge health`

```bash
dnsforge health [-h] [--setup-file SETUP_FILE] {score} ...
```

Options:

- `--setup-file SETUP_FILE` default='/etc/dnsforge/setup.conf':

### `dnsforge health score`

```bash
dnsforge health score [-h] [--format {text,json}]
```

Options:

- `--format FORMAT` default='text' choices=text,json:

### `dnsforge initialize`

```bash
dnsforge initialize [-h] [--render-only] [--apply] [--dry-run]
```

Options:

- `--render-only`:
- `--apply`: Apply a previously rendered DNSForge BIND configuration
- `--dry-run`:

### `dnsforge job cancel`

```bash
dnsforge job cancel [-h] job_id
```

Options:

- `job_id` required:

### `dnsforge job history`

```bash
dnsforge job history [-h]
```

### `dnsforge job list`

```bash
dnsforge job list [-h]
```

### `dnsforge job run`

```bash
dnsforge job run [-h] [--dry-run] job_id
```

Options:

- `job_id` required:
- `--dry-run`:

### `dnsforge job show`

```bash
dnsforge job show [-h] job_id
```

Options:

- `job_id` required:

### `dnsforge metrics show`

```bash
dnsforge metrics show [-h]
```

### `dnsforge migrate`

```bash
dnsforge migrate [-h] --to {proxy-forwarder,proxy-hybrid}
                        [--setup-file SETUP_FILE] [--target-root TARGET_ROOT]
                        [--reason REASON] [--dry-run]
```

Options:

- `--to TARGET` required choices=proxy-forwarder,proxy-hybrid:
- `--setup-file SETUP_FILE` default='/etc/dnsforge/setup.conf':
- `--target-root TARGET_ROOT` default='/':
- `--reason REASON`:
- `--dry-run`:

### `dnsforge profile audit`

```bash
dnsforge profile audit [-h]
```

### `dnsforge readiness`

```bash
dnsforge readiness [-h] [--format {text,json}]
```

Options:

- `--format FORMAT` default='text' choices=text,json:

### `dnsforge render`

```bash
dnsforge render [-h] {proxy,authoritative} ...
```

### `dnsforge render authoritative`

```bash
dnsforge render authoritative [-h] [node]
```

Options:

- `node`:

### `dnsforge render proxy`

```bash
dnsforge render proxy [-h] [--type {forwarder,hybrid}] [node]
```

Options:

- `node`:
- `--type PROXY_TYPE` choices=forwarder,hybrid:

### `dnsforge report generate`

```bash
dnsforge report generate [-h] [--format {json,yaml,html}]
                                [--output OUTPUT]
```

Options:

- `--format FORMAT` default='json' choices=json,yaml,html:
- `--output OUTPUT`:

### `dnsforge restore`

```bash
dnsforge restore [-h] --backup BACKUP [--target-root TARGET_ROOT]
                        [--dry-run]
```

Options:

- `--backup BACKUP` required:
- `--target-root TARGET_ROOT` default='/':
- `--dry-run`:

### `dnsforge rpz enable`

```bash
dnsforge rpz enable [-h]
```

### `dnsforge rpz status`

```bash
dnsforge rpz status [-h]
```

### `dnsforge rpz test`

```bash
dnsforge rpz test [-h] domain
```

Options:

- `domain` required:

### `dnsforge rpz update`

```bash
dnsforge rpz update [-h]
```

### `dnsforge security audit`

```bash
dnsforge security audit [-h]
```

### `dnsforge security history`

```bash
dnsforge security history [-h]
```

### `dnsforge security rollback`

```bash
dnsforge security rollback [-h] [--version VERSION]
```

Options:

- `--version VERSION`:

### `dnsforge security show`

```bash
dnsforge security show [-h]
```

### `dnsforge status`

```bash
dnsforge status [-h] [--setup-file SETUP_FILE] [--format {text,json}]
```

Options:

- `--setup-file SETUP_FILE` default='/etc/dnsforge/setup.conf':
- `--format FORMAT` default='text' choices=text,json:

### `dnsforge sync providers`

```bash
dnsforge sync providers [-h]
```

### `dnsforge validate`

```bash
dnsforge validate [-h] {proxy,authoritative} ...
```

### `dnsforge validate authoritative`

```bash
dnsforge validate authoritative [-h] [node]
```

Options:

- `node`:

### `dnsforge validate proxy`

```bash
dnsforge validate proxy [-h] [--type {forwarder,hybrid}] [node]
```

Options:

- `node`:
- `--type PROXY_TYPE` choices=forwarder,hybrid:

### `dnsforge version`

```bash
dnsforge version [-h]
```

### `dnsforge view attach-zone`

```bash
dnsforge view attach-zone [-h] name zone
```

Options:

- `name` required:
- `zone` required:

### `dnsforge view create`

```bash
dnsforge view create [-h] name
```

Options:

- `name` required:

### `dnsforge view delete`

```bash
dnsforge view delete [-h] name
```

Options:

- `name` required:

### `dnsforge view list`

```bash
dnsforge view list [-h]
```

### `dnsforge zone backup`

```bash
dnsforge zone backup [-h] --reason REASON name
```

Options:

- `name` required:
- `--reason REASON` required:

### `dnsforge zone create`

```bash
dnsforge zone create [-h] [--name ZONE_NAME]
                            [--type {master,secondary,stub,forward,hint,rpz,catalog,reverse-master,reverse-secondary}]
                            [--views VIEWS]
                            [--profile {authoritative,proxy-forwarder,proxy-hybrid}]
                            [--cluster CLUSTER] [--description DESCRIPTION]
                            [--business-owner BUSINESS_OWNER]
                            [--technical-owner TECHNICAL_OWNER]
                            [--environment ENVIRONMENT]
                            [--classification CLASSIFICATION]
                            [--state {draft,active,deprecated,retired}]
                            [--disabled] --reason REASON
                            [name]
```

Options:

- `name`:
- `--name ZONE_NAME`:
- `--type ZONE_TYPE` default='master' choices=master,secondary,stub,forward,hint,rpz,catalog,reverse-master,reverse-secondary:
- `--views VIEWS` default='internal':
- `--profile PROFILE` default='authoritative' choices=authoritative,proxy-forwarder,proxy-hybrid:
- `--cluster CLUSTER`:
- `--description DESCRIPTION` default='':
- `--business-owner BUSINESS_OWNER` default='':
- `--technical-owner TECHNICAL_OWNER` default='':
- `--environment ENVIRONMENT` default='':
- `--classification CLASSIFICATION` default='':
- `--state STATE` default='draft' choices=draft,active,deprecated,retired:
- `--disabled`:
- `--reason REASON` required:

### `dnsforge zone delete`

```bash
dnsforge zone delete [-h] [--name ZONE_NAME] --reason REASON [name]
```

Options:

- `name`:
- `--name ZONE_NAME`:
- `--reason REASON` required:

### `dnsforge zone diff`

```bash
dnsforge zone diff [-h] --zone ZONE_NAME --from FROM_VERSION
                          --to TO_VERSION
```

Options:

- `--zone ZONE_NAME` required:
- `--from FROM_VERSION` required:
- `--to TO_VERSION` required:

### `dnsforge zone disable`

```bash
dnsforge zone disable [-h] [--name ZONE_NAME] --reason REASON [name]
```

Options:

- `name`:
- `--name ZONE_NAME`:
- `--reason REASON` required:

### `dnsforge zone edit`

```bash
dnsforge zone edit [-h] [--add ADD_RECORD] [--update UPDATE_RECORD]
                          [--delete DELETE_RECORD] [--ttl TTL] --reason REASON
                          name
```

Options:

- `name` required:
- `--add ADD_RECORD`:
- `--update UPDATE_RECORD`:
- `--delete DELETE_RECORD`:
- `--ttl TTL`:
- `--reason REASON` required:

### `dnsforge zone enable`

```bash
dnsforge zone enable [-h] [--name ZONE_NAME] --reason REASON [name]
```

Options:

- `name`:
- `--name ZONE_NAME`:
- `--reason REASON` required:

### `dnsforge zone get`

```bash
dnsforge zone get [-h] --name NAME
```

Options:

- `--name NAME` required:

### `dnsforge zone history`

```bash
dnsforge zone history [-h] name
```

Options:

- `name` required:

### `dnsforge zone list`

```bash
dnsforge zone list [-h] [--enabled] [--format {text,json}]
```

Options:

- `--enabled`: Show enabled/active zones only
- `--format FORMAT` default='text' choices=text,json:

### `dnsforge zone retire`

```bash
dnsforge zone retire [-h] [--name ZONE_NAME] --reason REASON [name]
```

Options:

- `name`:
- `--name ZONE_NAME`:
- `--reason REASON` required:

### `dnsforge zone rollback`

```bash
dnsforge zone rollback [-h] --zone ZONE_NAME --version VERSION
                              --reason REASON
```

Options:

- `--zone ZONE_NAME` required:
- `--version VERSION` required:
- `--reason REASON` required:

### `dnsforge zone search`

```bash
dnsforge zone search [-h] [--zone ZONE_NAME] [--owner OWNER]
                            [--view VIEW] [--state STATE]
                            [--environment ENVIRONMENT]
                            [--classification CLASSIFICATION]
                            [--record-name RECORD_NAME]
                            [--record-type RECORD_TYPE] [--value VALUE]
```

Options:

- `--zone ZONE_NAME`:
- `--owner OWNER`:
- `--view VIEW`:
- `--state STATE`:
- `--environment ENVIRONMENT`:
- `--classification CLASSIFICATION`:
- `--record-name RECORD_NAME`:
- `--record-type RECORD_TYPE`:
- `--value VALUE`:

### `dnsforge zone show`

```bash
dnsforge zone show [-h] [--zone ZONE_NAME] [--version VERSION] [name]
```

Options:

- `name`:
- `--zone ZONE_NAME`:
- `--version VERSION`:

### `dnsforge zone status`

```bash
dnsforge zone status [-h] name
```

Options:

- `name` required:
