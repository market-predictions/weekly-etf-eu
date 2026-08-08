from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--basket", default="config/ucits_close_price_validation_basket.yml")
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--qualification-output", required=True)
    parser.add_argument("--provider-registry", default="config/ucits_price_provider_registry.yml")
    parser.add_argument("--portfolio-state", default="output/etf_eu_portfolio_state.json")
    parser.add_argument("--provider-cache", default="config/etf_eu_provider_close_cache_20260731.json")
    args = parser.parse_args()

    output = Path(args.output)
    qualification_output = Path(args.qualification_output)
    expected_output = output.parent / f"ucits_close_price_validation_basket_results_{args.run_id}.json"
    expected_qualification = output.parent / f"ucits_price_provider_qualification_{args.run_id}.json"
    if output != expected_output:
        raise SystemExit(f"WP11A_COMPAT_NONCANONICAL_OUTPUT:{output}:expected={expected_output}")
    if qualification_output != expected_qualification:
        raise SystemExit(
            f"WP11A_COMPAT_NONCANONICAL_QUALIFICATION_OUTPUT:{qualification_output}:expected={expected_qualification}"
        )

    command = [
        sys.executable,
        "pricing/build_ucits_close_price_validation_basket_results.py",
        "--basket",
        args.basket,
        "--provider-registry",
        args.provider_registry,
        "--portfolio-state",
        args.portfolio_state,
        "--provider-cache",
        args.provider_cache,
        "--run-id",
        args.run_id,
        "--report-date",
        args.report_date,
        "--output-dir",
        str(output.parent),
        "--verify-identity",
        "--pause-seconds",
        "0.2",
        "--agreement-tolerance-pct",
        "1.0",
        "--require-funded-consensus",
    ]
    print("WP11A_COMPAT_ROUTE", " ".join(command), flush=True)
    subprocess.run(command, cwd=str(ROOT), check=True)

    if not output.exists() or not qualification_output.exists():
        raise SystemExit("WP11A_COMPAT_EXPECTED_ARTIFACTS_MISSING")
    print(
        "WP11A_COMPAT_OK"
        f" | output={output}"
        f" | qualification={qualification_output}"
        f" | report_date={args.report_date}"
        f" | run_id={args.run_id}"
    )


if __name__ == "__main__":
    main()
