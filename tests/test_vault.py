"""Tests for the local vault module."""

import json
import pytest
from pathlib import Path

from envchain.vault import Vault, VaultError


@pytest.fixture
def tmp_vault(tmp_path):
    """Return a Vault instance backed by a temporary directory."""
    return Vault(name="test", vault_dir=tmp_path)


def test_vault_set_and_get(tmp_vault):
    tmp_vault.set("API_KEY", "secret123")
    assert tmp_vault.get("API_KEY") == "secret123"


def test_vault_get_missing_key_returns_none(tmp_vault):
    assert tmp_vault.get("NONEXISTENT") is None


def test_vault_save_and_load(tmp_vault):
    tmp_vault.set("DB_PASS", "hunter2")
    tmp_vault.save()

    loaded = Vault(name="test", vault_dir=tmp_vault.vault_dir)
    loaded.load()
    assert loaded.get("DB_PASS") == "hunter2"


def test_vault_file_permissions(tmp_vault):
    tmp_vault.set("TOKEN", "abc")
    tmp_vault.save()
    mode = tmp_vault.vault_path.stat().st_mode & 0o777
    assert mode == 0o600


def test_vault_delete_existing_key(tmp_vault):
    tmp_vault.set("KEY", "value")
    result = tmp_vault.delete("KEY")
    assert result is True
    assert tmp_vault.get("KEY") is None


def test_vault_delete_missing_key(tmp_vault):
    result = tmp_vault.delete("GHOST")
    assert result is False


def test_vault_list_keys(tmp_vault):
    tmp_vault.set("A", "1")
    tmp_vault.set("B", "2")
    keys = tmp_vault.list_keys()
    assert sorted(keys) == ["A", "B"]


def test_vault_load_empty_when_file_missing(tmp_vault):
    tmp_vault.load()
    assert tmp_vault.list_keys() == []


def test_vault_load_raises_on_corrupt_file(tmp_path):
    vault = Vault(name="bad", vault_dir=tmp_path)
    vault.vault_path.write_text("not valid json")
    with pytest.raises(VaultError, match="Failed to load vault"):
        vault.load()


def test_vault_destroy(tmp_vault):
    tmp_vault.set("X", "y")
    tmp_vault.save()
    assert tmp_vault.vault_path.exists()
    tmp_vault.destroy()
    assert not tmp_vault.vault_path.exists()
    assert tmp_vault.list_keys() == []


def test_vault_set_overwrites_existing_key(tmp_vault):
    """Setting a key twice should update the value, not duplicate it."""
    tmp_vault.set("API_KEY", "original")
    tmp_vault.set("API_KEY", "updated")
    assert tmp_vault.get("API_KEY") == "updated"
    assert tmp_vault.list_keys().count("API_KEY") == 1
