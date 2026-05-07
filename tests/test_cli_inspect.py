"""Tests for envchain.cli_inspect."""

import io
import json
import os
import pytest

from envchain.cli_inspect import build_parser, run
from envchain.profile import Profile
from envchain.chain import Chain


@pytest.fixture()
def env_dirs(tmp_path):
    profiles_dir = tmp_path / "profiles"
    chains_dir = tmp_path / "chains"
    profiles_dir.mkdir()
    chains_dir.mkdir()
    return {"profiles_dir": str(profiles_dir), "chains_dir": str(chains_dir)}


def _make_profile(env_dirs, name, data):
    p = Profile(name, profiles_dir=env_dirs["profiles_dir"])
    for k, v in data.items():
        p.set(k, v)
    p.save()
    return p


def _make_chain(env_dirs, name, profile_names):
    c = Chain(name, chains_dir=env_dirs["chains_dir"])
    for pn in profile_names:
        c.add(pn)
    c.save()
    return c


def _run(args_list, env_dirs):
    parser = build_parser()
    args = parser.parse_args(
        args_list
        + [
            "--profiles-dir", env_dirs["profiles_dir"],
            "--chains-dir", env_dirs["chains_dir"],
        ]
    )
    out = io.StringIO()
    run(args, out=out)
    return out.getvalue()


def test_list_profiles_empty(env_dirs):
    output = _run(["list", "profiles"], env_dirs)
    assert output == ""


def test_list_profiles_returns_names(env_dirs):
    _make_profile(env_dirs, "alpha", {"A": "1"})
    _make_profile(env_dirs, "beta", {"B": "2"})
    output = _run(["list", "profiles"], env_dirs)
    lines = output.strip().splitlines()
    assert sorted(lines) == ["alpha", "beta"]


def test_list_chains_returns_names(env_dirs):
    _make_profile(env_dirs, "base", {"X": "1"})
    _make_chain(env_dirs, "mychain", ["base"])
    output = _run(["list", "chains"], env_dirs)
    assert "mychain" in output


def test_describe_profile(env_dirs):
    _make_profile(env_dirs, "svc", {"PORT": "8080", "HOST": "localhost"})
    output = _run(["describe", "profile", "svc"], env_dirs)
    assert "PORT" in output or "HOST" in output


def test_describe_chain(env_dirs):
    _make_profile(env_dirs, "base", {"X": "1"})
    _make_chain(env_dirs, "prod", ["base"])
    output = _run(["describe", "chain", "prod"], env_dirs)
    assert "prod" in output or "base" in output


def test_describe_missing_profile_exits(env_dirs):
    parser = build_parser()
    args = parser.parse_args(
        ["describe", "profile", "nonexistent",
         "--profiles-dir", env_dirs["profiles_dir"],
         "--chains-dir", env_dirs["chains_dir"]]
    )
    with pytest.raises(SystemExit) as exc_info:
        run(args)
    assert exc_info.value.code == 1
