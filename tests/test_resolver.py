"""Tests for envchain.resolver."""

import pytest

from envchain.chain import Chain
from envchain.profile import Profile
from envchain.resolver import Resolver, ResolverError
from envchain.vault import Vault


@pytest.fixture()
def profiles_dir(tmp_path):
    return str(tmp_path / "profiles")


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path / "vault")


def _make_profile(name: str, data: dict, profiles_dir: str) -> Profile:
    p = Profile(name, profiles_dir)
    for k, v in data.items():
        p.set(k, v)
    p.save()
    return p


def test_resolve_single_profile(profiles_dir):
    _make_profile("base", {"APP_ENV": "production", "PORT": "8080"}, profiles_dir)
    chain = Chain("mychain")
    chain.add("base")
    resolver = Resolver(chain, profiles_dir)
    env = resolver.resolve()
    assert env["APP_ENV"] == "production"
    assert env["PORT"] == "8080"


def test_resolve_later_profile_overrides_earlier(profiles_dir):
    _make_profile("base", {"DEBUG": "false", "PORT": "8080"}, profiles_dir)
    _make_profile("dev", {"DEBUG": "true"}, profiles_dir)
    chain = Chain("mychain")
    chain.add("base")
    chain.add("dev")
    resolver = Resolver(chain, profiles_dir)
    env = resolver.resolve()
    assert env["DEBUG"] == "true"
    assert env["PORT"] == "8080"


def test_resolve_vault_secret_injected(profiles_dir, vault_dir):
    _make_profile("app", {"DB_PASSWORD": "vault:db_pass"}, profiles_dir)
    vault = Vault(vault_dir)
    vault.set("db_pass", "supersecret")
    vault.save()
    chain = Chain("mychain")
    chain.add("app")
    resolver = Resolver(chain, profiles_dir, vault=vault)
    env = resolver.resolve()
    assert env["DB_PASSWORD"] == "supersecret"


def test_resolve_missing_vault_secret_raises(profiles_dir, vault_dir):
    _make_profile("app", {"API_KEY": "vault:missing_key"}, profiles_dir)
    vault = Vault(vault_dir)
    vault.save()
    chain = Chain("mychain")
    chain.add("app")
    resolver = Resolver(chain, profiles_dir, vault=vault)
    with pytest.raises(ResolverError, match="missing_key"):
        resolver.resolve()


def test_resolve_vault_ref_without_vault_raises(profiles_dir):
    _make_profile("app", {"TOKEN": "vault:my_token"}, profiles_dir)
    chain = Chain("mychain")
    chain.add("app")
    resolver = Resolver(chain, profiles_dir)
    with pytest.raises(ResolverError, match="no vault configured"):
        resolver.resolve()


def test_resolve_missing_profile_raises(profiles_dir):
    chain = Chain("mychain")
    chain.add("nonexistent")
    resolver = Resolver(chain, profiles_dir)
    with pytest.raises(ResolverError, match="nonexistent"):
        resolver.resolve()


def test_resolve_empty_chain_returns_empty(profiles_dir):
    chain = Chain("empty")
    resolver = Resolver(chain, profiles_dir)
    assert resolver.resolve() == {}
