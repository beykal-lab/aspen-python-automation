"""Template `.bkp` case builder."""

from __future__ import annotations

from pathlib import Path

from case_builder.base import BuildAction, BuildPlan
from process_model.models import ProcessCase


class TemplateBkpBuilder:
    """Plan actions for modifying a known Aspen backup template."""

    def __init__(self, template_path: Path, output_dir: Path = Path("cases/generated")) -> None:
        self.template_path = template_path
        self.output_dir = output_dir

    def plan(self, process_case: ProcessCase) -> BuildPlan:
        output_path = self.output_dir / f"{process_case.case.name}.bkp"
        feed = process_case.streams["FEED"]
        tower = process_case.units["TOWER"]

        actions = [
            BuildAction(
                name="copy-template",
                description="Copy the source Aspen backup template to a generated case path.",
                payload={"source": str(self.template_path), "target": str(output_path)},
            ),
            BuildAction(
                name="open-case",
                description="Open the generated Aspen backup file.",
                payload={"path": str(output_path)},
            ),
            BuildAction(
                name="write-components",
                description="Confirm the process components expected by the template.",
                payload={"components": process_case.components},
            ),
            BuildAction(
                name="write-feed",
                description="Write FEED stream temperature, pressure, flow, and composition.",
                payload={
                    "stream": "FEED",
                    "temperature_c": feed.temperature_c,
                    "pressure_bar": feed.pressure_bar,
                    "flow_kmol_hr": feed.flow_kmol_hr,
                    "composition": feed.composition,
                },
            ),
            BuildAction(
                name="write-tower",
                description="Write TOWER stages, feed stage, pressure, and reflux ratio.",
                payload={
                    "unit": "TOWER",
                    "type": tower.type,
                    "stages": tower.stages,
                    "feed_stage": tower.feed_stage,
                    "pressure_bar": tower.pressure_bar,
                    "reflux_ratio": tower.reflux_ratio,
                },
            ),
            BuildAction(
                name="write-products",
                description="Write product purity targets for DIST and BOTTOM.",
                payload={"products": {name: spec.__dict__ for name, spec in process_case.products.items()}},
            ),
            BuildAction(
                name="run-aspen",
                description="Run the Aspen simulation for the generated case.",
                payload={},
            ),
            BuildAction(
                name="save-case",
                description="Save the generated Aspen backup case.",
                payload={"path": str(output_path)},
            ),
            BuildAction(
                name="extract-results",
                description="Extract convergence, purity, duty, and flow results.",
                payload={"streams": ["DIST", "BOTTOM"], "unit": "TOWER"},
            ),
        ]
        return BuildPlan(mode="template", case_name=process_case.case.name, actions=actions)
