"""Execute Aspen build plans in dry-run or COM-backed modes."""

from __future__ import annotations

import csv
import json
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from aspen_runtime.adapter import AspenComAdapter
from aspen_runtime.connection import AspenConnection
from aspen_runtime.input_renderer import render_distillation_inp
from case_builder.base import BuildAction, BuildPlan


@dataclass(frozen=True)
class StepResult:
    name: str
    status: str
    message: str
    payload: dict[str, object]


@dataclass(frozen=True)
class ExecutionReport:
    case_name: str
    runtime_mode: str
    success: bool
    steps: list[StepResult]
    report_path: Path
    results_path: Path


class AspenPlanExecutor:
    """Run a build plan and persist user-readable execution artifacts."""

    def __init__(
        self,
        runtime_mode: str = "dry-run",
        output_root: Path = Path("cases/generated"),
        adapter: object | None = None,
    ) -> None:
        if runtime_mode not in {"dry-run", "detect", "execute"}:
            raise ValueError("runtime_mode must be one of: dry-run, detect, execute")
        self.runtime_mode = runtime_mode
        self.output_root = output_root
        self.adapter = adapter
        self._active_case_path: Path | None = None
        self._blank_input_path: Path | None = None
        self._blank_process_payload: dict[str, object] = {}
        self._results: dict[str, object] = {}

    def execute(self, plan: BuildPlan) -> ExecutionReport:
        run_dir = self.output_root / plan.case_name / f"{plan.mode}-{self.runtime_mode}"
        run_dir.mkdir(parents=True, exist_ok=True)

        steps: list[StepResult] = []
        try:
            for action in plan.actions:
                result = self._execute_action(plan, action, run_dir)
                steps.append(result)
                if result.status == "failed":
                    break
        finally:
            if self.runtime_mode == "execute" and self.adapter is not None:
                close = getattr(self.adapter, "close", None)
                if callable(close):
                    close()

        accepted_statuses = {"success", "skipped"} if self.runtime_mode != "execute" else {"success"}
        success = all(step.status in accepted_statuses for step in steps)
        report_path = run_dir / "run_report.json"
        results_path = run_dir / "results.csv"
        self._write_report(plan, steps, success, report_path)
        self._write_results(plan, success, results_path)

        return ExecutionReport(
            case_name=plan.case_name,
            runtime_mode=self.runtime_mode,
            success=success,
            steps=steps,
            report_path=report_path,
            results_path=results_path,
        )

    def _execute_action(self, plan: BuildPlan, action: BuildAction, run_dir: Path) -> StepResult:
        if self.runtime_mode == "dry-run":
            return StepResult(
                name=action.name,
                status="success",
                message=f"dry-run completed for action: {action.name}",
                payload=action.payload,
            )

        if self.runtime_mode == "detect":
            status = AspenConnection(mode="detect").check()
            return StepResult(
                name=action.name,
                status="skipped" if status.available else "failed",
                message=status.message,
                payload=action.payload,
            )

        if action.name == "copy-template":
            return self._copy_template(action)

        if self.runtime_mode == "execute":
            return self._execute_com_action(plan, action, run_dir)

        return StepResult(
            name=action.name,
            status="skipped",
            message="execute mode has not implemented this Aspen action yet.",
            payload=action.payload,
        )

    def _execute_com_action(self, plan: BuildPlan, action: BuildAction, run_dir: Path) -> StepResult:
        adapter = self._adapter()
        try:
            if action.name == "start-aspen":
                message = adapter.start()
            elif action.name == "open-case":
                path = Path(str(action.payload["path"]))
                self._active_case_path = path
                message = adapter.open_archive(path)
            elif action.name == "create-new-simulation":
                self._blank_input_path = run_dir / f"{plan.case_name}.inp"
                message = f"prepared generated Aspen input file: {self._blank_input_path}"
            elif plan.mode == "template" and action.name in {
                "write-components",
                "write-feed",
                "write-tower",
                "write-products",
            }:
                message = "template action payload acknowledged for current Aspen case."
            elif action.name in {"add-components", "set-property-method", "create-streams", "create-tower"}:
                self._blank_process_payload[action.name] = action.payload
                message = "captured action payload for generated Aspen input file."
            elif action.name in {"connect-streams", "write-feed", "write-tower"}:
                self._blank_process_payload[action.name] = action.payload
                message = "captured action payload for generated Aspen input file."
            elif action.name == "run-initialization":
                input_path = self._write_blank_input_file(plan, run_dir)
                message = adapter.open_input_file(input_path)
                message = f"{message}; {adapter.run()}"
            elif action.name == "run-aspen":
                message = adapter.run()
            elif action.name == "save-case":
                path = Path(str(action.payload["path"]))
                self._active_case_path = path
                message = adapter.write_archive(path)
                if plan.mode == "blank":
                    self._results = self._extract_stream_results(adapter)
                    action.payload.update(self._results)
                    message = f"{message}; extracted {len(self._results)} Aspen Tree values."
            elif action.name == "extract-results":
                self._results = self._extract_stream_results(adapter)
                action.payload.update(self._results)
                message = f"extracted {len(self._results)} Aspen Tree values."
            else:
                return StepResult(
                    name=action.name,
                    status="failed",
                    message=f"unsupported execute action: {action.name}",
                    payload=action.payload,
                )
        except Exception as exc:
            return StepResult(
                name=action.name,
                status="failed",
                message=f"{type(exc).__name__}: {exc}",
                payload=action.payload,
            )

        return StepResult(
            name=action.name,
            status="success",
            message=message,
            payload=action.payload,
        )

    def _extract_stream_results(self, adapter) -> dict[str, object]:
        results: dict[str, object] = {}
        paths = {
            "DIST_BENZENE_MOLEFRAC": r"\Data\Streams\DIST\Output\MOLEFRAC\MIXED\BENZENE",
            "DIST_TOLUENE_MOLEFRAC": r"\Data\Streams\DIST\Output\MOLEFRAC\MIXED\TOLUENE",
            "BOTTOM_BENZENE_MOLEFRAC": r"\Data\Streams\BOTTOM\Output\MOLEFRAC\MIXED\BENZENE",
            "BOTTOM_TOLUENE_MOLEFRAC": r"\Data\Streams\BOTTOM\Output\MOLEFRAC\MIXED\TOLUENE",
            "DIST_BENZENE_MOLEFLOW": r"\Data\Streams\DIST\Output\MOLEFLOW\MIXED\BENZENE",
            "BOTTOM_TOLUENE_MOLEFLOW": r"\Data\Streams\BOTTOM\Output\MOLEFLOW\MIXED\TOLUENE",
            "DIST_TEMP_OUT": r"\Data\Streams\DIST\Output\TEMP_OUT\MIXED",
            "BOTTOM_TEMP_OUT": r"\Data\Streams\BOTTOM\Output\TEMP_OUT\MIXED",
            "DIST_PRES_OUT": r"\Data\Streams\DIST\Output\PRES_OUT\MIXED",
            "BOTTOM_PRES_OUT": r"\Data\Streams\BOTTOM\Output\PRES_OUT\MIXED",
        }
        for label, path in paths.items():
            try:
                results[label] = adapter.read_node(path)
            except Exception as exc:
                results[label] = f"{type(exc).__name__}: {exc}"
        return results

    def _adapter(self):
        if self.adapter is None:
            self.adapter = AspenComAdapter(visible=True)
        return self.adapter

    def _write_blank_input_file(self, plan: BuildPlan, run_dir: Path) -> Path:
        from process_model.loader import load_process_case

        source = plan.actions[1].payload.get("source_config")
        if not source:
            raise ValueError("blank execution requires source_config in create-new-simulation action")
        process_case = load_process_case(Path(str(source)))
        input_path = self._blank_input_path or (run_dir / f"{plan.case_name}.inp")
        input_path.write_text(render_distillation_inp(process_case), encoding="utf-8")
        return input_path

    def _copy_template(self, action: BuildAction) -> StepResult:
        source = Path(str(action.payload["source"]))
        target = Path(str(action.payload["target"]))
        if not source.exists():
            return StepResult(
                name=action.name,
                status="failed",
                message=f"template file does not exist: {source}",
                payload=action.payload,
            )

        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        return StepResult(
            name=action.name,
            status="success",
            message=f"copied template to {target}",
            payload=action.payload,
        )

    def _write_report(
        self,
        plan: BuildPlan,
        steps: list[StepResult],
        success: bool,
        report_path: Path,
    ) -> None:
        payload = {
            "case_name": plan.case_name,
            "builder_mode": plan.mode,
            "runtime_mode": self.runtime_mode,
            "success": success,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "steps": [asdict(step) for step in steps],
        }
        report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _write_results(self, plan: BuildPlan, success: bool, results_path: Path) -> None:
        with results_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "case_name",
                    "builder_mode",
                    "runtime_mode",
                    "execution_status",
                    "converged",
                    "DIST_BENZENE_MOLEFRAC",
                    "BOTTOM_TOLUENE_MOLEFRAC",
                    "DIST_BENZENE_MOLEFLOW",
                    "BOTTOM_TOLUENE_MOLEFLOW",
                    "DIST_TEMP_OUT",
                    "BOTTOM_TEMP_OUT",
                ],
            )
            writer.writeheader()
            writer.writerow(
                {
                    "case_name": plan.case_name,
                    "builder_mode": plan.mode,
                    "runtime_mode": self.runtime_mode,
                    "execution_status": "dry-run" if self.runtime_mode == "dry-run" else "executed",
                    "converged": "unknown" if self.runtime_mode == "dry-run" else str(success).lower(),
                    "DIST_BENZENE_MOLEFRAC": self._results.get("DIST_BENZENE_MOLEFRAC", ""),
                    "BOTTOM_TOLUENE_MOLEFRAC": self._results.get("BOTTOM_TOLUENE_MOLEFRAC", ""),
                    "DIST_BENZENE_MOLEFLOW": self._results.get("DIST_BENZENE_MOLEFLOW", ""),
                    "BOTTOM_TOLUENE_MOLEFLOW": self._results.get("BOTTOM_TOLUENE_MOLEFLOW", ""),
                    "DIST_TEMP_OUT": self._results.get("DIST_TEMP_OUT", ""),
                    "BOTTOM_TEMP_OUT": self._results.get("BOTTOM_TEMP_OUT", ""),
                }
            )
