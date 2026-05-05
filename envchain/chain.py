"""Chain builder — compose multiple profiles into a single resolved environment."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from envchain.profile import Profile, DEFAULT_PROFILES_DIR


class Chain:
    """Builds an ordered chain of profiles and resolves them into one env map."""

    def __init__(self, profiles_dir: Path = DEFAULT_PROFILES_DIR) -> None:
        self.profiles_dir = profiles_dir
        self._profile_names: List[str] = []

    # ------------------------------------------------------------------
    # Builder API
    # ------------------------------------------------------------------

    def add(self, profile_name: str) -> "Chain":
        """Append a profile to the chain. Returns self for fluent chaining."""
        if profile_name not in self._profile_names:
            self._profile_names.append(profile_name)
        return self

    def remove(self, profile_name: str) -> "Chain":
        """Remove a profile from the chain if present."""
        self._profile_names = [n for n in self._profile_names if n != profile_name]
        return self

    @property
    def profile_names(self) -> List[str]:
        return list(self._profile_names)

    # ------------------------------------------------------------------
    # Resolution
    # ------------------------------------------------------------------

    def resolve(self) -> Dict[str, str]:
        """Merge all profiles in order; later profiles override earlier ones."""
        merged: Dict[str, str] = {}
        for name in self._profile_names:
            profile = Profile.load(name, self.profiles_dir)
            merged.update(profile.resolve(self.profiles_dir))
        return merged

    def apply_to_env(self) -> None:
        """Export the resolved chain into the current process environment."""
        import os
        for key, value in self.resolve().items():
            os.environ[key] = value

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {"profiles": self._profile_names}

    @classmethod
    def from_dict(cls, data: dict, profiles_dir: Path = DEFAULT_PROFILES_DIR) -> "Chain":
        chain = cls(profiles_dir=profiles_dir)
        for name in data.get("profiles", []):
            chain.add(name)
        return chain

    def __repr__(self) -> str:
        return f"Chain(profiles={self._profile_names!r})"
