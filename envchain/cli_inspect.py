"""CLI subcommand for inspecting profiles and chains."""

import argparse
import sys

from envchain.inspector import Inspector, InspectorError


def build_parser(subparsers=None):
    description = "Inspect profiles and chains"
    if subparsers is not None:
        parser = subparsers.add_parser("inspect", help=description)
    else:
        parser = argparse.ArgumentParser(description=description)

    sub = parser.add_subparsers(dest="inspect_cmd", required=True)

    # list subcommand
    list_parser = sub.add_parser("list", help="List profiles or chains")
    list_parser.add_argument(
        "kind",
        choices=["profiles", "chains"],
        help="What to list",
    )

    # describe subcommand
    describe_parser = sub.add_parser("describe", help="Describe a profile or chain")
    describe_parser.add_argument(
        "kind",
        choices=["profile", "chain"],
        help="Kind of object to describe",
    )
    describe_parser.add_argument("name", help="Name of the profile or chain")

    parser.add_argument(
        "--profiles-dir",
        default=None,
        help="Directory where profiles are stored",
    )
    parser.add_argument(
        "--chains-dir",
        default=None,
        help="Directory where chains are stored",
    )

    return parser


def run(args, out=None):
    if out is None:
        out = sys.stdout

    kwargs = {}
    if args.profiles_dir:
        kwargs["profiles_dir"] = args.profiles_dir
    if args.chains_dir:
        kwargs["chains_dir"] = args.chains_dir

    try:
        inspector = Inspector(**kwargs)

        if args.inspect_cmd == "list":
            if args.kind == "profiles":
                names = inspector.list_profiles()
            else:
                names = inspector.list_chains()
            for name in sorted(names):
                out.write(name + "\n")

        elif args.inspect_cmd == "describe":
            if args.kind == "profile":
                info = inspector.describe_profile(args.name)
            else:
                info = inspector.describe_chain(args.name)
            for key, value in info.items():
                out.write(f"{key}: {value}\n")

    except InspectorError as exc:
        sys.stderr.write(f"Error: {exc}\n")
        sys.exit(1)
