"""CLI subcommand for managing profiles."""

import argparse
import sys

from envchain.profile import Profile, ProfileError


def build_parser(subparsers):
    parser = subparsers.add_parser(
        "profile",
        help="Manage environment variable profiles",
    )
    sub = parser.add_subparsers(dest="profile_cmd", required=True)

    # set
    p_set = sub.add_parser("set", help="Set a variable in a profile")
    p_set.add_argument("profile", help="Profile name")
    p_set.add_argument("key", help="Variable name")
    p_set.add_argument("value", help="Variable value")

    # get
    p_get = sub.add_parser("get", help="Get a variable from a profile")
    p_get.add_argument("profile", help="Profile name")
    p_get.add_argument("key", help="Variable name")

    # unset
    p_unset = sub.add_parser("unset", help="Remove a variable from a profile")
    p_unset.add_argument("profile", help="Profile name")
    p_unset.add_argument("key", help="Variable name")

    # list
    p_list = sub.add_parser("list", help="List variables in a profile")
    p_list.add_argument("profile", help="Profile name")

    return parser


def run(args, profiles_dir=None):
    kwargs = {"profiles_dir": profiles_dir} if profiles_dir else {}

    try:
        profile = Profile(args.profile, **kwargs)
    except ProfileError as exc:
        if args.profile_cmd not in ("set",):
            print(f"error: {exc}", file=sys.stderr)
            sys.exit(1)
        profile = Profile(args.profile, **kwargs)

    if args.profile_cmd == "set":
        profile.set(args.key, args.value)
        profile.save()
        print(f"Set {args.key} in profile '{args.profile}'.")

    elif args.profile_cmd == "get":
        try:
            profile.load()
        except ProfileError as exc:
            print(f"error: {exc}", file=sys.stderr)
            sys.exit(1)
        value = profile.get(args.key)
        if value is None:
            print(f"error: key '{args.key}' not found in profile '{args.profile}'", file=sys.stderr)
            sys.exit(1)
        print(value)

    elif args.profile_cmd == "unset":
        try:
            profile.load()
        except ProfileError as exc:
            print(f"error: {exc}", file=sys.stderr)
            sys.exit(1)
        profile.unset(args.key)
        profile.save()
        print(f"Unset {args.key} from profile '{args.profile}'.")

    elif args.profile_cmd == "list":
        try:
            profile.load()
        except ProfileError as exc:
            print(f"error: {exc}", file=sys.stderr)
            sys.exit(1)
        keys = profile.keys()
        if not keys:
            print(f"Profile '{args.profile}' is empty.")
        else:
            for key in sorted(keys):
                print(key)
