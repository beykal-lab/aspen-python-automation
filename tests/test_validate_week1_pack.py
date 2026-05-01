import subprocess
import sys
from pathlib import Path

from competition_pack.validation import validate_csv_width, validate_week1_pack


def test_week1_pack_validates_current_workspace():
    result = validate_week1_pack(Path("."))

    assert result == []


def test_csv_width_check_reports_malformed_rows(tmp_path):
    malformed = tmp_path / "bad.csv"
    malformed.write_text("a,b,c\n1,2\n", encoding="utf-8")

    result = validate_csv_width(malformed)

    assert result == ["bad.csv: row 2 has 2 columns, expected 3"]


def test_main_help_does_not_start_aspen():
    result = subprocess.run(
        [sys.executable, "main.py", "--help"],
        text=True,
        capture_output=True,
        timeout=15,
    )

    assert result.returncode == 0
    assert "week-1" in result.stdout.lower()


def test_legacy_validation_script_still_runs():
    result = subprocess.run(
        [sys.executable, "scripts/validate_week1_pack.py", "--root", "."],
        text=True,
        capture_output=True,
        timeout=15,
    )

    assert result.returncode == 0
    assert "passed" in result.stdout.lower()
