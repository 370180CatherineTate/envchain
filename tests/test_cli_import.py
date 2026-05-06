"""Tests for the cli_import module."""

import os
import pytest

from envchain.cli_import import run
from envchain.profile import Profile, ProfileError


@pytest.fixture
def env_dirs(tmp_path):
    profiles = tmp_path / "profiles"
    profiles.mkdir()
    return {"profiles": str(profiles)}


@pytest.fixture
def dotenv_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("APP_ENV=production\nDB_HOST=localhost\n")
    return str(f)


def test_run_dotenv_import(env_dirs, dotenv_file, capsys):
    run(
        ["myapp", "dotenv", dotenv_file],
        profiles_dir=env_dirs["profiles"],
    )
    out = capsys.readouterr().out
    assert "myapp" in out
    assert "2" in out
    profile = Profile.load("myapp", env_dirs["profiles"])
    assert profile.get("APP_ENV") == "production"


def test_run_dotenv_missing_file_exits(env_dirs, capsys):
    with pytest.raises(SystemExit) as exc:
        run(
            ["myapp", "dotenv", "/nonexistent/.env"],
            profiles_dir=env_dirs["profiles"],
        )
    assert exc.value.code == 1
    err = capsys.readouterr().err
    assert "Error" in err


def test_run_env_import(env_dirs, monkeypatch, capsys):
    monkeypatch.setenv("CLI_TEST_VAR", "hello")
    run(
        ["envtest", "env", "CLI_TEST_VAR"],
        profiles_dir=env_dirs["profiles"],
    )
    out = capsys.readouterr().out
    assert "envtest" in out
    profile = Profile.load("envtest", env_dirs["profiles"])
    assert profile.get("CLI_TEST_VAR") == "hello"


def test_run_env_no_match_exits(env_dirs, capsys):
    with pytest.raises(SystemExit) as exc:
        run(
            ["envtest", "env", "DEFINITELY_UNSET_VAR_XYZ"],
            profiles_dir=env_dirs["profiles"],
        )
    assert exc.value.code == 1


def test_run_dotenv_overwrite_flag(env_dirs, dotenv_file, capsys):
    run(["myapp", "dotenv", dotenv_file], profiles_dir=env_dirs["profiles"])
    p = Profile.load("myapp", env_dirs["profiles"])
    p.set("APP_ENV", "staging")
    p.save()
    run(["myapp", "dotenv", dotenv_file, "--overwrite"], profiles_dir=env_dirs["profiles"])
    p2 = Profile.load("myapp", env_dirs["profiles"])
    assert p2.get("APP_ENV") == "production"
