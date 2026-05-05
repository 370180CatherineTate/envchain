"""Profile management for envchain — load, save, and chain environment variable profiles."""

from __future__ import annotations

import os
import json
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_PROFILES_DIR = Path.home() / ".envchain" / "profiles"


class ProfileError(Exception):
    """Raised when a profile operation fails."""


class Profile:
    """Represents a named collection of environment variables with optional chaining."""

    def __init__(self, name: str, variables: Optional[Dict[str, str]] = None,
                 extends: Optional[List[str]] = None,
                 profiles_dir: Path = DEFAULT_PROFILES_DIR) -> None:
        self.name = name
        self.variables: Dict[str, str] = variables or {}
        self.extends: List[str] = extends or []
        self.profiles_dir = profiles_dir

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _profile_path(self) -> Path:
        return self.profiles_dir / f"{self.name}.json"

    def save(self) -> None:
        """Persist the profile to disk."""
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        data = {"name": self.name, "extends": self.extends, "variables": self.variables}
        path = self._profile_path()
        path.write_text(json.dumps(data, indent=2))
        path.chmod(0o600)

    @classmethod
    def load(cls, name: str, profiles_dir: Path = DEFAULT_PROFILES_DIR) -> "Profile":
        """Load a profile from disk by name."""
        path = profiles_dir / f"{name}.json"
        if not path.exists():
            raise ProfileError(f"Profile '{name}' not found in {profiles_dir}")
        data = json.loads(path.read_text())
        return cls(
            name=data["name"],
            variables=data.get("variables", {}),
            extends=data.get("extends", []),
            profiles_dir=profiles_dir,
        )

    # ------------------------------------------------------------------
    # Variable resolution with chaining
    # ------------------------------------------------------------------

    def resolve(self, profiles_dir: Optional[Path] = None) -> Dict[str, str]:
        """Return merged variables, applying parent profiles first (left-to-right)."""
        base_dir = profiles_dir or self.profiles_dir
        merged: Dict[str, str] = {}
        for parent_name in self.extends:
            parent = Profile.load(parent_name, base_dir)
            merged.update(parent.resolve(base_dir))
        merged.update(self.variables)
        return merged

    def set_var(self, key: str, value: str) -> None:
        self.variables[key] = value

    def get_var(self, key: str) -> Optional[str]:
        return self.variables.get(key)

    def delete_var(self, key: str) -> None:
        self.variables.pop(key, None)

    def apply_to_env(self) -> None:
        """Export resolved variables into the current process environment."""
        for key, value in self.resolve().items():
            os.environ[key] = value

    def __repr__(self) -> str:
        return f"Profile(name={self.name!r}, extends={self.extends!r}, vars={list(self.variables.keys())})"
