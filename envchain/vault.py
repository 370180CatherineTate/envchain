"""Local vault for storing secrets on disk with restricted permissions."""

import json
import os
import stat
from pathlib import Path

DEFAULT_VAULT_DIR = Path.home() / ".envchain" / "vault"
VAULT_FILE = "secrets.json"


class VaultError(Exception):
    """Raised on vault operation failures."""


class Vault:
    def __init__(self, vault_dir=None):
        self._vault_dir = Path(vault_dir) if vault_dir else DEFAULT_VAULT_DIR
        self._secrets: dict[str, str] = {}
        self._ensure_vault_dir()
        self.load()

    def _ensure_vault_dir(self):
        self._vault_dir.mkdir(parents=True, exist_ok=True)
        self._vault_dir.chmod(0o700)

    def load(self):
        vault_file = self._vault_dir / VAULT_FILE
        if not vault_file.exists():
            self._secrets = {}
            return
        try:
            with vault_file.open("r") as fh:
                self._secrets = json.load(fh)
        except (json.JSONDecodeError, OSError) as exc:
            raise VaultError(f"Failed to load vault: {exc}") from exc

    def save(self):
        vault_file = self._vault_dir / VAULT_FILE
        try:
            with vault_file.open("w") as fh:
                json.dump(self._secrets, fh, indent=2)
            vault_file.chmod(0o600)
        except OSError as exc:
            raise VaultError(f"Failed to save vault: {exc}") from exc

    def set(self, key: str, value: str):
        if not key:
            raise VaultError("Secret key must not be empty.")
        self._secrets[key] = value

    def get(self, key: str) -> str | None:
        return self._secrets.get(key)

    def delete(self, key: str):
        if key not in self._secrets:
            raise VaultError(f"Secret '{key}' does not exist.")
        del self._secrets[key]

    def keys(self) -> list[str]:
        return list(self._secrets.keys())

    def all_secrets(self) -> dict[str, str]:
        return dict(self._secrets)

    def __contains__(self, key: str) -> bool:
        return key in self._secrets

    def __len__(self) -> int:
        return len(self._secrets)
