from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pricing.provider_secret_safety import enforce_provider_secret_safety
from pricing.ucits_funded_universe import resolve_provider_registry_funded_universe
from pricing.ucits_price_evidence_cache import apply_provider_evidence_cache
from pricing.ucits_price_provider_engine import (
    build_legacy_validation_artifact,
    build_provider_qualification,
)
from pricing.ucits_price_qualification_policy import apply_identity_anchor_policy


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--basket", default="config/ucits_close_price_validation_basket.yml")
    parser.add_argument("--provider-registry", default="config/ucits_price_provider_registry.yml")
    parser.add_argument("--portfolio-state", default="output/etf_eu_portfolio_state.json")
    parser.add_argument("--provider-cache", default="config/etf_eu_provider_close_cache_20260731.json")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--report-date")
    parser.add_argument("--output-dir", default="output/pricing")
    parser.add_argument("--providers", default="")
    parser.add_argument("--verify-identity", action="store_true")
    parser.add_argument("--pause-seconds", type=float, default=1.0)
    parser.add_argument("--max-close-age-days", type=int, default=7)
    parser.add_argument("--agreement-tolerance-pct", type=float, default=1.0)
    parser.add_argument("--require-funded-consensus", action="store_true")
    # Retained compatibility arguments; provider-specific throttling now lives in adapters.
    parser.add_argument("--rate-limit-cooldown-seconds", type=float, default=600.0)
    parser.add_argument("--max-attempts", type=int, default=1)
    parser.add_argument("--rate-limit-mode", choices=("stop", "sleep"), default="stop")
    args = parser.parse_args()

    secret_safety = enforce_provider_secret_safety()
    report_date = date.fromisoformat(args.report_date or os.environ.get("REPORT_DATE") or date.today().isoformat())
    providers = [item.strip() for item in args.providers.split(",") if item.strip()] or None
    output_dir = Path(args.output_dir)
    qualification_path = output_dir / f"ucits_price_provider_qualification_{args.run_id}.json"
    legacy_path = output_dir / f"ucits_close_price_validation_basket_results_{args.run_id}.json"
    resolved_registry_path = output_dir / f"ucits_price_provider_registry_resolved_{args.run_id}.yml"

    funded_authority = resolve_provider_registry_funded_universe(
        registry_path=Path(args.provider_registry),
        portfolio_state_path=Path(args.portfolio_state),
        output_path=resolved_registry_path,
    )
    build_provider_qualification(
        registry_path=resolved_registry_path,
        report_date=report_date,
        output_path=qualification_path,
        providers=providers,
        verify_identity=args.verify_identity,
        pause_seconds=args.pause_seconds,
        max_close_age_days=args.max_close_age_days,
        agreement_tolerance_pct=args.agreement_tolerance_pct,
    )
    cache_path = Path(args.provider_cache) if args.provider_cache else None
    apply_provider_evidence_cache(qualification_path, cache_path)
    qualification = apply_identity_anchor_policy(qualification_path)
    qualification["funded_universe_authority"] = funded_authority
    qualification["provider_registry_source"] = args.provider_registry
    qualification["resolved_provider_registry"] = str(resolved_registry_path)
    qualification["provider_secret_safety"] = secret_safety
    qualification_path.write_text(json.dumps(qualification, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    build_legacy_validation_artifact(
        qualification_path=qualification_path,
        output_path=legacy_path,
        source_basket=args.basket,
        run_id=args.run_id,
    )

    print(
        "UCITS_CLOSE_PRICE_VALIDATION_BASKET_RESULTS_OK"
        f" | path={legacy_path}"
        f" | qualification={qualification_path}"
        f" | report_date={report_date}"
        f" | funded_consensus={qualification['funded_consensus_count']}/{qualification['funded_line_count']}"
        f" | identity_anchors={qualification['funded_identity_anchor_count']}/{qualification['funded_line_count']}"
        f" | cache_used={qualification.get('provider_cache_used_count', 0)}"
        f" | stale_registry_flags={funded_authority['stale_registry_funded_flags_overridden']}"
        f" | alpha_live={secret_safety['alpha_vantage_live_enabled']}"
        f" | gate={qualification['report_pricing_gate_passed']}"
    )
    require_consensus = args.require_funded_consensus or bool(os.environ.get("WP11_RUN_ID"))
    if require_consensus and not qualification.get("report_pricing_gate_passed"):
        raise SystemExit("Funded-position provider consensus and identity-anchor gate failed; report generation is blocked.")


if __name__ == "__main__":
    main()
