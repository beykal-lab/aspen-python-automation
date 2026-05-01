"""Render Aspen Plus input files from process definitions."""

from __future__ import annotations

from process_model.models import ProcessCase


def render_distillation_inp(process_case: ProcessCase) -> str:
    """Render the first supported binary RadFrac case as Aspen input text."""
    feed = process_case.streams["FEED"]
    tower = process_case.units["TOWER"]
    distillate_flow = feed.flow_kmol_hr / 2

    component_lines = []
    for index, component in enumerate(process_case.components):
        suffix = " /" if index < len(process_case.components) - 1 else ""
        component_lines.append(f"    {component} {component}{suffix}")

    composition_parts = [
        f"{component} {fraction:g}" for component, fraction in feed.composition.items()
    ]
    composition_line = " / ".join(composition_parts)

    return "\n".join(
        [
            f"TITLE '{process_case.case.name}'",
            "",
            "IN-UNITS SI",
            "",
            "DEF-STREAMS CONVEN ALL",
            "",
            "DATABANKS 'APV150 PURE41' / 'APV150 AQUEOUS' / 'APV150 INORGANIC'",
            "",
            "PROP-SOURCES 'APV150 PURE41' / 'APV150 AQUEOUS' / 'APV150 INORGANIC'",
            "",
            "COMPONENTS",
            *component_lines,
            "",
            "SOLVE",
            "    RUN-MODE MODE=SIM",
            "",
            "PROPERTIES NRTL",
            "",
            "FLOWSHEET",
            "    BLOCK TOWER IN=FEED OUT=DIST BOTTOM",
            "",
            "STREAM FEED",
            (
                "    SUBSTREAM MIXED "
                f"TEMP={feed.temperature_c:g} "
                f"PRES={feed.pressure_bar:g} "
                f"MOLE-FLOW={feed.flow_kmol_hr:g}"
            ),
            f"    MOLE-FRAC {composition_line}",
            "",
            "BLOCK TOWER RADFRAC",
            f"    PARAM NSTAGE={tower.stages} ALGORITHM=STANDARD MAXOL=25 DAMPING=NONE",
            "    COL-CONFIG CONDENSER=TOTAL",
            f"    FEEDS FEED {tower.feed_stage}",
            f"    PRODUCTS DIST 1 L / BOTTOM {tower.stages} L",
            f"    P-SPEC 1 {tower.pressure_bar:g}",
            f"    COL-SPECS MOLE-RR={tower.reflux_ratio:.1f} MOLE-D={distillate_flow:.1f}",
            "    TRAY-REPORT TRAY-OPTION=ALL-TRAYS",
            "",
            "STREAM-REPOR MOLEFLOW MASSFLOW MOLEFRAC MASSFRAC",
            "",
        ]
    )
