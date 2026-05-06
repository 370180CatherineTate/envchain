"""CLI entry point for importing environment variables into profiles."""

import argparse
import os
import sys

from envchain.importer import Importer, ImporterError


DEFAULT_PROFILES_DIR = os.path.expanduser("~/.envchain/profiles")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envchain import",
        description="Import environment variables into a profile",
    )
    parser.add_argument("profile", help="Target profile name")
    subparsers = parser.add_subparsers(dest="source", required=True)

    dotenv_p = subparsers.add_parser("dotenv", help="Import from a .env file")
    dotenv_p.add_argument("file", help="Path to the .env file")
    dotenv_p.add_argument(
        "--overwrite", action="store_true", help="Overwrite existing keys"
    )

    env_p = subparsers.add_parser("env", help="Import from current shell environment")
    env_p.add_argument("keys", nargs="+", help="Environment variable keys to import")
    env_p.add_argument(
        "--overwrite", action="store_true", help="Overwrite existing keys"
    )

    parser.add_argument(
        "--profiles-dir",
        default=DEFAULT_PROFILES_DIR,
        help="Directory where profiles are stored",
    )
    return parser


def run(argv=None, profiles_dir: str = None):
    parser = build_parser()
    args = parser.parse_args(argv)

    pdir = profiles_dir or args.profiles_dir
    importer = Importer(pdir)

    try:
        if args.source == "dotenv":
            profile = importer.from_dotenv(args.file, args.profile, overwrite=args.overwrite)
            print(f"Imported {len(profile.all())} variable(s) into profile '{args.profile}'")
        elif args.source == "env":
            profile = importer.from_env(args.keys, args.profile, overwrite=args.overwrite)
            print(f"Imported variable(s) into profile '{args.profile}'")
    except ImporterError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run()
