# Dual-Engine Aspen Modeling Design

## Goal

Build a reusable chemical-design competition automation platform that supports
both stable template-driven `.bkp` generation and progressive blank-Aspen case
creation from a shared process definition.

## Context

The current project has a safe CLI, a Week-1 competition validation module, and
a clean Git boundary for templates, docs, tests, and generated artifacts. The
next phase must avoid returning to hard-coded one-off Aspen scripts. Aspen COM
operations should live behind a narrow runtime interface, while competition
logic should operate on project-owned process definitions.

## Scope

This design covers the first production-shaped slice:

- A process model that validates distillation process definitions.
- A shared case-builder interface.
- A template `.bkp` builder that plans copy/open/write/run/save actions.
- A blank-Aspen builder that plans component, property, stream, block, and
  connection creation actions.
- An Aspen runtime interface that can run in dry-run mode without Aspen.
- An execution layer that persists run reports and result summaries for every
  builder/runtime combination.
- CLI commands that expose validation, planning, and Aspen availability checks.
- Tests that run in CI without Aspen installed.

This design does not promise full Aspen graphical flowsheet creation in every
Aspen version. Blank-case creation is implemented as a capability-driven path:
when a required COM capability is unavailable, the tool reports the unsupported
step and recommends the template builder.

## Architecture

```text
process_case.yml
  -> process_model.loader
  -> process_model.validation
  -> case_builder.base.CaseBuilder
      -> case_builder.template_builder.TemplateBkpBuilder
      -> case_builder.blank_builder.BlankAspenBuilder
  -> aspen_runtime.connection.AspenConnection
  -> aspen_runtime.case.AspenCase
  -> results and run logs
```

The process model is Aspen-independent. Builders convert a validated process
definition into an ordered action plan. Runtime classes execute those actions
against Aspen when available, or return dry-run diagnostics when Aspen is not
available.

## Process Definition

The first supported process shape is a binary distillation case:

```yaml
case:
  name: benzene_toluene_distillation
  mode: template
  description: Benzene/toluene split for competition automation testing.

components:
  - BENZENE
  - TOLUENE

streams:
  FEED:
    temperature_c: 25
    pressure_bar: 1
    flow_kmol_hr: 100
    composition:
      BENZENE: 0.5
      TOLUENE: 0.5

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
```

Required logical nodes are `FEED`, `TOWER`, `DIST`, and `BOTTOM`. The validator
checks component presence, feed composition closure, positive flow, valid stage
numbers, and product target components.

## Builder Behavior

`TemplateBkpBuilder` uses a known Aspen template case. It produces actions:

1. Copy source template to an output case path.
2. Open the copied case.
3. Write component, feed, tower, and product specification values through Aspen
   Tree paths.
4. Run Aspen.
5. Save the case.
6. Extract configured results.

`BlankAspenBuilder` starts from an empty Aspen document. It produces actions:

1. Start Aspen.
2. Create a new simulation.
3. Add components.
4. Set the property method.
5. Create FEED, DIST, and BOTTOM streams.
6. Create the TOWER block.
7. Connect the streams.
8. Write feed and tower parameters.
9. Run Aspen initialization.
10. Save the case.

Both builders expose the same interface and return a `BuildPlan` object before
execution, so CLI and future UI code can show the user what will happen.

## Runtime Behavior

The Aspen runtime has three modes:

- `dry-run`: never imports `win32com`, suitable for CI and planning.
- `detect`: attempts to import and dispatch Aspen, then reports availability.
- `execute`: performs COM operations and returns structured success or failure.

Runtime errors are represented as structured status objects with a step name,
message, and optional Aspen Tree path. CLI output should be readable by a user
who is not debugging Python internals.

## CLI

The first slice adds:

```powershell
python main.py case-validate --config templates/distillation/benzene_toluene.yml
python main.py case-plan --config templates/distillation/benzene_toluene.yml --mode template
python main.py case-plan --config templates/distillation/benzene_toluene.yml --mode blank
python main.py case-run --config templates/distillation/benzene_toluene.yml --mode template --runtime-mode dry-run
python main.py case-run --config templates/distillation/benzene_toluene.yml --mode blank --runtime-mode dry-run
python main.py aspen-check
```

Existing commands remain supported:

```powershell
python main.py validate-week1 --root .
python main.py legacy-aspen-sample --script "Aspen_to_Data-driven optimization.py"
```

## Testing

Tests must not require Aspen. The first slice verifies:

- Process definitions load and validate.
- Invalid definitions produce specific messages.
- Template and blank builders generate different but valid action plans.
- Template and blank dry-runs generate separate report directories so their
  outputs do not overwrite each other.
- `aspen-check` reports unavailable Aspen cleanly when `win32com` is absent.
- Existing Week-1 validation and help behavior remain intact.

## Git Policy

Track process templates, source code, tests, docs, and CI configuration. Do not
track generated `.bkp` files, run outputs, logs, downloaded PDFs, or external
repository clones. Each future feature branch should produce one coherent local
commit and, when push permissions are unavailable, an exported patch file.
