"""Tests for envchain.auditor and envchain.cli_audit."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import pytest

from envchain.auditor import Auditor
from envchain.cli_audit import build_parser, run


@pytest.fixture
def audit_dir(tmp_path):
    return tmp_path / "audit_data"


def test_record_and_read_all(audit_dir):
    a = Auditor(audit_dir)
    a.record("resolve", {"profile": "dev"})
    a.record("export", {"chain": "mychain"})
    entries = a.read_all()
    assert len(entries) == 2
    assert entries[0]["event"] == "resolve"
    assert entries[0]["profile"] == "dev"
    assert entries[1]["event"] == "export"


def test_read_all_empty(audit_dir):
    a = Auditor(audit_dir)
    assert a.read_all() == []


def test_filter_by_event(audit_dir):
    a = Auditor(audit_dir)
    a.record("resolve", {"profile": "staging"})
    a.record("export", {"chain": "c1"})
    a.record("resolve", {"profile": "prod"})
    results = a.filter_by_event("resolve")
    assert len(results) == 2
    assert all(e["event"] == "resolve" for e in results)


def test_clear(audit_dir):
    a = Auditor(audit_dir)
    a.record("resolve", {"profile": "dev"})
    a.clear()
    assert a.read_all() == []


def test_clear_nonexistent_log(audit_dir):
    a = Auditor(audit_dir)
    # Should not raise even if log never existed
    a.clear()


def test_timestamp_is_recent(audit_dir):
    before = time.time()
    a = Auditor(audit_dir)
    a.record("export", {"chain": "x"})
    after = time.time()
    entry = a.read_all()[0]
    assert before <= entry["timestamp"] <= after


# --- CLI tests ---

def _parse(data_dir, *args):
    parser = build_parser()
    ns = parser.parse_args(list(args) + ["--data-dir", str(data_dir)])
    return ns


def test_cli_list_empty(audit_dir, capsys):
    ns = _parse(audit_dir, "list")
    run(ns)
    out = capsys.readouterr().out
    assert "No audit log entries" in out


def test_cli_list_shows_entries(audit_dir, capsys):
    a = Auditor(audit_dir)
    a.record("resolve", {"profile": "dev"})
    ns = _parse(audit_dir, "list")
    run(ns)
    out = capsys.readouterr().out
    assert "resolve" in out
    assert "dev" in out


def test_cli_list_filter_by_event(audit_dir, capsys):
    a = Auditor(audit_dir)
    a.record("resolve", {"profile": "dev"})
    a.record("export", {"chain": "c1"})
    ns = _parse(audit_dir, "list", "--event", "export")
    run(ns)
    out = capsys.readouterr().out
    assert "export" in out
    assert "resolve" not in out


def test_cli_clear(audit_dir, capsys):
    a = Auditor(audit_dir)
    a.record("resolve", {"profile": "dev"})
    ns = _parse(audit_dir, "clear")
    run(ns)
    out = capsys.readouterr().out
    assert "cleared" in out
    assert a.read_all() == []
