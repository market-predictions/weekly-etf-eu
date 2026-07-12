from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_repair_pdf_validator_can_run_as_a_script() -> None:
    completed = subprocess.run(
        [sys.executable, "tools/validate_etf_eu_routine_pdf_client_grade_v2.py", "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert "--pdf" in completed.stdout
