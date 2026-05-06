"""Tests for envchain.exporter."""

import pytest

from envchain.exporter import Exporter, ExporterError


@pytest.fixture
def simple_env():
    return {"API_KEY": "abc123", "DEBUG": "true", "DB_URL": "postgres://localhost/db"}


def test_bash_export_format(simple_env):
    out = Exporter(simple_env).export("bash")
    assert 'export API_KEY="abc123"' in out
    assert 'export DEBUG="true"' in out
    assert 'export DB_URL="postgres://localhost/db"' in out


def test_fish_export_format(simple_env):
    out = Exporter(simple_env).export("fish")
    assert 'set -x API_KEY "abc123"' in out
    assert 'set -x DEBUG "true"' in out


def test_dotenv_format(simple_env):
    out = Exporter(simple_env).export("dotenv")
    assert 'API_KEY="abc123"' in out
    assert 'DEBUG="true"' in out
    # dotenv should NOT have 'export' keyword
    assert "export" not in out


def test_default_format_is_bash(simple_env):
    out_default = Exporter(simple_env).export()
    out_bash = Exporter(simple_env).export("bash")
    assert out_default == out_bash


def test_output_is_sorted(simple_env):
    out = Exporter(simple_env).export("bash")
    lines = out.splitlines()
    keys = [line.split()[1].split("=")[0] for line in lines]
    assert keys == sorted(keys)


def test_unsupported_format_raises(simple_env):
    with pytest.raises(ExporterError, match="Unsupported format"):
        Exporter(simple_env).export("powershell")


def test_invalid_env_type_raises():
    with pytest.raises(ExporterError, match="env must be a dict"):
        Exporter(["KEY=value"])


def test_bash_escapes_double_quotes():
    env = {"MSG": 'say "hello"'}
    out = Exporter(env).export("bash")
    assert 'export MSG="say \\"hello\\""' in out


def test_bash_escapes_backslash():
    env = {"PATH_VAL": "C:\\Users\\test"}
    out = Exporter(env).export("bash")
    assert "\\\\" in out


def test_empty_env_produces_empty_string():
    out = Exporter({}).export("bash")
    assert out == ""
