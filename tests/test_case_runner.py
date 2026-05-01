import csv
import json
import subprocess
import sys
from pathlib import Path

from aspen_runtime.executor import AspenPlanExecutor
from case_builder.blank_builder import BlankAspenBuilder
from process_model.loader import load_process_case


def test_dry_run_executor_writes_report_and_results(tmp_path):
    process_case = load_process_case(Path("templates/distillation/benzene_toluene.yml"))
    plan = BlankAspenBuilder(output_dir=tmp_path).plan(process_case)

    report = AspenPlanExecutor(runtime_mode="dry-run", output_root=tmp_path).execute(plan)

    assert report.success is True
    assert report.report_path.exists()
    assert report.results_path.exists()
    assert report.report_path.parent.name == "blank-dry-run"
    payload = json.loads(report.report_path.read_text(encoding="utf-8"))
    assert payload["case_name"] == "benzene_toluene_distillation"
    assert payload["runtime_mode"] == "dry-run"
    assert payload["steps"][0]["status"] == "success"

    with report.results_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["case_name"] == "benzene_toluene_distillation"
    assert rows[0]["execution_status"] == "dry-run"


def test_case_run_cli_completes_dry_run(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "main.py",
            "case-run",
            "--config",
            "templates/distillation/benzene_toluene.yml",
            "--mode",
            "blank",
            "--runtime-mode",
            "dry-run",
            "--output-dir",
            str(tmp_path),
        ],
        text=True,
        capture_output=True,
        timeout=15,
    )

    assert result.returncode == 0
    assert "Execution completed: success" in result.stdout
    assert "run_report.json" in result.stdout
