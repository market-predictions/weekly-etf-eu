from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pricing.ucits_close_price_multi_source import build_results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--basket", default="config/ucits_close_price_validation_basket.yml")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--report-date")
    parser.add_argument("--output-dir", default="output/pricing")
    parser.add_argument("--pause-seconds", type=float, default=15.0)
    parser.add_argument("--rate-limit-cooldown-seconds", type=float, default=600.0)
    parser.add_argument("--max-attempts", type=int, default=2)
    parser.add_argument("--rate-limit-mode", choices=("stop", "sleep"), default="stop")
    args = parser.parse_args()

    report_date = args.report_date or os.environ.get("REPORT_DATE")
    yahoo_rate_limit_mode = args.rate_limit_mode
    if os.environ.get("WP11_RUN_ID"):
        yahoo_rate_limit_mode = "sleep"

    build_results(
        basket_path=Path(args.basket),
        run_id=args.run_id,
        output_dir=Path(args.output_dir),
        report_date=report_date,
        pause_seconds=args.pause_seconds,
        rate_limit_cooldown_seconds=args.rate_limit_cooldown_seconds,
        max_attempts=args.max_attempts,
        yahoo_rate_limit_mode=yahoo_rate_limit_mode,
    )


if __name__ == "__main__":
    main()
