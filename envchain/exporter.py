"""Export resolved environment variables in various shell formats."""

from __future__ import annotations

from typing import Dict, Literal

ShellFormat = Literal["bash", "fish", "dotenv"]


class ExporterError(Exception):
    """Raised when export fails."""


class Exporter:
    """Formats resolved environment variables for shell consumption."""

    SUPPORTED_FORMATS: tuple[str, ...] = ("bash", "fish", "dotenv")

    def __init__(self, env: Dict[str, str]) -> None:
        if not isinstance(env, dict):
            raise ExporterError("env must be a dict")
        self._env = env

    def export(self, fmt: ShellFormat = "bash") -> str:
        """Return a string of export statements in the requested format."""
        if fmt not in self.SUPPORTED_FORMATS:
            raise ExporterError(
                f"Unsupported format '{fmt}'. "
                f"Choose from: {', '.join(self.SUPPORTED_FORMATS)}"
            )
        method = getattr(self, f"_fmt_{fmt}")
        return method()

    def _fmt_bash(self) -> str:
        lines = []
        for key, value in sorted(self._env.items()):
            escaped = value.replace("\\", "\\\\").replace('"', '\\"')
            lines.append(f'export {key}="{escaped}"')
        return "\n".join(lines)

    def _fmt_fish(self) -> str:
        lines = []
        for key, value in sorted(self._env.items()):
            escaped = value.replace("\\", "\\\\").replace('"', '\\"')
            lines.append(f'set -x {key} "{escaped}"')
        return "\n".join(lines)

    def _fmt_dotenv(self) -> str:
        lines = []
        for key, value in sorted(self._env.items()):
            escaped = value.replace("\\", "\\\\").replace('"', '\\"')
            lines.append(f'{key}="{escaped}"')
        return "\n".join(lines)
