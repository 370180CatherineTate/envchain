"""Main CLI entry point for envchain."""

import argparse
import sys

from envchain import cli_export, cli_import, cli_inspect, cli_vault, cli_profile


def build_parser():
    parser = argparse.ArgumentParser(
        prog="envchain",
        description="Manage and chain environment variable profiles with secret injection.",
    )
    subparsers = parser.add_subparsers(dest="cmd", required=True)

    cli_export.build_parser(subparsers)
    cli_import.build_parser(subparsers)
    cli_inspect.build_parser(subparsers)
    cli_vault.build_parser(subparsers)
    cli_profile.build_parser(subparsers)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.cmd == "export":
        cli_export.run(args)
    elif args.cmd == "import":
        cli_import.run(args)
    elif args.cmd == "inspect":
        cli_inspect.run(args)
    elif args.cmd == "vault":
        cli_vault.run(args)
    elif args.cmd == "profile":
        cli_profile.run(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
