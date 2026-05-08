"""Tests for envchain.snapshotter."""

import json
import pytest
from pathlib import Path

from envchain.snapshotter import Snapshotter, SnapshotError


@pytest.fixture
def env_dirs(tmp_path):
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    snapshots_dir = tmp_path / "snapshots"
    return profiles_dir, snapshots_dir


def _write_profile(profiles_dir: Path, name: str, data: dict):
    p = profiles_dir / f"{name}.json"
    p.write_text(json.dumps(data))


def test_create_snapshot_all_profiles(env_dirs):
    profiles_dir, snapshots_dir = env_dirs
    _write_profile(profiles_dir, "dev", {"vars": {"FOO": "bar"}})
    _write_profile(profiles_dir, "prod", {"vars": {"FOO": "baz"}})

    s = Snapshotter(str(profiles_dir), str(snapshots_dir))
    snap = s.create("backup1")

    assert snap["name"] == "backup1"
    assert "dev" in snap["profiles"]
    assert "prod" in snap["profiles"]
    assert snap["profiles"]["dev"] == {"vars": {"FOO": "bar"}}


def test_create_snapshot_selected_profiles(env_dirs):
    profiles_dir, snapshots_dir = env_dirs
    _write_profile(profiles_dir, "dev", {"vars": {"A": "1"}})
    _write_profile(profiles_dir, "prod", {"vars": {"A": "2"}})

    s = Snapshotter(str(profiles_dir), str(snapshots_dir))
    snap = s.create("only_dev", profile_names=["dev"])

    assert "dev" in snap["profiles"]
    assert "prod" not in snap["profiles"]


def test_create_snapshot_missing_profile_raises(env_dirs):
    profiles_dir, snapshots_dir = env_dirs
    s = Snapshotter(str(profiles_dir), str(snapshots_dir))
    with pytest.raises(SnapshotError, match="Profile not found"):
        s.create("bad", profile_names=["nonexistent"])


def test_create_invalid_name_raises(env_dirs):
    profiles_dir, snapshots_dir = env_dirs
    s = Snapshotter(str(profiles_dir), str(snapshots_dir))
    with pytest.raises(SnapshotError, match="Invalid snapshot name"):
        s.create("bad-name!")


def test_restore_snapshot(env_dirs):
    profiles_dir, snapshots_dir = env_dirs
    _write_profile(profiles_dir, "dev", {"vars": {"X": "original"}})

    s = Snapshotter(str(profiles_dir), str(snapshots_dir))
    s.create("snap1")

    # Overwrite the profile with new data
    _write_profile(profiles_dir, "dev", {"vars": {"X": "changed"}})

    restored = s.restore("snap1", overwrite=True)
    assert "dev" in restored

    result = json.loads((profiles_dir / "dev.json").read_text())
    assert result["vars"]["X"] == "original"


def test_restore_no_overwrite_raises(env_dirs):
    profiles_dir, snapshots_dir = env_dirs
    _write_profile(profiles_dir, "dev", {"vars": {"X": "1"}})

    s = Snapshotter(str(profiles_dir), str(snapshots_dir))
    s.create("snap1")

    with pytest.raises(SnapshotError, match="already exists"):
        s.restore("snap1", overwrite=False)


def test_restore_missing_snapshot_raises(env_dirs):
    profiles_dir, snapshots_dir = env_dirs
    s = Snapshotter(str(profiles_dir), str(snapshots_dir))
    with pytest.raises(SnapshotError, match="Snapshot not found"):
        s.restore("ghost")


def test_list_snapshots(env_dirs):
    profiles_dir, snapshots_dir = env_dirs
    _write_profile(profiles_dir, "dev", {"vars": {}})

    s = Snapshotter(str(profiles_dir), str(snapshots_dir))
    s.create("alpha")
    s.create("beta")

    listing = s.list_snapshots()
    names = [entry["name"] for entry in listing]
    assert "alpha" in names
    assert "beta" in names


def test_delete_snapshot(env_dirs):
    profiles_dir, snapshots_dir = env_dirs
    _write_profile(profiles_dir, "dev", {"vars": {}})

    s = Snapshotter(str(profiles_dir), str(snapshots_dir))
    s.create("to_delete")
    s.delete("to_delete")

    assert s.list_snapshots() == []


def test_delete_missing_snapshot_raises(env_dirs):
    profiles_dir, snapshots_dir = env_dirs
    s = Snapshotter(str(profiles_dir), str(snapshots_dir))
    with pytest.raises(SnapshotError, match="Snapshot not found"):
        s.delete("nope")
