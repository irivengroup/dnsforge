#!/usr/bin/env bash

is_firewalld_active() {

    systemctl is-active firewalld >/dev/null 2>&1
}


configure_proxy_firewall() {

    if ! is_firewalld_active
    then
        log_info "firewalld inactive - firewall configuration skipped"
        return 0
    fi

    log_info "Applying firewalld rules for DNS proxy"

    firewall-cmd --permanent --add-service=dns
    firewall-cmd --permanent --add-port=953/tcp
    firewall-cmd --permanent --add-port=8053/tcp
    firewall-cmd --reload

    log_ok "firewalld rules applied"
}


configure_authoritative_firewall() {

    if ! is_firewalld_active
    then
        log_info "firewalld inactive - firewall configuration skipped"
        return 0
    fi

    log_info "Applying firewalld rules for authoritative DNS"

    firewall-cmd --permanent --add-service=dns
    firewall-cmd --permanent --add-port=953/tcp
    firewall-cmd --permanent --add-port=8053/tcp
    firewall-cmd --permanent --add-protocol=vrrp || true
    firewall-cmd --reload

    log_ok "firewalld rules applied"
}
