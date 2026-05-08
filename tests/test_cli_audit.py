import pytest
from pathlib import Path
from unittest.mock import patch

from envchain.cli_audit import run
from envchain.auditor import Auditor


@pytest.fixture()
def audit_dir(tmp_path: Path) -> Path:
    d = tmp_path / "audit"
    d.mkdir(parents=True)
    return d


def _run(argv, audit_dir):
    run(argv=argv, data_dir=audit_dir.parent)


def test_list_empty(audit_dir, capsys):
    _run(["list"], audit_dir)
    out = capsys.readouterr().out
    assert "No audit log entries" in out


def test_list_shows_entries(audit_dir, capsys):
    auditor = Auditor(audit_dir)
    auditor.record("export", "profile=default")
    auditor.record("vault_set", "key=SECRET")

    _run(["list"], audit_dir)
    out = capsys.readouterr().out
    assert "export" in out
    assert "vault_set" in out
    assert "profile=default" in out


def test_list_filter_by_event(audit_dir, capsys):
    auditor = Auditor(audit_dir)
    auditor.record("export", "profile=default")
    auditor.record("vault_set", "key=SECRET")

    _run(["list", "--event", "export"], audit_dir)
    out = capsys.readouterr().out
    assert "export" in out
    assert "vault_set" not in out


def test_list_limit(audit_dir, capsys):
    auditor = Auditor(audit_dir)
    for i in range(10):
        auditor.record("export", f"run={i}")

    _run(["list", "--limit", "3"], audit_dir)
    out = capsys.readouterr().out
    lines = [l for l in out.strip().splitlines() if l]
    assert len(lines) == 3


def test_clear(audit_dir, capsys):
    auditor = Auditor(audit_dir)
    auditor.record("export", "profile=default")

    _run(["clear"], audit_dir)
    out = capsys.readouterr().out
    assert "cleared" in out.lower()

    entries = auditor.read_all()
    assert entries == []


def test_list_after_clear_empty(audit_dir, capsys):
    auditor = Auditor(audit_dir)
    auditor.record("export", "profile=default")
    auditor.clear()

    _run(["list"], audit_dir)
    out = capsys.readouterr().out
    assert "No audit log entries" in out
