"""Top-level CLI dispatcher for envchain."""

import argparse
import sys

from envchain import cli_export, cli_import


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envchain",
        description="Manage and chain environment variable profiles",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # export sub-command
    export_parser = subparsers.add_parser(
        "export", help="Export resolved environment variables"
    )
    export_parser.set_defaults(_runner=cli_export.run)

    # import sub-command
    import_parser = subparsers.add_parser(
        "import", help="Import environment variables into a profile"
    )
    import_parser.set_defaults(_runner=cli_import.run)

    return parser


def main(argv=None):
    """Entry point: dispatch to the correct sub-command runner."""
    if argv is None:
        argv = sys.argv[1:]

    if not argv:
        build_parser().print_help()
        sys.exit(0)

    command = argv[0]
    rest = argv[1:]

    if command == "export":
        cli_export.run(rest)
    elif command == "import":
        cli_import.run(rest)
    else:
        build_parser().print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
