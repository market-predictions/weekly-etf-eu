from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pricing.ucits_price_provider_engine import build_provider_qualification


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", default="config/ucits_price_provider_registry.yml")
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--providers", default="")
    parser.add_argument("--verify-identity", action="store_true")
    parser.add_argument("--pause-seconds", type=float, default=1.0)
    parser.add_argument("--max-close-age-days", type=int, default=7)
    parser.add_argument("--agreement-tolerance-pct", type=float, default=1.0)
    args = parser.parse_args()
    providers = [item.strip() for item in args.providers.split(",") if item.strip()] or None
    build_provider_qualification(
        registry_path=Path(args.registry),
        report_date=date.fromisoformat(args.report_date),
        output_path=Path(args.output),
        providers=providers,
        verify_identity=args.verify_identity,
        pause_seconds=args.pause_seconds,
        max_close_age_days=args.max_close_age_days,
        agreement_tolerance_pct=args.agreement_tolerance_pct,
    )


if __name__ == "__main__":
    main()
