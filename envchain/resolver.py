"""Resolver module for envchain.

Resolves the final environment variable map by merging profiles in a chain,
with optional secret injection from a Vault.
"""

from typing import Optional

from envchain.chain import Chain
from envchain.profile import Profile, ProfileError
from envchain.vault import Vault, VaultError


class ResolverError(Exception):
    """Raised when resolution of a chain fails."""


class Resolver:
    """Resolves environment variables for a given Chain.

    Profiles are merged in order; later profiles override earlier ones.
    Vault secrets are injected for values matching the pattern ``vault:<key>``.
    """

    VAULT_PREFIX = "vault:"

    def __init__(self, chain: Chain, profiles_dir: str, vault: Optional[Vault] = None):
        self.chain = chain
        self.profiles_dir = profiles_dir
        self.vault = vault

    def resolve(self) -> dict:
        """Return the merged environment variable mapping for the chain.

        Raises:
            ResolverError: If a referenced profile cannot be loaded or a vault
                           secret cannot be found.
        """
        merged: dict = {}

        for name in self.chain.profile_names:
            try:
                profile = Profile.load(name, self.profiles_dir)
            except ProfileError as exc:
                raise ResolverError(
                    f"Failed to load profile '{name}': {exc}"
                ) from exc
            merged.update(profile.all())

        resolved: dict = {}
        for key, value in merged.items():
            if isinstance(value, str) and value.startswith(self.VAULT_PREFIX):
                secret_key = value[len(self.VAULT_PREFIX):]
                resolved[key] = self._resolve_secret(secret_key)
            else:
                resolved[key] = value

        return resolved

    def _resolve_secret(self, secret_key: str) -> str:
        """Fetch *secret_key* from the vault.

        Raises:
            ResolverError: If no vault is configured or the key is missing.
        """
        if self.vault is None:
            raise ResolverError(
                f"Cannot resolve vault secret '{secret_key}': no vault configured."
            )
        value = self.vault.get(secret_key)
        if value is None:
            raise ResolverError(
                f"Vault secret '{secret_key}' not found."
            )
        return value
