"""Command-line entry point for this competition workspace."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from aspen_runtime.connection import AspenConnection
from case_builder.blank_builder import BlankAspenBuilder
from case_builder.template_builder import TemplateBkpBuilder
from competition_pack.validation import validate_week1_pack
from process_model.loader import load_process_case
from process_model.validation import validate_process_case


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

    case_validate_parser = subparsers.add_parser(
        "case-validate",
        help="Validate a process case definition.",
    )
    case_validate_parser.add_argument(
        "--config",
        type=Path,
        required=True,
        help="Process case YAML file.",
    )

    case_plan_parser = subparsers.add_parser(
        "case-plan",
        help="Print the ordered build actions for a process case.",
    )
    case_plan_parser.add_argument(
        "--config",
        type=Path,
        required=True,
        help="Process case YAML file.",
    )
    case_plan_parser.add_argument(
        "--mode",
        choices=["template", "blank"],
        default="template",
        help="Builder mode to plan.",
    )
    case_plan_parser.add_argument(
        "--template",
        type=Path,
        default=Path("templates/aspen/distillation_base.bkp"),
        help="Template .bkp path for template mode.",
    )

    aspen_check_parser = subparsers.add_parser(
        "aspen-check",
        help="Check Aspen runtime availability.",
    )
    aspen_check_parser.add_argument(
        "--mode",
        choices=["dry-run", "detect", "execute"],
        default="detect",
        help="Connection check mode.",
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


def run_case_validate(config: Path) -> int:
    process_case = load_process_case(config)
    result = validate_process_case(process_case)
    if not result.valid:
        print("Process case validation failed:")
        for error in result.errors:
            print(f"- {error}")
        return 1
    print("Process case validation passed.")
    return 0


def run_case_plan(config: Path, mode: str, template: Path) -> int:
    process_case = load_process_case(config)
    result = validate_process_case(process_case)
    if not result.valid:
        print("Process case validation failed:")
        for error in result.errors:
            print(f"- {error}")
        return 1

    if mode == "template":
        plan = TemplateBkpBuilder(template_path=template).plan(process_case)
    else:
        plan = BlankAspenBuilder().plan(process_case)

    print(f"Build plan: {plan.case_name} ({plan.mode})")
    for index, action in enumerate(plan.actions, start=1):
        print(f"{index}. {action.name}: {action.description}")
    return 0


def run_aspen_check(mode: str) -> int:
    status = AspenConnection(mode=mode).check()
    print(status.message)
    return 0 if status.available else 1


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "validate-week1":
        return run_validate_week1(args.root)
    if args.command == "legacy-aspen-sample":
        return run_legacy_script(args.script)
    if args.command == "case-validate":
        return run_case_validate(args.config)
    if args.command == "case-plan":
        return run_case_plan(args.config, args.mode, args.template)
    if args.command == "aspen-check":
        return run_aspen_check(args.mode)

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
