"""Shared builder interfaces and action-plan models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from process_model.models import ProcessCase


@dataclass(frozen=True)
class BuildAction:
    name: str
    description: str
    payload: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class BuildPlan:
    mode: str
    case_name: str
    actions: list[BuildAction]


class CaseBuilder(Protocol):
    def plan(self, process_case: ProcessCase) -> BuildPlan:
        """Return an ordered Aspen build plan for a validated process case."""
