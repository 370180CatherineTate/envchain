"""Import environment variables from .env files or shell environment into profiles."""

import os
import re
from typing import Dict, Optional

from envchain.profile import Profile, ProfileError


class ImporterError(Exception):
    pass


class Importer:
    def __init__(self, profiles_dir: str):
        self.profiles_dir = profiles_dir

    def from_dotenv(self, path: str, profile_name: str, overwrite: bool = False) -> Profile:
        """Import key=value pairs from a .env file into a named profile."""
        if not os.path.isfile(path):
            raise ImporterError(f"File not found: {path}")

        env_vars = self._parse_dotenv(path)
        if not env_vars:
            raise ImporterError(f"No valid variables found in {path}")

        try:
            profile = Profile.load(profile_name, self.profiles_dir)
        except ProfileError:
            profile = Profile(profile_name, self.profiles_dir)

        for key, value in env_vars.items():
            if not overwrite and profile.get(key) is not None:
                continue
            profile.set(key, value)

        profile.save()
        return profile

    def from_env(self, keys: list, profile_name: str, overwrite: bool = False) -> Profile:
        """Import specific keys from the current shell environment into a profile."""
        try:
            profile = Profile.load(profile_name, self.profiles_dir)
        except ProfileError:
            profile = Profile(profile_name, self.profiles_dir)

        imported = 0
        for key in keys:
            value = os.environ.get(key)
            if value is None:
                continue
            if not overwrite and profile.get(key) is not None:
                continue
            profile.set(key, value)
            imported += 1

        if imported == 0:
            raise ImporterError("No matching environment variables found")

        profile.save()
        return profile

    @staticmethod
    def _parse_dotenv(path: str) -> Dict[str, str]:
        """Parse a .env file and return a dict of key-value pairs."""
        result = {}
        pattern = re.compile(
            r'^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*([^\r\n]*)'
        )
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                match = pattern.match(line)
                if match:
                    key = match.group(1)
                    value = match.group(2).strip().strip('"\'')
                    result[key] = value
        return result
