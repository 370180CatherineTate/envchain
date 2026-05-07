"""Inspector module for listing and describing profiles, chains, and vault keys."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from envchain.profile import Profile, ProfileError
from envchain.chain import Chain
from envchain.vault import Vault


class InspectorError(Exception):
    """Raised when inspection fails."""


class Inspector:
    """Provides introspection utilities for envchain resources."""

    def __init__(self, profiles_dir: Path, vault_dir: Path) -> None:
        self.profiles_dir = Path(profiles_dir)
        self.vault_dir = Path(vault_dir)

    def list_profiles(self) -> List[str]:
        """Return sorted list of available profile names."""
        if not self.profiles_dir.exists():
            return []
        return sorted(
            p.stem for p in self.profiles_dir.glob("*.json")
        )

    def list_chains(self) -> List[str]:
        """Return sorted list of available chain names."""
        if not self.profiles_dir.exists():
            return []
        return sorted(
            p.stem for p in self.profiles_dir.glob("*.chain.json")
        )

    def describe_profile(self, name: str) -> dict:
        """Return metadata and keys for a given profile."""
        try:
            profile = Profile.load(name, self.profiles_dir)
        except ProfileError as exc:
            raise InspectorError(str(exc)) from exc
        return {
            "name": name,
            "keys": sorted(profile.all_keys()),
            "count": len(profile.all_keys()),
        }

    def describe_chain(self, name: str) -> dict:
        """Return metadata and profile list for a given chain."""
        try:
            chain = Chain.load(name, self.profiles_dir)
        except Exception as exc:
            raise InspectorError(f"Chain '{name}' not found: {exc}") from exc
        return {
            "name": name,
            "profiles": chain.profile_names(),
            "count": len(chain.profile_names()),
        }

    def list_vault_keys(self) -> List[str]:
        """Return sorted list of keys stored in the vault."""
        vault = Vault(self.vault_dir)
        return sorted(vault.keys())
