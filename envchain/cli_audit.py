import argparse
import os
import sys
from pathlib import Path

from envchain.auditor import Auditor, AuditorError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envchain audit",
        description="View and manage the envchain audit log",
    )
    sub = parser.add_subparsers(dest="audit_cmd", required=True)

    # list
    ls = sub.add_parser("list", help="List audit log entries")
    ls.add_argument(
        "--event",
        metavar="EVENT",
        help="Filter by event type (e.g. export, import, vault_set)",
    )
    ls.add_argument(
        "--limit",
        type=int,
        default=50,
        metavar="N",
        help="Maximum number of entries to show (default: 50)",
    )

    # clear
    sub.add_parser("clear", help="Clear all audit log entries")

    return parser


def _default_data_dir() -> Path:
    xdg = os.environ.get("XDG_DATA_HOME")
    if xdg:
        return Path(xdg) / "envchain"
    return Path.home() / ".local" / "share" / "envchain"


def run(argv: list[str] | None = None, data_dir: Path | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    audit_dir = (data_dir or _default_data_dir()) / "audit"
    auditor = Auditor(audit_dir)

    try:
        if args.audit_cmd == "list":
            entries = auditor.read_all(event=args.event)
            entries = entries[-args.limit :]
            if not entries:
                print("No audit log entries found.")
                return
            for entry in entries:
                ts = entry.get("timestamp", "?")
                event = entry.get("event", "?")
                detail = entry.get("detail", "")
                print(f"[{ts}] {event}  {detail}")

        elif args.audit_cmd == "clear":
            auditor.clear()
            print("Audit log cleared.")

    except AuditorError as exc:
        print(f"audit error: {exc}", file=sys.stderr)
        sys.exit(1)
