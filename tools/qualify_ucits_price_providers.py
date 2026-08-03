from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pricing.provider_secret_safety import enforce_provider_secret_safety
from pricing.ucits_price_evidence_cache import apply_provider_evidence_cache
from pricing.ucits_price_provider_engine import build_provider_qualification
from pricing.ucits_price_qualification_policy import apply_identity_anchor_policy


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", default="config/ucits_price_provider_registry.yml")
    parser.add_argument("--provider-cache", default="config/etf_eu_provider_close_cache_20260731.json")
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--providers", default="")
    parser.add_argument("--verify-identity", action="store_true")
    parser.add_argument("--pause-seconds", type=float, default=1.0)
    parser.add_argument("--max-close-age-days", type=int, default=7)
    parser.add_argument("--agreement-tolerance-pct", type=float, default=1.0)
    args = parser.parse_args()
    secret_safety = enforce_provider_secret_safety()
    providers = [item.strip() for item in args.providers.split(",") if item.strip()] or None
    output = Path(args.output)
    build_provider_qualification(
        registry_path=Path(args.registry),
        report_date=date.fromisoformat(args.report_date),
        output_path=output,
        providers=providers,
        verify_identity=args.verify_identity,
        pause_seconds=args.pause_seconds,
        max_close_age_days=args.max_close_age_days,
        agreement_tolerance_pct=args.agreement_tolerance_pct,
    )
    cache_path = Path(args.provider_cache) if args.provider_cache else None
    apply_provider_evidence_cache(output, cache_path)
    payload = apply_identity_anchor_policy(output)
    payload["provider_secret_safety"] = secret_safety
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "UCITS_PRICE_IDENTITY_POLICY_OK"
        f" | funded_consensus={payload['funded_consensus_count']}/{payload['funded_line_count']}"
        f" | identity_anchors={payload['funded_identity_anchor_count']}/{payload['funded_line_count']}"
        f" | cache_used={payload.get('provider_cache_used_count', 0)}"
        f" | alpha_live={secret_safety['alpha_vantage_live_enabled']}"
        f" | gate={payload['report_pricing_gate_passed']}"
    )


if __name__ == "__main__":
    main()
