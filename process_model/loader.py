"""Load process definitions from YAML files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from process_model.models import CaseMetadata, ProcessCase, ProductSpec, StreamSpec, UnitSpec


def _required_mapping(data: dict[str, Any], key: str, path: Path) -> dict[str, Any]:
    value = data.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected mapping at '{key}'")
    return value


def load_process_case(path: Path) -> ProcessCase:
    """Load a process case YAML file into dataclasses."""
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: expected YAML mapping")

    case_data = _required_mapping(raw, "case", path)
    streams_data = _required_mapping(raw, "streams", path)
    units_data = _required_mapping(raw, "units", path)
    products_data = _required_mapping(raw, "products", path)
    components = raw.get("components")
    if not isinstance(components, list) or not all(isinstance(item, str) for item in components):
        raise ValueError(f"{path}: expected list of component names")

    streams = {
        name: StreamSpec(
            temperature_c=float(values["temperature_c"]),
            pressure_bar=float(values["pressure_bar"]),
            flow_kmol_hr=float(values["flow_kmol_hr"]),
            composition={component: float(fraction) for component, fraction in values["composition"].items()},
        )
        for name, values in streams_data.items()
    }
    units = {
        name: UnitSpec(
            type=str(values["type"]),
            stages=int(values["stages"]),
            feed_stage=int(values["feed_stage"]),
            pressure_bar=float(values["pressure_bar"]),
            reflux_ratio=float(values["reflux_ratio"]),
        )
        for name, values in units_data.items()
    }
    products = {
        name: ProductSpec(
            target_component=str(values["target_component"]),
            purity_min=float(values["purity_min"]),
        )
        for name, values in products_data.items()
    }

    return ProcessCase(
        case=CaseMetadata(
            name=str(case_data["name"]),
            mode=str(case_data.get("mode", "template")),
            description=str(case_data.get("description", "")),
        ),
        components=components,
        streams=streams,
        units=units,
        products=products,
        source_path=str(path),
    )
