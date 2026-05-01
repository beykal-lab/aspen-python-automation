from pathlib import Path

from process_model.loader import load_process_case
from process_model.validation import validate_process_case


def test_loads_benzene_toluene_template():
    case = load_process_case(Path("templates/distillation/benzene_toluene.yml"))

    assert case.case.name == "benzene_toluene_distillation"
    assert case.components == ["BENZENE", "TOLUENE"]
    assert case.streams["FEED"].flow_kmol_hr == 100
    assert case.units["TOWER"].type == "RADFRAC"


def test_validates_required_distillation_nodes():
    case = load_process_case(Path("templates/distillation/benzene_toluene.yml"))

    result = validate_process_case(case)

    assert result.valid is True
    assert result.errors == []


def test_reports_invalid_feed_composition_sum(tmp_path):
    config = tmp_path / "bad_case.yml"
    config.write_text(
        """
case:
  name: bad_case
  mode: template
components:
  - BENZENE
  - TOLUENE
streams:
  FEED:
    temperature_c: 25
    pressure_bar: 1
    flow_kmol_hr: 100
    composition:
      BENZENE: 0.8
      TOLUENE: 0.4
units:
  TOWER:
    type: RADFRAC
    stages: 30
    feed_stage: 15
    pressure_bar: 1
    reflux_ratio: 2.0
products:
  DIST:
    target_component: BENZENE
    purity_min: 0.95
  BOTTOM:
    target_component: TOLUENE
    purity_min: 0.95
""",
        encoding="utf-8",
    )
    case = load_process_case(config)

    result = validate_process_case(case)

    assert result.valid is False
    assert "FEED composition must sum to 1.0" in result.errors
