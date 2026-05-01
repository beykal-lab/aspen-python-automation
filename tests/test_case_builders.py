from pathlib import Path

from case_builder.blank_builder import BlankAspenBuilder
from case_builder.template_builder import TemplateBkpBuilder
from process_model.loader import load_process_case


def test_template_builder_plans_copy_open_write_run_save():
    case = load_process_case(Path("templates/distillation/benzene_toluene.yml"))
    plan = TemplateBkpBuilder(template_path=Path("templates/aspen/distillation_base.bkp")).plan(case)

    assert plan.mode == "template"
    assert [action.name for action in plan.actions][:2] == ["copy-template", "open-case"]
    assert "write-feed" in [action.name for action in plan.actions]
    assert "run-aspen" in [action.name for action in plan.actions]
    assert plan.actions[-1].name == "extract-results"


def test_blank_builder_plans_new_case_creation():
    case = load_process_case(Path("templates/distillation/benzene_toluene.yml"))
    plan = BlankAspenBuilder().plan(case)

    assert plan.mode == "blank"
    assert [action.name for action in plan.actions][:3] == [
        "start-aspen",
        "create-new-simulation",
        "add-components",
    ]
    assert "connect-streams" in [action.name for action in plan.actions]
    assert plan.actions[-1].name == "save-case"
