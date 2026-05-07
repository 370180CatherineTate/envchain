"""Tests for cli_profile subcommand."""

import argparse
import pytest

from envchain.cli_profile import build_parser, run
from envchain.profile import Profile


@pytest.fixture()
def env_dirs(tmp_path):
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    return {"profiles_dir": str(profiles_dir)}


def _parse(args):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="cmd")
    build_parser(subparsers)
    return parser.parse_args(["profile"] + args)


def _make_profile(profiles_dir, name, data):
    p = Profile(name, profiles_dir=profiles_dir)
    for k, v in data.items():
        p.set(k, v)
    p.save()
    return p


def test_set_creates_and_saves(env_dirs, capsys):
    args = _parse(["set", "dev", "FOO", "bar"])
    run(args, **env_dirs)
    out = capsys.readouterr().out
    assert "Set FOO in profile 'dev'" in out

    p = Profile("dev", **env_dirs)
    p.load()
    assert p.get("FOO") == "bar"


def test_get_existing_key(env_dirs, capsys):
    _make_profile(env_dirs["profiles_dir"], "dev", {"API_KEY": "secret"})
    args = _parse(["get", "dev", "API_KEY"])
    run(args, **env_dirs)
    out = capsys.readouterr().out
    assert out.strip() == "secret"


def test_get_missing_key_exits(env_dirs):
    _make_profile(env_dirs["profiles_dir"], "dev", {"X": "1"})
    args = _parse(["get", "dev", "MISSING"])
    with pytest.raises(SystemExit) as exc_info:
        run(args, **env_dirs)
    assert exc_info.value.code == 1


def test_get_missing_profile_exits(env_dirs):
    args = _parse(["get", "nonexistent", "KEY"])
    with pytest.raises(SystemExit) as exc_info:
        run(args, **env_dirs)
    assert exc_info.value.code == 1


def test_unset_removes_key(env_dirs, capsys):
    _make_profile(env_dirs["profiles_dir"], "dev", {"A": "1", "B": "2"})
    args = _parse(["unset", "dev", "A"])
    run(args, **env_dirs)

    p = Profile("dev", **env_dirs)
    p.load()
    assert p.get("A") is None
    assert p.get("B") == "2"


def test_list_profile_keys(env_dirs, capsys):
    _make_profile(env_dirs["profiles_dir"], "dev", {"Z": "26", "A": "1"})
    args = _parse(["list", "dev"])
    run(args, **env_dirs)
    out = capsys.readouterr().out
    lines = out.strip().splitlines()
    assert lines == ["A", "Z"]


def test_list_empty_profile(env_dirs, capsys):
    _make_profile(env_dirs["profiles_dir"], "empty", {})
    args = _parse(["list", "empty"])
    run(args, **env_dirs)
    out = capsys.readouterr().out
    assert "empty" in out
