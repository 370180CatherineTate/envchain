"""Tests for the Importer module."""

import os
import pytest

from envchain.importer import Importer, ImporterError
from envchain.profile import Profile, ProfileError


@pytest.fixture
def profiles_dir(tmp_path):
    d = tmp_path / "profiles"
    d.mkdir()
    return str(d)


@pytest.fixture
def dotenv_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text(
        "# comment\n"
        "APP_ENV=production\n"
        "DB_HOST=localhost\n"
        "export SECRET_KEY=abc123\n"
        "QUOTED=\"hello world\"\n"
        "SINGLE_QUOTED='value'\n"
        "EMPTY_LINE=\n"
    )
    return str(f)


def test_parse_dotenv(profiles_dir, dotenv_file):
    importer = Importer(profiles_dir)
    result = importer._parse_dotenv(dotenv_file)
    assert result["APP_ENV"] == "production"
    assert result["DB_HOST"] == "localhost"
    assert result["SECRET_KEY"] == "abc123"
    assert result["QUOTED"] == "hello world"
    assert result["SINGLE_QUOTED"] == "value"


def test_from_dotenv_creates_profile(profiles_dir, dotenv_file):
    importer = Importer(profiles_dir)
    profile = importer.from_dotenv(dotenv_file, "myapp")
    assert profile.get("APP_ENV") == "production"
    assert profile.get("DB_HOST") == "localhost"


def test_from_dotenv_saves_profile(profiles_dir, dotenv_file):
    importer = Importer(profiles_dir)
    importer.from_dotenv(dotenv_file, "saved")
    loaded = Profile.load("saved", profiles_dir)
    assert loaded.get("APP_ENV") == "production"


def test_from_dotenv_no_overwrite(profiles_dir, dotenv_file):
    importer = Importer(profiles_dir)
    importer.from_dotenv(dotenv_file, "myapp")
    # Manually change a value
    p = Profile.load("myapp", profiles_dir)
    p.set("APP_ENV", "staging")
    p.save()
    # Re-import without overwrite
    importer.from_dotenv(dotenv_file, "myapp", overwrite=False)
    p2 = Profile.load("myapp", profiles_dir)
    assert p2.get("APP_ENV") == "staging"


def test_from_dotenv_with_overwrite(profiles_dir, dotenv_file):
    importer = Importer(profiles_dir)
    importer.from_dotenv(dotenv_file, "myapp")
    p = Profile.load("myapp", profiles_dir)
    p.set("APP_ENV", "staging")
    p.save()
    importer.from_dotenv(dotenv_file, "myapp", overwrite=True)
    p2 = Profile.load("myapp", profiles_dir)
    assert p2.get("APP_ENV") == "production"


def test_from_dotenv_missing_file(profiles_dir):
    importer = Importer(profiles_dir)
    with pytest.raises(ImporterError, match="File not found"):
        importer.from_dotenv("/nonexistent/.env", "myapp")


def test_from_env_imports_keys(profiles_dir, monkeypatch):
    monkeypatch.setenv("MY_APP_TOKEN", "tok123")
    monkeypatch.setenv("MY_APP_HOST", "example.com")
    importer = Importer(profiles_dir)
    profile = importer.from_env(["MY_APP_TOKEN", "MY_APP_HOST"], "envtest")
    assert profile.get("MY_APP_TOKEN") == "tok123"
    assert profile.get("MY_APP_HOST") == "example.com"


def test_from_env_missing_keys_raises(profiles_dir):
    importer = Importer(profiles_dir)
    with pytest.raises(ImporterError, match="No matching"):
        importer.from_env(["DEFINITELY_NOT_SET_XYZ"], "envtest")
