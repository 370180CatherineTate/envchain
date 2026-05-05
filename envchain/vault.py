"""Local vault for storing and retrieving secrets securely."""

import json
import os
from pathlib import Path
from typing import Optional

DEFAULT_VAULT_DIR = Path.home() / ".envchain" / "vaults"


class VaultError(Exception):
    """Raised when a vault operation fails."""


class Vault:
    """A simple file-based local vault for storing secrets."""

    def __init__(self, name: str, vault_dir: Optional[Path] = None):
        self.name = name
        self.vault_dir = vault_dir or DEFAULT_VAULT_DIR
        self.vault_path = self.vault_dir / f"{name}.json"
        self._secrets: dict[str, str] = {}

    def _ensure_vault_dir(self) -> None:
        self.vault_dir.mkdir(parents=True, exist_ok=True)

    def load(self) -> None:
        """Load secrets from the vault file."""
        if not self.vault_path.exists():
            self._secrets = {}
            return
        try:
            with open(self.vault_path, "r") as f:
                self._secrets = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            raise VaultError(f"Failed to load vault '{self.name}': {e}") from e

    def save(self) -> None:
        """Persist secrets to the vault file."""
        self._ensure_vault_dir()
        try:
            with open(self.vault_path, "w") as f:
                json.dump(self._secrets, f, indent=2)
            os.chmod(self.vault_path, 0o600)
        except OSError as e:
            raise VaultError(f"Failed to save vault '{self.name}': {e}") from e

    def set(self, key: str, value: str) -> None:
        """Store a secret in the vault."""
        self._secrets[key] = value

    def get(self, key: str) -> Optional[str]:
        """Retrieve a secret by key, or None if not found."""
        return self._secrets.get(key)

    def delete(self, key: str) -> bool:
        """Remove a secret by key. Returns True if it existed."""
        if key in self._secrets:
            del self._secrets[key]
            return True
        return False

    def list_keys(self) -> list[str]:
        """Return all secret keys stored in the vault."""
        return list(self._secrets.keys())

    def destroy(self) -> None:
        """Delete the vault file from disk."""
        if self.vault_path.exists():
            self.vault_path.unlink()
        self._secrets = {}
