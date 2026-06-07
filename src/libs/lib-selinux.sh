#!/usr/bin/env bash

apply_selinux_contexts() {

    if ! command -v restorecon >/dev/null 2>&1
    then
        log_warn "restorecon not found - skipping SELinux relabel"
        return 0
    fi

    log_info "Restoring SELinux contexts"

    restorecon -Rv /etc/named.conf /etc/named /var/named /var/log/named || true

    if command -v setsebool >/dev/null 2>&1
    then
        setsebool -P named_write_master_zones on || true
    fi

    log_ok "SELinux contexts restored"
}
