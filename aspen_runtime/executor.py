"""Execute Aspen build plans in dry-run or COM-backed modes."""

from __future__ import annotations

import csv
import json
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from aspen_runtime.connection import AspenConnection
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

    def __init__(self, runtime_mode: str = "dry-run", output_root: Path = Path("cases/generated")) -> None:
        if runtime_mode not in {"dry-run", "detect", "execute"}:
            raise ValueError("runtime_mode must be one of: dry-run, detect, execute")
        self.runtime_mode = runtime_mode
        self.output_root = output_root

    def execute(self, plan: BuildPlan) -> ExecutionReport:
        run_dir = self.output_root / plan.case_name / f"{plan.mode}-{self.runtime_mode}"
        run_dir.mkdir(parents=True, exist_ok=True)

        steps: list[StepResult] = []
        for action in plan.actions:
            result = self._execute_action(action)
            steps.append(result)
            if result.status == "failed":
                break

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

    def _execute_action(self, action: BuildAction) -> StepResult:
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

        if action.name in {"open-case", "start-aspen", "create-new-simulation"}:
            status = AspenConnection(mode="execute").check()
            return StepResult(
                name=action.name,
                status="success" if status.available else "failed",
                message=status.message,
                payload=action.payload,
            )

        return StepResult(
            name=action.name,
            status="skipped",
            message="execute mode has not implemented this Aspen action yet.",
            payload=action.payload,
        )

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
                }
            )
