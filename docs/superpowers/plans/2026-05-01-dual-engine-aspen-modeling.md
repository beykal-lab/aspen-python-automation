# Dual-Engine Aspen Modeling Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first testable slice of a dual-engine Aspen modeling platform with process validation, template planning, blank-case planning, and Aspen availability checks.

**Architecture:** The implementation keeps process modeling independent from Aspen COM. Builders convert validated process definitions into ordered build actions. Aspen runtime code exposes dry-run and detection behavior so CI can test the system without Aspen installed.

**Tech Stack:** Python 3, argparse, dataclasses, pathlib, PyYAML, pytest, optional pywin32 on Windows.

---

## File Structure

- `process_model/__init__.py`: package marker and exported names.
- `process_model/models.py`: dataclasses for process cases, streams, units, products, and validation results.
- `process_model/loader.py`: YAML loading and dataclass conversion.
- `process_model/validation.py`: domain validation for binary distillation cases.
- `case_builder/__init__.py`: package marker and exported names.
- `case_builder/base.py`: shared `BuildAction`, `BuildPlan`, and `CaseBuilder` interface.
- `case_builder/template_builder.py`: template `.bkp` action planner.
- `case_builder/blank_builder.py`: blank Aspen action planner.
- `aspen_runtime/__init__.py`: package marker and exported names.
- `aspen_runtime/connection.py`: Aspen availability detection and dry-run status.
- `aspen_runtime/executor.py`: build-plan execution and report persistence.
- `templates/distillation/benzene_toluene.yml`: canonical process case.
- `tests/test_process_model.py`: process loading and validation tests.
- `tests/test_case_builders.py`: builder plan tests.
- `tests/test_aspen_runtime_cli.py`: Aspen check and CLI tests.
- `tests/test_case_runner.py`: end-to-end dry-run execution tests.
- `main.py`: CLI commands for case validation, planning, and Aspen detection.

## Task 1: Process Model

**Files:**
- Create: `process_model/__init__.py`
- Create: `process_model/models.py`
- Create: `process_model/loader.py`
- Create: `process_model/validation.py`
- Create: `templates/distillation/benzene_toluene.yml`
- Test: `tests/test_process_model.py`

- [ ] **Step 1: Write failing tests**

```python
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
```

- [ ] **Step 2: Run tests and verify failure**

Run: `python -m pytest tests/test_process_model.py -q`

Expected: failure because `process_model` does not exist.

- [ ] **Step 3: Implement minimal process dataclasses, loader, validator, and template**

Create focused dataclasses, load YAML with `yaml.safe_load`, and validate required logical nodes `FEED`, `TOWER`, `DIST`, and `BOTTOM`.

- [ ] **Step 4: Verify tests pass**

Run: `python -m pytest tests/test_process_model.py -q`

Expected: `2 passed`.

## Task 2: Builder Action Plans

**Files:**
- Create: `case_builder/__init__.py`
- Create: `case_builder/base.py`
- Create: `case_builder/template_builder.py`
- Create: `case_builder/blank_builder.py`
- Test: `tests/test_case_builders.py`

- [ ] **Step 1: Write failing tests**

```python
from pathlib import Path

from case_builder.blank_builder import BlankAspenBuilder
from case_builder.template_builder import TemplateBkpBuilder
from process_model.loader import load_process_case


def test_template_builder_plans_copy_open_write_run_save():
    case = load_process_case(Path("templates/distillation/benzene_toluene.yml"))
    plan = TemplateBkpBuilder(template_path=Path("templates/aspen/distillation_base.bkp")).plan(case)

    assert plan.mode == "template"
    assert [action.name for action in plan.actions][:2] == ["copy-template", "open-case"]
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
```

- [ ] **Step 2: Run tests and verify failure**

Run: `python -m pytest tests/test_case_builders.py -q`

Expected: failure because `case_builder` does not exist.

- [ ] **Step 3: Implement action-plan dataclasses and builders**

Use `BuildAction(name: str, description: str, payload: dict[str, object])` and
`BuildPlan(mode: str, case_name: str, actions: list[BuildAction])`.

- [ ] **Step 4: Verify tests pass**

Run: `python -m pytest tests/test_case_builders.py -q`

Expected: `2 passed`.

