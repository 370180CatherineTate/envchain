"""CLI helper: resolve a chain and print export statements."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envchain.chain import Chain
from envchain.exporter import Exporter, ExporterError
from envchain.resolver import Resolver, ResolverError

DEFAULT_PROFILES_DIR = Path.home() / ".envchain" / "profiles"
DEFAULT_VAULT_DIR = Path.home() / ".envchain" / "vault"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envchain export",
        description="Resolve and export environment variables from a chain.",
    )
    parser.add_argument("chain_name", help="Name of the chain to export")
    parser.add_argument(
        "--format",
        "-f",
        choices=["bash", "fish", "dotenv"],
        default="bash",
        help="Output format (default: bash)",
    )
    parser.add_argument(
        "--profiles-dir",
        default=str(DEFAULT_PROFILES_DIR),
        help="Directory containing profile files",
    )
    parser.add_argument(
        "--vault-dir",
        default=str(DEFAULT_VAULT_DIR),
        help="Directory containing vault files",
    )
    return parser


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    profiles_dir = Path(args.profiles_dir)
    vault_dir = Path(args.vault_dir)

    try:
        chain = Chain.load(args.chain_name, profiles_dir=profiles_dir)
        resolver = Resolver(
            profile_names=chain.profile_names,
            profiles_dir=profiles_dir,
            vault_dir=vault_dir,
        )
        env = resolver.resolve()
        output = Exporter(env).export(args.format)
        if output:
            print(output)
        return 0
    except (ResolverError, ExporterError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(run())
