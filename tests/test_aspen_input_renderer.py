from pathlib import Path

from aspen_runtime.input_renderer import render_distillation_inp
from process_model.loader import load_process_case


def test_renders_benzene_toluene_distillation_input():
    process_case = load_process_case(Path("templates/distillation/benzene_toluene.yml"))

    text = render_distillation_inp(process_case)

    assert "COMPONENTS" in text
    assert "BENZENE BENZENE" in text
    assert "TOLUENE TOLUENE" in text
    assert "BLOCK TOWER RADFRAC" in text
    assert "FEEDS FEED 15" in text
    assert "COL-SPECS MOLE-RR=2.0" in text
