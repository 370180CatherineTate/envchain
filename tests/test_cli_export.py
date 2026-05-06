"""Tests for envchain.cli_export."""

import json
import os
from pathlib import Path

import pytest

from envchain.cli_export import run
from envchain.profile import Profile
from envchain.chain import Chain


@pytest.fixture
def env_dirs(tmp_path):
    profiles_dir = tmp_path / "profiles"
    vault_dir = tmp_path / "vault"
    profiles_dir.mkdir()
    vault_dir.mkdir()
    return profiles_dir, vault_dir


def _make_profile(profiles_dir: Path, name: str, variables: dict) -> None:
    p = Profile(name, profiles_dir=profiles_dir)
    for k, v in variables.items():
        p.set(k, v)
    p.save()


def _make_chain(profiles_dir: Path, chain_name: str, profile_names: list) -> None:
    c = Chain(chain_name, profiles_dir=profiles_dir)
    for pn in profile_names:
        c.add(pn)
    c.save()


def test_run_bash_output(env_dirs):
    profiles_dir, vault_dir = env_dirs
    _make_profile(profiles_dir, "base", {"FOO": "bar", "BAZ": "qux"})
    _make_chain(profiles_dir, "mychain", ["base"])

    rc = run([
        "mychain",
        "--format", "bash",
        "--profiles-dir", str(profiles_dir),
        "--vault-dir", str(vault_dir),
    ])
    assert rc == 0


def test_run_dotenv_output(env_dirs, capsys):
    profiles_dir, vault_dir = env_dirs
    _make_profile(profiles_dir, "base", {"KEY": "val"})
    _make_chain(profiles_dir, "mychain", ["base"])

    rc = run([
        "mychain",
        "--format", "dotenv",
        "--profiles-dir", str(profiles_dir),
        "--vault-dir", str(vault_dir),
    ])
    captured = capsys.readouterr()
    assert rc == 0
    assert 'KEY="val"' in captured.out
    assert "export" not in captured.out


def test_run_fish_output(env_dirs, capsys):
    profiles_dir, vault_dir = env_dirs
    _make_profile(profiles_dir, "base", {"FISH_VAR": "swim"})
    _make_chain(profiles_dir, "mychain", ["base"])

    rc = run([
        "mychain",
        "--format", "fish",
        "--profiles-dir", str(profiles_dir),
        "--vault-dir", str(vault_dir),
    ])
    captured = capsys.readouterr()
    assert rc == 0
    assert 'set -x FISH_VAR "swim"' in captured.out


def test_run_missing_chain_returns_error(env_dirs, capsys):
    profiles_dir, vault_dir = env_dirs
    rc = run([
        "nonexistent",
        "--profiles-dir", str(profiles_dir),
        "--vault-dir", str(vault_dir),
    ])
    captured = capsys.readouterr()
    assert rc == 1
    assert "error:" in captured.err
