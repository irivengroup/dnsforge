from __future__ import annotations

from pathlib import Path

from dnsforge.interfaces.cli.main import build_parser


def test_security_related_cli_commands_parse(tmp_path: Path) -> None:
    setup_file = tmp_path / "setup.conf"
    setup_file.write_text(
        """ROLE="dns-proxy"
PROXY_TYPE="forwarder"
ENABLE_DNSSEC="yes"
ENABLE_RPZ="yes"
SECURITY_PROFILE="enterprise"
NODE_NAME="proxy01"
ENABLE_CLUSTER="yes"
CLUSTER_ROLE="proxy"
CLUSTER_PEERS="proxy01,proxy02"
CLUSTER_VIP="10.10.10.53"
CLUSTER_INTERFACE="eth0"
""",
        encoding="utf-8",
    )
    parser = build_parser()
    commands = [
        ["security", "history"],
        ["security", "rollback", "--version", "1"],
        ["acl", "--state-file", str(tmp_path / "acls.json"), "list"],
        ["acl", "--state-file", str(tmp_path / "acls.json"), "create", "internal"],
        ["acl", "--state-file", str(tmp_path / "acls.json"), "add-network", "internal", "10.0.0.0/8"],
        ["view", "--state-file", str(tmp_path / "views.json"), "list"],
        ["view", "--state-file", str(tmp_path / "views.json"), "create", "internal"],
        ["view", "--state-file", str(tmp_path / "views.json"), "attach-zone", "internal", "example.com"],
        ["dnssec", "--setup-file", str(setup_file), "status"],
        ["dnssec", "--setup-file", str(setup_file), "status", "--zone", "example.com"],
        ["dnssec", "--setup-file", str(setup_file), "validate"],
        ["dnssec", "--setup-file", str(setup_file), "validate", "--zone", "example.com"],
        ["dnssec", "--setup-file", str(setup_file), "enable", "--zone", "example.com", "--reason", "unit test change"],
        ["dnssec", "--setup-file", str(setup_file), "disable", "--zone", "example.com", "--reason", "unit test change"],
        ["dnssec", "--setup-file", str(setup_file), "sign", "--zone", "example.com", "--reason", "unit test change"],
        [
            "dnssec",
            "--setup-file",
            str(setup_file),
            "rotate-ksk",
            "--zone",
            "example.com",
            "--reason",
            "unit test change",
        ],
        [
            "dnssec",
            "--setup-file",
            str(setup_file),
            "rotate-zsk",
            "--zone",
            "example.com",
            "--reason",
            "unit test change",
        ],
        ["dnssec", "--setup-file", str(setup_file), "check-expiry"],
        ["rpz", "--setup-file", str(setup_file), "status"],
        ["rpz", "enable"],
        ["rpz", "update"],
        ["rpz", "test", "bad-domain.test"],
        ["cluster", "validate-security", "--setup-file", str(setup_file)],
    ]
    for command in commands:
        parser.parse_args(command)
