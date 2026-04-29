"""Command-line entry point for this competition workspace."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from competition_pack.validation import validate_week1_pack


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Week-1 chemical design competition workspace tools."
    )
    subparsers = parser.add_subparsers(dest="command")

    validate_parser = subparsers.add_parser(
        "validate-week1",
        help="Validate the Week-1 control pack YAML and CSV files.",
    )
    validate_parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Repository root to validate. Defaults to current directory.",
    )

    legacy_parser = subparsers.add_parser(
        "legacy-aspen-sample",
        help="Run the original Aspen LHS sample script.",
    )
    legacy_parser.add_argument(
        "--script",
        type=Path,
        default=Path("Aspen_to_Data-driven optimization.py"),
        help="Legacy script path. Kept explicit to avoid starting Aspen on import.",
    )
    return parser


def run_validate_week1(root: Path) -> int:
    errors = validate_week1_pack(root)
    if errors:
        print("Week-1 pack validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Week-1 pack validation passed.")
    return 0


def run_legacy_script(script: Path) -> int:
    if not script.exists():
        print(f"Legacy script not found: {script}")
        return 1
    return subprocess.call([sys.executable, str(script)])


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "validate-week1":
        return run_validate_week1(args.root)
    if args.command == "legacy-aspen-sample":
        return run_legacy_script(args.script)

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
