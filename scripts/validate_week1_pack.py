"""Validate the competition week-1 control pack."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from competition_pack.validation import validate_week1_pack


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Repository root to validate. Defaults to current directory.",
    )
    args = parser.parse_args()

    errors = validate_week1_pack(args.root)
    if errors:
        print("Week-1 pack validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Week-1 pack validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
