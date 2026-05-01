"""Validation rules for process definitions."""

from __future__ import annotations

from process_model.models import ProcessCase, ValidationResult


def validate_process_case(process_case: ProcessCase) -> ValidationResult:
    """Validate the first supported binary distillation process shape."""
    errors: list[str] = []

    if "FEED" not in process_case.streams:
        errors.append("missing required stream: FEED")
    if "TOWER" not in process_case.units:
        errors.append("missing required unit: TOWER")
    for product_name in ("DIST", "BOTTOM"):
        if product_name not in process_case.products:
            errors.append(f"missing required product: {product_name}")

    if len(process_case.components) < 2:
        errors.append("at least two components are required")

    feed = process_case.streams.get("FEED")
    if feed is not None:
        if feed.flow_kmol_hr <= 0:
            errors.append("FEED flow_kmol_hr must be positive")
        composition_sum = sum(feed.composition.values())
        if abs(composition_sum - 1.0) > 1e-6:
            errors.append("FEED composition must sum to 1.0")
        for component in feed.composition:
            if component not in process_case.components:
                errors.append(f"FEED composition component is not declared: {component}")

    tower = process_case.units.get("TOWER")
    if tower is not None:
        if tower.type.upper() != "RADFRAC":
            errors.append("TOWER type must be RADFRAC")
        if tower.stages <= 1:
            errors.append("TOWER stages must be greater than 1")
        if tower.feed_stage < 1 or tower.feed_stage > tower.stages:
            errors.append("TOWER feed_stage must be between 1 and stages")
        if tower.reflux_ratio <= 0:
            errors.append("TOWER reflux_ratio must be positive")

    for product_name, product in process_case.products.items():
        if product.target_component not in process_case.components:
            errors.append(f"{product_name} target_component is not declared: {product.target_component}")
        if product.purity_min <= 0 or product.purity_min > 1:
            errors.append(f"{product_name} purity_min must be in (0, 1]")

    return ValidationResult(errors=errors)
