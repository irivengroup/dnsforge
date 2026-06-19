from __future__ import annotations

CLI_API_PARITY_PRINCIPLES = (
    "DNSForge CLI is a primary local administration interface.",
    "The CLI must remain available on every installed DNSForge server.",
    "HTTP APIs, DNSForge Manager and external products are optional adapters.",
    "No operational feature may become API-only or GUI-only.",
    "CLI and APIs must share application services instead of wrapping each other.",
)

# Commands that must always remain locally exposed by the installed dnsforge binary.
LOCAL_CLI_COMMANDS = (
    "acl",
    "audit",
    "backup",
    "catalog",
    "cluster",
    "config",
    "deploy",
    "disaster",
    "dnssec",
    "doctor",
    "generate",
    "health",
    "initialize",
    "migrate",
    "profile",
    "render",
    "restore",
    "rpz",
    "security",
    "status",
    "validate",
    "version",
    "view",
    "zone",
)
