"""Validation helpers for the week-1 competition control pack."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import yaml


YAML_FILES = [
    Path("config/project.yml"),
    Path("config/routes.yml"),
    Path("config/economics.yml"),
    Path("config/report_outline.yml"),
    Path("data/task/task_requirements.yml"),
    Path("data/literature/literature_search_keywords.yml"),
]

CSV_FILES = [
    Path("data/literature/evidence_table_template.csv"),
    Path("data/route_selection/route_score_matrix_template.csv"),
    Path("data/market/market_research_template.csv"),
]

REQUIRED_SUBMISSION_IDS = {"A1", "A2", "A3", "A4", "A5"}
CORE_ROUTE_IDS = {"R1", "R2", "R3"}


def load_yaml(path: Path) -> Any:
    """Load a UTF-8 YAML document."""
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def validate_yaml_file(path: Path) -> list[str]:
    """Validate that a YAML file exists, parses, and is not empty."""
    if not path.exists():
        return [f"{path}: missing"]

    try:
        data = load_yaml(path)
    except Exception as exc:  # pragma: no cover - exact parser message varies.
        return [f"{path}: YAML parse error: {type(exc).__name__}: {exc}"]

    if data is None:
        return [f"{path}: parsed to empty document"]
    return []


def validate_csv_width(path: Path) -> list[str]:
    """Validate that all non-empty CSV rows have the header width."""
    if not path.exists():
        return [f"{path}: missing"]

    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = [row for row in csv.reader(handle) if row]

    if not rows:
        return [f"{path.name}: empty csv"]

    errors: list[str] = []
    expected_width = len(rows[0])
    for index, row in enumerate(rows, start=1):
        if len(row) != expected_width:
            errors.append(f"{path.name}: row {index} has {len(row)} columns, expected {expected_width}")
    return errors


def validate_submission_ids(task_requirements: dict[str, Any]) -> list[str]:
    """Validate required submission material IDs."""
    items = task_requirements["submission_materials"]["required"]
    actual_ids = {item["id"] for item in items}
    missing = sorted(REQUIRED_SUBMISSION_IDS - actual_ids)
    return [f"missing required submission id: {item_id}" for item_id in missing]


def validate_route_ids(routes_config: dict[str, Any]) -> list[str]:
    """Validate core process route IDs."""
    actual_ids = {route["id"] for route in routes_config["routes"]}
    missing = sorted(CORE_ROUTE_IDS - actual_ids)
    return [f"missing core route id: {route_id}" for route_id in missing]


def validate_economic_constants(economics: dict[str, Any]) -> list[str]:
    """Validate task-book economic constants used by the first-week pack."""
    checks = {
        "304 stainless steel price": (
            economics["equipment_material_prices"]["stainless_steel_304"]["price_cny_per_ton"],
            48000,
        ),
        "low pressure steam price": (
            economics["utilities"]["low_pressure_steam"]["price_cny_per_ton"],
            255,
        ),
        "electricity price": (
            economics["utilities"]["electricity"]["price_cny_per_kwh"],
            0.70,
        ),
    }

    errors: list[str] = []
    for label, (actual, expected) in checks.items():
        if actual != expected:
            errors.append(f"{label}: expected {expected}, got {actual}")
    return errors


def validate_week1_pack(root: Path) -> list[str]:
    """Validate all required Week-1 pack YAML and CSV files under root."""
    errors: list[str] = []

    for relative_path in YAML_FILES:
        errors.extend(validate_yaml_file(root / relative_path))

    for relative_path in CSV_FILES:
        errors.extend(validate_csv_width(root / relative_path))

    if errors:
        return errors

    task_requirements = load_yaml(root / "data/task/task_requirements.yml")
    routes_config = load_yaml(root / "config/routes.yml")
    economics = load_yaml(root / "config/economics.yml")

    errors.extend(validate_submission_ids(task_requirements))
    errors.extend(validate_route_ids(routes_config))
    errors.extend(validate_economic_constants(economics))
    return errors
