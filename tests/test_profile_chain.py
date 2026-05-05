"""Tests for Profile and Chain modules."""

import os
import pytest
from pathlib import Path

from envchain.profile import Profile, ProfileError
from envchain.chain import Chain


@pytest.fixture()
def profiles_dir(tmp_path: Path) -> Path:
    d = tmp_path / "profiles"
    d.mkdir()
    return d


# ---------------------------------------------------------------------------
# Profile tests
# ---------------------------------------------------------------------------

def test_profile_set_and_get(profiles_dir):
    p = Profile("base", profiles_dir=profiles_dir)
    p.set_var("FOO", "bar")
    assert p.get_var("FOO") == "bar"


def test_profile_save_and_load(profiles_dir):
    p = Profile("base", profiles_dir=profiles_dir)
    p.set_var("KEY", "value")
    p.save()

    loaded = Profile.load("base", profiles_dir)
    assert loaded.get_var("KEY") == "value"


def test_profile_file_permissions(profiles_dir):
    p = Profile("secure", profiles_dir=profiles_dir)
    p.set_var("SECRET", "s3cr3t")
    p.save()
    mode = (profiles_dir / "secure.json").stat().st_mode & 0o777
    assert mode == 0o600


def test_profile_load_missing_raises(profiles_dir):
    with pytest.raises(ProfileError, match="not found"):
        Profile.load("nonexistent", profiles_dir)


def test_profile_delete_var(profiles_dir):
    p = Profile("base", profiles_dir=profiles_dir)
    p.set_var("REMOVE_ME", "yes")
    p.delete_var("REMOVE_ME")
    assert p.get_var("REMOVE_ME") is None


def test_profile_resolve_with_extends(profiles_dir):
    parent = Profile("parent", profiles_dir=profiles_dir)
    parent.set_var("BASE", "from_parent")
    parent.set_var("OVERRIDE", "parent_val")
    parent.save()

    child = Profile("child", extends=["parent"], profiles_dir=profiles_dir)
    child.set_var("OVERRIDE", "child_val")
    child.set_var("CHILD_ONLY", "yes")

    resolved = child.resolve(profiles_dir)
    assert resolved["BASE"] == "from_parent"
    assert resolved["OVERRIDE"] == "child_val"  # child wins
    assert resolved["CHILD_ONLY"] == "yes"


# ---------------------------------------------------------------------------
# Chain tests
# ---------------------------------------------------------------------------

def test_chain_resolve_merges_profiles(profiles_dir):
    a = Profile("a", profiles_dir=profiles_dir)
    a.set_var("FROM_A", "a")
    a.set_var("SHARED", "a_val")
    a.save()

    b = Profile("b", profiles_dir=profiles_dir)
    b.set_var("FROM_B", "b")
    b.set_var("SHARED", "b_val")
    b.save()

    chain = Chain(profiles_dir=profiles_dir).add("a").add("b")
    result = chain.resolve()
    assert result["FROM_A"] == "a"
    assert result["FROM_B"] == "b"
    assert result["SHARED"] == "b_val"  # b overrides a


def test_chain_add_duplicate_ignored(profiles_dir):
    chain = Chain(profiles_dir=profiles_dir).add("x").add("x")
    assert chain.profile_names.count("x") == 1


def test_chain_remove(profiles_dir):
    chain = Chain(profiles_dir=profiles_dir).add("a").add("b").remove("a")
    assert "a" not in chain.profile_names
    assert "b" in chain.profile_names


def test_chain_serialisation_roundtrip(profiles_dir):
    chain = Chain(profiles_dir=profiles_dir).add("p1").add("p2")
    data = chain.to_dict()
    restored = Chain.from_dict(data, profiles_dir=profiles_dir)
    assert restored.profile_names == ["p1", "p2"]
