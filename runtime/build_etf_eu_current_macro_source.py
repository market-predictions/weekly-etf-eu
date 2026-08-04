from __future__ import annotations

import argparse
import copy
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

FED_SOURCE_URL = "https://www.federalreserve.gov/newsevents/pressreleases/monetary20260729a.htm"
ECB_SOURCE_URL = "https://www.ecb.europa.eu/press/pr/date/2026/html/ecb.mp260723~29f24d99bc.en.html"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def refresh(donor: dict[str, Any], *, report_date: str, donor_source: str) -> dict[str, Any]:
    payload = copy.deepcopy(donor)
    donor_report_date = str(donor.get("report_date") or "")
    generated_at = utc_now()

    payload["report_date"] = report_date
    payload["generated_at_utc"] = generated_at
    payload["source_of_truth_repo"] = "market-predictions/weekly-etf-eu"
    payload["reference_architecture_repo"] = "market-predictions/weekly-etf"
    payload["current_context_refresh"] = {
        "schema_version": "etf_eu_current_macro_source_refresh_v1",
        "refreshed_at_utc": generated_at,
        "report_date": report_date,
        "historical_donor_report_date": donor_report_date,
        "historical_donor_source": donor_source,
        "refresh_scope": "official_central_bank_policy_facts_only",
        "regime_label_treatment": "retained_historical_strategy_context_not_new_market_regime_measurement",
        "fresh_official_sources": [
            {
                "institution": "Federal Reserve",
                "event_date": "2026-07-29",
                "source_url": FED_SOURCE_URL,
                "verification_status": "official_primary_source_verified",
            },
            {
                "institution": "European Central Bank",
                "event_date": "2026-07-23",
                "source_url": ECB_SOURCE_URL,
                "verification_status": "official_primary_source_verified",
            },
        ],
        "authority": "descriptive_only",
        "funding_authority": False,
        "portfolio_mutation": False,
        "execution_authority": False,
        "delivery_authority": False,
    }

    authority = payload.setdefault("authority", {})
    authority["authority_class"] = "current_official_policy_context_plus_historical_regime"
    authority["client_facing_authority"] = False
    authority["client_surface_allowed"] = True
    authority["decision_authority"] = "descriptive_only"
    authority["decision_framework"] = (
        "Fresh official central-bank decisions may inform descriptive context; the retained donor regime label is historical strategy context only."
    )
    authority["input_state_contract"] = (
        "Official Fed and ECB releases are current policy inputs. Donor market-regime and lane-adjustment fields remain historical context and cannot create allocation authority."
    )
    authority["output_contract"] = (
        "Only client-safe policy context and explicitly labelled historical regime context may enter the EU report."
    )
    authority["operational_runbook"] = (
        "Verify official policy releases, preserve donor schema, record refresh provenance, and keep funding and execution gates separate."
    )
    authority["shadow_only"] = True

    banks = payload.setdefault("central_banks", {})
    fed = banks.setdefault("fed", {})
    fed.update(
        {
            "confidence": 0.95,
            "event_date": "2026-07-29",
            "event_status": "verified_latest_policy_decision",
            "stance": "On hold / inflation vigilance",
            "likely_direction": (
                "The FOMC kept the federal funds target at 3.50%-3.75% on 29 July 2026; three members preferred a 25 bp increase."
            ),
            "main_risk": (
                "Elevated inflation and energy-related supply shocks increase the risk of renewed tightening or delayed easing."
            ),
            "etf_implication": (
                "Maintain quality and cash discipline; duration-sensitive or high-beta allocations still require current price, relative-strength and portfolio gates."
            ),
            "source_url": FED_SOURCE_URL,
        }
    )
    ecb = banks.setdefault("ecb", {})
    ecb.update(
        {
            "confidence": 0.95,
            "event_date": "2026-07-23",
            "event_status": "verified_latest_policy_decision",
            "stance": "On hold after June tightening / data-dependent",
            "likely_direction": (
                "The ECB kept all three key rates unchanged on 23 July 2026 and retained a meeting-by-meeting, data-dependent approach."
            ),
            "main_risk": (
                "Energy-price volatility and second-round inflation effects can weaken growth while keeping policy restrictive."
            ),
            "etf_implication": (
                "European equity and bond additions require exact UCITS identity, current completed-close evidence, liquidity and relative-strength confirmation."
            ),
            "source_url": ECB_SOURCE_URL,
        }
    )

    field_authority = payload.setdefault("field_authority", {})
    field_authority["current_context_refresh"] = {
        "authority_class": "official_policy_provenance",
        "client_surface_allowed": False,
        "decision_authority": "descriptive_only",
        "notes": [
            "Records official policy freshness and donor-history boundaries.",
            "Does not authorize portfolio mutation, funding, execution or delivery.",
        ],
    }

    catalysts = [row for row in payload.get("policy_catalysts", []) if isinstance(row, dict)]
    catalysts = [
        row
        for row in catalysts
        if str(row.get("policy_area") or "") not in {"Federal Reserve rate-policy hold", "ECB rate-policy hold"}
    ]
    catalysts.insert(
        0,
        {
            "policy_area": "Federal Reserve rate-policy hold",
            "event_date": "2026-07-29",
            "event_status": "verified_report_week_policy_event",
            "latest_signal": (
                "The FOMC held the target range at 3.50%-3.75%; three voters preferred a 25 bp increase, reinforcing inflation and rate-volatility discipline."
            ),
            "direction": "on hold with hawkish dissent",
            "confidence": 0.95,
            "time_horizon": "1-6 months",
            "affected_lanes": [
                "AI compute infrastructure",
                "Rate-sensitive small caps",
                "Long-duration bonds",
            ],
            "transfer_to_report": True,
            "source_url": FED_SOURCE_URL,
        },
    )
    catalysts.insert(
        1,
        {
            "policy_area": "ECB rate-policy hold",
            "event_date": "2026-07-23",
            "event_status": "verified_report_week_policy_event",
            "latest_signal": (
                "The ECB kept key rates unchanged and retained a data-dependent approach while monitoring energy-driven inflation risks."
            ),
            "direction": "on hold / data-dependent",
            "confidence": 0.95,
            "time_horizon": "1-6 months",
            "affected_lanes": [
                "Non-U.S. developed diversification",
                "Rate-sensitive small caps",
                "Long-duration bonds",
            ],
            "transfer_to_report": True,
            "source_url": ECB_SOURCE_URL,
        },
    )
    payload["policy_catalysts"] = catalysts

    regime = payload.setdefault("regime", {})
    regime["current"] = str(regime.get("current") or "Policy transition / mixed regime")
    regime["confidence_source"] = "retained_donor_historical_context"
    regime["what_changed"] = [
        "The 29 July FOMC decision kept rates unchanged but included three votes for a rate increase.",
        "The ECB kept rates unchanged on 23 July while highlighting persistent energy and inflation uncertainty.",
        "The market-regime label is retained from the 29 July donor review as historical strategy context and is not re-estimated in this refresh.",
    ]

    memory = payload.setdefault("regime_memory", {})
    memory["report_date"] = report_date
    memory["updated_at_utc"] = generated_at
    memory["regime_changed_this_run"] = False
    memory["transition_state"] = "retained_historical_context"
    memory["decision_rule"] = (
        "Do not infer a fresh regime shift from policy releases alone; require new price, breadth and cross-asset evidence."
    )
    transfer = memory.setdefault("report_transfer", {})
    transfer["show_in_report"] = True
    transfer["max_lines"] = 2
    transfer["summary"] = (
        "Policy transition / mixed regime remains historical strategy context from 29 July; fresh Fed and ECB decisions reinforce inflation and cash-discipline risks."
    )

    payload["portfolio_implications"] = [
        "Retain cash discipline while policy remains inflation-sensitive and both the Fed and ECB are on hold.",
        "Fund only exact UCITS lines with current completed-close agreement, adequate liquidity and explicit allocation authority.",
        "Treat thematic candidates as monitored opportunities until portfolio and activation gates pass; current prices alone do not authorize funding.",
    ]

    report_transfer = payload.setdefault("report_transfer", {})
    report_transfer["style_rule"] = (
        "Transfer only current official policy facts and clearly labelled historical regime context; never present stale donor analysis as current market truth."
    )
    report_transfer["max_policy_catalysts"] = 3
    report_transfer["max_portfolio_implications"] = 3
    report_transfer["max_what_changed_bullets"] = 3

    promotion = payload.setdefault("promotion_gates", {})
    promotion["status"] = "descriptive_policy_refresh_not_promoted"
    promotion["client_surface_status"] = "descriptive_surface_only"
    promotion["decision_authority_status"] = "none_for_portfolio_activation"

    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--donor", type=Path, required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    donor = load_object(args.donor)
    payload = refresh(donor, report_date=args.report_date, donor_source=str(args.donor))
    required = {
        "active_drivers",
        "authority",
        "central_banks",
        "confidence_decomposition",
        "field_authority",
        "macro_data_audit_summary",
        "policy_catalysts",
        "portfolio_implications",
        "promotion_gates",
        "regime",
        "report_date",
        "schema_version",
    }
    missing = sorted(required - set(payload))
    if missing:
        raise RuntimeError("Current macro source missing required donor fields: " + ", ".join(missing))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        "ETF_EU_CURRENT_MACRO_SOURCE_OK"
        f" | report_date={payload['report_date']}"
        f" | donor_report_date={payload['current_context_refresh']['historical_donor_report_date']}"
        f" | output={args.output}"
    )


if __name__ == "__main__":
    main()
