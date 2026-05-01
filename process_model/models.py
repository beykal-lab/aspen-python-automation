"""Dataclasses for Aspen-independent process definitions."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CaseMetadata:
    name: str
    mode: str
    description: str = ""


@dataclass(frozen=True)
class StreamSpec:
    temperature_c: float
    pressure_bar: float
    flow_kmol_hr: float
    composition: dict[str, float]


@dataclass(frozen=True)
class UnitSpec:
    type: str
    stages: int
    feed_stage: int
    pressure_bar: float
    reflux_ratio: float


@dataclass(frozen=True)
class ProductSpec:
    target_component: str
    purity_min: float


@dataclass(frozen=True)
class ProcessCase:
    case: CaseMetadata
    components: list[str]
    streams: dict[str, StreamSpec]
    units: dict[str, UnitSpec]
    products: dict[str, ProductSpec]
    source_path: str = ""


@dataclass(frozen=True)
class ValidationResult:
    errors: list[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not self.errors
