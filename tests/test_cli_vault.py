"""Tests for cli_vault subcommand."""

import argparse
import pytest
from pathlib import Path

from envchain.cli_vault import build_parser, run
from envchain.vault import Vault


@pytest.fixture()
def vault_dir(tmp_path):
    return tmp_path / "vault"


def _parse(args_list):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    build_parser(subparsers)
    return parser.parse_args(args_list)


def test_vault_set_and_get_via_cli(vault_dir, capsys):
    args = _parse(["vault", "set", "MY_TOKEN", "abc123"])
    run(args, vault_dir=vault_dir)
    captured = capsys.readouterr()
    assert "MY_TOKEN" in captured.out

    args = _parse(["vault", "get", "MY_TOKEN"])
    run(args, vault_dir=vault_dir)
    captured = capsys.readouterr()
    assert captured.out.strip() == "abc123"


def test_vault_get_missing_key_exits(vault_dir, capsys):
    args = _parse(["vault", "get", "MISSING_KEY"])
    with pytest.raises(SystemExit) as exc_info:
        run(args, vault_dir=vault_dir)
    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "MISSING_KEY" in captured.err


def test_vault_list_empty(vault_dir, capsys):
    args = _parse(["vault", "list"])
    run(args, vault_dir=vault_dir)
    captured = capsys.readouterr()
    assert "no secrets" in captured.out


def test_vault_list_shows_keys(vault_dir, capsys):
    v = Vault(vault_dir=vault_dir)
    v.set("ALPHA", "1")
    v.set("BETA", "2")
    v.save()

    args = _parse(["vault", "list"])
    run(args, vault_dir=vault_dir)
    captured = capsys.readouterr()
    assert "ALPHA" in captured.out
    assert "BETA" in captured.out


def test_vault_delete_key(vault_dir, capsys):
    v = Vault(vault_dir=vault_dir)
    v.set("TO_DELETE", "secret")
    v.save()

    args = _parse(["vault", "delete", "TO_DELETE"])
    run(args, vault_dir=vault_dir)
    captured = capsys.readouterr()
    assert "TO_DELETE" in captured.out

    v2 = Vault(vault_dir=vault_dir)
    assert v2.get("TO_DELETE") is None


def test_vault_delete_missing_key_exits(vault_dir, capsys):
    args = _parse(["vault", "delete", "GHOST"])
    with pytest.raises(SystemExit) as exc_info:
        run(args, vault_dir=vault_dir)
    assert exc_info.value.code == 1
