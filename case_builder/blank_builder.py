"""Blank Aspen case builder."""

from __future__ import annotations

from pathlib import Path

from case_builder.base import BuildAction, BuildPlan
from process_model.models import ProcessCase


class BlankAspenBuilder:
    """Plan actions for creating an Aspen case from an empty document."""

    def __init__(self, output_dir: Path = Path("cases/generated")) -> None:
        self.output_dir = output_dir

    def plan(self, process_case: ProcessCase) -> BuildPlan:
        output_path = self.output_dir / f"{process_case.case.name}-blank.bkp"
        tower = process_case.units["TOWER"]

        actions = [
            BuildAction(
                name="start-aspen",
                description="Start Aspen and make the automation session available.",
                payload={},
            ),
            BuildAction(
                name="create-new-simulation",
                description="Create a new empty Aspen simulation document.",
                payload={"case_name": process_case.case.name},
            ),
            BuildAction(
                name="add-components",
                description="Add declared chemical components to the simulation.",
                payload={"components": process_case.components},
            ),
            BuildAction(
                name="set-property-method",
                description="Set the first-slice default property method.",
                payload={"property_method": "NRTL"},
            ),
            BuildAction(
                name="create-streams",
                description="Create FEED, DIST, and BOTTOM material streams.",
                payload={"streams": ["FEED", "DIST", "BOTTOM"]},
            ),
            BuildAction(
                name="create-tower",
                description="Create the TOWER RadFrac block.",
                payload={"unit": "TOWER", "type": tower.type},
            ),
            BuildAction(
                name="connect-streams",
                description="Connect FEED into TOWER and connect DIST/BOTTOM products.",
                payload={"feed": "FEED", "unit": "TOWER", "products": ["DIST", "BOTTOM"]},
            ),
            BuildAction(
                name="write-feed",
                description="Write FEED conditions and composition.",
                payload={"stream": "FEED", "values": process_case.streams["FEED"].__dict__},
            ),
            BuildAction(
                name="write-tower",
                description="Write TOWER design parameters.",
                payload={"unit": "TOWER", "values": tower.__dict__},
            ),
            BuildAction(
                name="run-initialization",
                description="Run Aspen initialization after creating the flowsheet.",
                payload={},
            ),
            BuildAction(
                name="save-case",
                description="Save the blank-built Aspen backup case.",
                payload={"path": str(output_path)},
            ),
        ]
        return BuildPlan(mode="blank", case_name=process_case.case.name, actions=actions)
