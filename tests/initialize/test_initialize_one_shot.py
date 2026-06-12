from __future__ import annotations

from pathlib import Path

from dnsforge.infrastructure.initialize.state_store import InitializeAlreadyAppliedError, InitializeStateStore
from dnsforge.interfaces.cli.main import build_parser


def test_initialize_cli_accepts_one_shot_modes() -> None:
    parser = build_parser()
    for command in (
        ["initialize"],
        ["initialize", "--render-only"],
        ["initialize", "--apply"],
        ["initialize", "--dry-run"],
    ):
        parser.parse_args(command)


def test_initialize_lock_is_stored_outside_setup_conf(tmp_path: Path) -> None:
    setup_file = tmp_path / "etc/dnsforge/setup.conf"
    setup_file.parent.mkdir(parents=True)
    setup_file.write_text("ROLE=authoritative\nNODE_NAME=local\n", encoding="utf-8")

    store = InitializeStateStore()
    assert store.is_initialized(setup_file) is False
    store.mark_initialized(setup_file, role="authoritative", node="local")
    assert store.is_initialized(setup_file) is True

    try:
        store.assert_not_initialized(setup_file)
    except InitializeAlreadyAppliedError as exc:
        assert "already initialized" in str(exc)
    else:
        raise AssertionError("initialize one-shot lock did not block second attempt")

    assert "DNSFORGE_INITIALIZED" not in setup_file.read_text(encoding="utf-8")
    lock_file = setup_file.parent / ".initialized.conf.lock"
    data = lock_file.read_text(encoding="utf-8")
    assert "INITIALIZED=true" in data
    assert "INITIALIZED_AT=" in data
    assert "INITIALIZED_ROLE=authoritative" in data
    assert "INITIALIZED_NODE=local" in data
