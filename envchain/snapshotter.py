"""Snapshot and restore environment variable profiles."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path


class SnapshotError(Exception):
    pass


class Snapshotter:
    """Creates and restores named snapshots of profile data."""

    SNAPSHOT_DIR_NAME = "snapshots"

    def __init__(self, profiles_dir: str, snapshots_dir: str = None):
        self.profiles_dir = Path(profiles_dir)
        if snapshots_dir:
            self.snapshots_dir = Path(snapshots_dir)
        else:
            self.snapshots_dir = self.profiles_dir.parent / self.SNAPSHOT_DIR_NAME
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)

    def _snapshot_path(self, name: str) -> Path:
        return self.snapshots_dir / f"{name}.json"

    def create(self, name: str, profile_names: list = None) -> dict:
        """Snapshot all (or selected) profiles into a named snapshot file."""
        if not name or not name.isidentifier():
            raise SnapshotError(f"Invalid snapshot name: {name!r}")

        snapshot = {
            "name": name,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "profiles": {},
        }

        available = [
            p.stem for p in self.profiles_dir.glob("*.json")
        ]
        targets = profile_names if profile_names else available

        for pname in targets:
            pfile = self.profiles_dir / f"{pname}.json"
            if not pfile.exists():
                raise SnapshotError(f"Profile not found: {pname!r}")
            with open(pfile, "r") as f:
                snapshot["profiles"][pname] = json.load(f)

        dest = self._snapshot_path(name)
        with open(dest, "w") as f:
            json.dump(snapshot, f, indent=2)
        os.chmod(dest, 0o600)
        return snapshot

    def restore(self, name: str, overwrite: bool = False) -> list:
        """Restore profiles from a named snapshot. Returns list of restored profile names."""
        snap_path = self._snapshot_path(name)
        if not snap_path.exists():
            raise SnapshotError(f"Snapshot not found: {name!r}")

        with open(snap_path, "r") as f:
            snapshot = json.load(f)

        restored = []
        for pname, data in snapshot.get("profiles", {}).items():
            dest = self.profiles_dir / f"{pname}.json"
            if dest.exists() and not overwrite:
                raise SnapshotError(
                    f"Profile {pname!r} already exists. Use overwrite=True to replace."
                )
            with open(dest, "w") as f:
                json.dump(data, f, indent=2)
            os.chmod(dest, 0o600)
            restored.append(pname)
        return restored

    def list_snapshots(self) -> list:
        """Return list of snapshot metadata dicts (name + created_at)."""
        results = []
        for snap_file in sorted(self.snapshots_dir.glob("*.json")):
            with open(snap_file, "r") as f:
                data = json.load(f)
            results.append({
                "name": data.get("name", snap_file.stem),
                "created_at": data.get("created_at", ""),
                "profiles": list(data.get("profiles", {}).keys()),
            })
        return results

    def delete(self, name: str) -> None:
        """Delete a named snapshot."""
        snap_path = self._snapshot_path(name)
        if not snap_path.exists():
            raise SnapshotError(f"Snapshot not found: {name!r}")
        snap_path.unlink()
