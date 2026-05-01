import subprocess
import sys

from aspen_runtime.connection import AspenConnection


def test_aspen_connection_dry_run_is_available_without_com():
    status = AspenConnection(mode="dry-run").check()

    assert status.available is True
    assert status.mode == "dry-run"
    assert "dry-run" in status.message


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


def test_case_validate_cli_accepts_template():
    result = subprocess.run(
        [
            sys.executable,
            "main.py",
            "case-validate",
            "--config",
            "templates/distillation/benzene_toluene.yml",
        ],
        text=True,
        capture_output=True,
        timeout=15,
    )

    assert result.returncode == 0
    assert "Process case validation passed." in result.stdout
