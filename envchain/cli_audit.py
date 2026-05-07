"""CLI sub-command: envchain audit — view the audit log."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from envchain.auditor import Auditor, AuditorError


def build_parser(subparsers=None):
    description = "View or clear the envchain audit log."
    if subparsers is not None:
        parser = subparsers.add_parser("audit", help=description)
    else:
        parser = argparse.ArgumentParser(prog="envchain audit", description=description)

    sub = parser.add_subparsers(dest="audit_cmd")

    list_p = sub.add_parser("list", help="List audit log entries")
    list_p.add_argument(
        "--event", metavar="EVENT", default=None,
        help="Filter by event type (e.g. resolve, export)"
    )
    list_p.add_argument(
        "--data-dir", metavar="DIR", default=None,
        help="Path to envchain data directory"
    )

    clear_p = sub.add_parser("clear", help="Clear all audit log entries")
    clear_p.add_argument(
        "--data-dir", metavar="DIR", default=None,
        help="Path to envchain data directory"
    )

    return parser


def _default_data_dir() -> Path:
    return Path.home() / ".envchain"


def run(args: argparse.Namespace) -> None:
    data_dir = Path(args.data_dir) if args.data_dir else _default_data_dir()
    auditor = Auditor(data_dir)

    if args.audit_cmd == "list":
        entries = (
            auditor.filter_by_event(args.event)
            if args.event
            else auditor.read_all()
        )
        if not entries:
            print("No audit log entries found.")
            return
        for entry in entries:
            ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(entry["timestamp"]))
            event = entry.get("event", "unknown")
            details = {k: v for k, v in entry.items() if k not in ("timestamp", "event")}
            detail_str = "  ".join(f"{k}={v}" for k, v in details.items())
            print(f"[{ts}] {event}  {detail_str}")

    elif args.audit_cmd == "clear":
        auditor.clear()
        print("Audit log cleared.")

    else:
        build_parser().print_help()
        sys.exit(1)
