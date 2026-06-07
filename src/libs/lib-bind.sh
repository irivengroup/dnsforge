#!/usr/bin/env bash

install_bind_packages() {

    if [[ "${SKIP_INSTALL}" == "true" ]]
    then
        log_info "Package installation skipped"
        return 0
    fi

    if rpm -q bind >/dev/null 2>&1 && rpm -q bind-utils >/dev/null 2>&1
    then
        log_ok "BIND packages already installed"
        return 0
    fi

    log_info "Installing BIND packages"

    dnf install -y bind bind-utils policycoreutils-python-utils
}


install_keepalived_package() {

    if [[ "${SKIP_INSTALL}" == "true" ]]
    then
        log_info "Keepalived installation skipped"
        return 0
    fi

    if rpm -q keepalived >/dev/null 2>&1
    then
        log_ok "Keepalived already installed"
        return 0
    fi

    log_info "Installing keepalived"

    dnf install -y keepalived
}
