"""CLI subcommand for managing vault secrets."""

import argparse
import sys
from pathlib import Path

from envchain.vault import Vault, VaultError


def build_parser(subparsers):
    parser = subparsers.add_parser(
        "vault",
        help="Manage secrets in the local vault",
    )
    sub = parser.add_subparsers(dest="vault_cmd", required=True)

    # vault set <key> <value>
    p_set = sub.add_parser("set", help="Set a secret in the vault")
    p_set.add_argument("key", help="Secret key")
    p_set.add_argument("value", help="Secret value")

    # vault get <key>
    p_get = sub.add_parser("get", help="Get a secret from the vault")
    p_get.add_argument("key", help="Secret key")

    # vault delete <key>
    p_del = sub.add_parser("delete", help="Delete a secret from the vault")
    p_del.add_argument("key", help="Secret key")

    # vault list
    sub.add_parser("list", help="List all secret keys in the vault")

    return parser


def run(args, vault_dir=None):
    kwargs = {"vault_dir": vault_dir} if vault_dir else {}
    try:
        vault = Vault(**kwargs)
    except VaultError as exc:
        print(f"vault error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.vault_cmd == "set":
        vault.set(args.key, args.value)
        vault.save()
        print(f"Secret '{args.key}' saved.")

    elif args.vault_cmd == "get":
        value = vault.get(args.key)
        if value is None:
            print(f"Secret '{args.key}' not found.", file=sys.stderr)
            sys.exit(1)
        print(value)

    elif args.vault_cmd == "delete":
        try:
            vault.delete(args.key)
            vault.save()
            print(f"Secret '{args.key}' deleted.")
        except VaultError as exc:
            print(f"vault error: {exc}", file=sys.stderr)
            sys.exit(1)

    elif args.vault_cmd == "list":
        keys = vault.keys()
        if not keys:
            print("(no secrets stored)")
        else:
            for key in sorted(keys):
                print(key)
