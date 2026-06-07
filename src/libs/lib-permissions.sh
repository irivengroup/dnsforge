#!/usr/bin/env bash

apply_bind_permissions() {

    log_info "Applying BIND ownership and permissions"

    chown root:named /etc/named.conf
    chmod 0640 /etc/named.conf

    chown -R root:named /etc/named
    find /etc/named -type d -exec chmod 0750 {} \;
    find /etc/named -type f -exec chmod 0640 {} \;

    chown -R named:named /var/named
    find /var/named -type d -exec chmod 0750 {} \;
    find /var/named -type f -exec chmod 0640 {} \;

    mkdir -p /var/log/named
    chown -R named:named /var/log/named
    chmod 0750 /var/log/named

    log_ok "Permissions applied"
}