## Task 3: Aspen Runtime and CLI

**Files:**
- Create: `aspen_runtime/__init__.py`
- Create: `aspen_runtime/connection.py`
- Modify: `main.py`
- Test: `tests/test_aspen_runtime_cli.py`

- [ ] **Step 1: Write failing tests**

```python
import subprocess
import sys

from aspen_runtime.connection import AspenConnection


def test_aspen_connection_dry_run_is_available_without_com():
    status = AspenConnection(mode="dry-run").check()

    assert status.available is True
    assert status.mode == "dry-run"


def test_case_plan_cli_prints_template_actions():
    result = subprocess.run(
        [
            sys.executable,
            "main.py",
            "case-plan",
            "--config",
            "templates/distillation/benzene_toluene.yml",
            "--mode",
            "template",
        ],
        text=True,
        capture_output=True,
        timeout=15,
    )

    assert result.returncode == 0
    assert "copy-template" in result.stdout
    assert "run-aspen" in result.stdout
```

- [ ] **Step 2: Run tests and verify failure**

Run: `python -m pytest tests/test_aspen_runtime_cli.py -q`

Expected: failure because `aspen_runtime` and CLI commands do not exist.

- [ ] **Step 3: Implement runtime detection and CLI commands**

Add `aspen-check`, `case-validate`, and `case-plan` subcommands. Keep old
commands unchanged.

- [ ] **Step 4: Verify tests pass**

Run: `python -m pytest tests/test_aspen_runtime_cli.py -q`

Expected: tests pass whether or not Aspen is installed.

## Task 4: Full Verification and Commit

**Files:**
- Modify only files touched in Tasks 1-3.

- [ ] **Step 1: Run complete test suite**

Run: `python -m pytest`

Expected: all tests pass.

- [ ] **Step 2: Run CLI smoke tests**

Run:

```powershell
python main.py --help
python main.py case-validate --config templates/distillation/benzene_toluene.yml
python main.py case-plan --config templates/distillation/benzene_toluene.yml --mode template
python main.py case-plan --config templates/distillation/benzene_toluene.yml --mode blank
python main.py aspen-check --mode dry-run
```

Expected: each command exits with code 0.

- [ ] **Step 3: Commit**

Run:

```powershell
git add docs/superpowers process_model case_builder aspen_runtime templates/distillation tests main.py
git commit -m "Add dual-engine Aspen modeling foundation"
```

Expected: one coherent commit on `codex/dual-engine-aspen-modeling`.

## Task 5: Dry-Run Execution Layer

**Files:**
- Create: `aspen_runtime/executor.py`
- Modify: `aspen_runtime/__init__.py`
- Modify: `main.py`
- Test: `tests/test_case_runner.py`

- [ ] **Step 1: Write failing tests**

Write tests that execute the blank builder in `dry-run` mode and assert that
`run_report.json` and `results.csv` are created. Add a CLI test for
`python main.py case-run --config templates/distillation/benzene_toluene.yml --mode blank --runtime-mode dry-run`.

- [ ] **Step 2: Run tests and verify failure**

Run: `python -m pytest tests/test_case_runner.py -q`

Expected: failure because `aspen_runtime.executor` and `case-run` do not exist.

- [ ] **Step 3: Implement executor and CLI command**

Implement `AspenPlanExecutor.execute(plan)` so dry-run executes every action,
persists `run_report.json`, writes `results.csv`, and separates output by
`<builder-mode>-<runtime-mode>`.

- [ ] **Step 4: Verify tests and smoke runs**

Run:

```powershell
python -m pytest
python main.py case-run --config templates/distillation/benzene_toluene.yml --mode blank --runtime-mode dry-run --output-dir cases/generated
python main.py case-run --config templates/distillation/benzene_toluene.yml --mode template --runtime-mode dry-run --output-dir cases/generated
```

Expected: all tests pass and both dry-run commands complete successfully with
separate report directories.

## Self-Review

The plan covers the design requirements for process definitions, two builder
modes, runtime detection, CLI exposure, and tests that do not require Aspen. No
implementation step depends on real Aspen being installed. The first slice
intentionally produces action plans rather than executing COM flowsheet creation,
which keeps the scope small enough to verify and extend.
