"""Tests for the Inspector module."""

from __future__ import annotations

import pytest
from pathlib import Path

from envchain.inspector import Inspector, InspectorError
from envchain.profile import Profile
from envchain.chain import Chain
from envchain.vault import Vault


@pytest.fixture()
def env_dirs(tmp_path: Path):
    profiles_dir = tmp_path / "profiles"
    vault_dir = tmp_path / "vault"
    profiles_dir.mkdir()
    vault_dir.mkdir()
    return profiles_dir, vault_dir


def _make_profile(name: str, data: dict, profiles_dir: Path) -> Profile:
    p = Profile(name, profiles_dir)
    for k, v in data.items():
        p.set(k, v)
    p.save()
    return p


def test_list_profiles_empty(env_dirs):
    profiles_dir, vault_dir = env_dirs
    inspector = Inspector(profiles_dir, vault_dir)
    assert inspector.list_profiles() == []


def test_list_profiles_returns_names(env_dirs):
    profiles_dir, vault_dir = env_dirs
    _make_profile("alpha", {"A": "1"}, profiles_dir)
    _make_profile("beta", {"B": "2"}, profiles_dir)
    inspector = Inspector(profiles_dir, vault_dir)
    assert inspector.list_profiles() == ["alpha", "beta"]


def test_describe_profile(env_dirs):
    profiles_dir, vault_dir = env_dirs
    _make_profile("myprof", {"FOO": "bar", "BAZ": "qux"}, profiles_dir)
    inspector = Inspector(profiles_dir, vault_dir)
    result = inspector.describe_profile("myprof")
    assert result["name"] == "myprof"
    assert result["keys"] == ["BAZ", "FOO"]
    assert result["count"] == 2


def test_describe_profile_missing_raises(env_dirs):
    profiles_dir, vault_dir = env_dirs
    inspector = Inspector(profiles_dir, vault_dir)
    with pytest.raises(InspectorError):
        inspector.describe_profile("nonexistent")


def test_describe_chain(env_dirs):
    profiles_dir, vault_dir = env_dirs
    _make_profile("p1", {"X": "1"}, profiles_dir)
    _make_profile("p2", {"Y": "2"}, profiles_dir)
    chain = Chain("mychain", profiles_dir)
    chain.add("p1")
    chain.add("p2")
    chain.save()
    inspector = Inspector(profiles_dir, vault_dir)
    result = inspector.describe_chain("mychain")
    assert result["name"] == "mychain"
    assert result["profiles"] == ["p1", "p2"]
    assert result["count"] == 2


def test_describe_chain_missing_raises(env_dirs):
    profiles_dir, vault_dir = env_dirs
    inspector = Inspector(profiles_dir, vault_dir)
    with pytest.raises(InspectorError):
        inspector.describe_chain("ghost")


def test_list_vault_keys(env_dirs):
    profiles_dir, vault_dir = env_dirs
    vault = Vault(vault_dir)
    vault.set("SECRET_A", "aaa")
    vault.set("SECRET_B", "bbb")
    vault.save()
    inspector = Inspector(profiles_dir, vault_dir)
    assert inspector.list_vault_keys() == ["SECRET_A", "SECRET_B"]


def test_list_vault_keys_empty(env_dirs):
    profiles_dir, vault_dir = env_dirs
    inspector = Inspector(profiles_dir, vault_dir)
    assert inspector.list_vault_keys() == []
