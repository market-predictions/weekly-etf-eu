#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    checks = (
        root / "tools" / "validate_etf_eu_repository_boundary.py",
        root / "tools" / "validate_etf_eu_workflow_authority.py",
    )
    missing = [str(path.relative_to(root)) for path in checks if not path.exists()]
    if missing:
        raise SystemExit("ETF_EU_PRODUCT_BOUNDARY_CHECK_MISSING | " + ",".join(missing))
    for check in checks:
        completed = subprocess.run([sys.executable, str(check)], cwd=root, check=False)
        if completed.returncode != 0:
            raise SystemExit(f"ETF_EU_PRODUCT_BOUNDARY_FAILED | check={check.relative_to(root)} | rc={completed.returncode}")
    print("ETF_EU_PRODUCT_BOUNDARY_PASS")


if __name__ == "__main__":
    main()
