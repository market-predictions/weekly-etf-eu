from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STAGE_1_META = {
    "ai_compute_infrastructure": {
        "portfolio_label": "VVSM",
        "exchange_symbol": "VVSM",
        "isin": "IE00BMC38736",
        "fund_name": "VanEck Semiconductor UCITS ETF",
        "donor_status_field": "smh_status",
    },
    "cyber_security": {
        "portfolio_label": "LOCK",
        "exchange_symbol": "L0CK",
        "isin": "IE00BG0J4C88",
        "fund_name": "iShares Digital Security UCITS ETF",
        "donor_status_field": "cibr_status",
    },
}

BLOCKER_LABELS = {
    "accepted_current_eur_completed_close": {
        "nl": "actuele afgeronde Xetra-slotkoers ontbreekt",
        "en": "accepted current completed Xetra close is unavailable",
    },
    "accepted_liquidity_measurement": {
        "nl": "geaccepteerde 20-daagse liquiditeitsmeting ontbreekt",
        "en": "accepted 20-session liquidity measurement is unavailable",
    },
    "timestamped_bid_ask_quote_size": {
        "nl": "timestamped bied-, laat- en quote-sizebewijs ontbreekt",
        "en": "timestamped bid, ask and quote-size evidence is unavailable",
    },
    "donor_fresh_add_direction_absent": {
        "nl": "de donor geeft geen nieuwe kooprichting",
        "en": "the donor does not emit a fresh-add direction",
    },
    "stage_1_candidate_not_allowlisted": {
        "nl": "niet toegelaten tot fase 1",
        "en": "not allowlisted for Stage 1",
    },
    "pricing_missing_or_stale": {
        "nl": "actuele prijsbasis ontbreekt",
        "en": "current pricing basis is unavailable",
    },
    "liquidity_below_threshold": {
        "nl": "liquiditeit ligt onder de beleidsdrempel",
        "en": "liquidity is below the policy threshold",
    },
    "product_structure_review_required": {
        "nl": "productstructuur vereist aanvullende beoordeling",
        "en": "product structure requires additional review",
    },
}


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def number(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def ticker(position: dict[str, Any]) -> str:
    return str(position.get("ticker") or position.get("exchange_ticker") or "").strip().upper()


def preferred_variant(allocator: dict[str, Any]) -> dict[str, Any]:
    variant_id = str(allocator.get("preferred_shadow_variant") or "")
    variants = [row for row in allocator.get("variants") or [] if isinstance(row, dict)]
    for row in variants:
        if str(row.get("variant_id") or "") == variant_id:
            return row
    raise RuntimeError(f"Preferred allocator variant not found: {variant_id}")


def candidate_line(candidate: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(candidate, dict):
        return {}
    lines = [row for row in candidate.get("trading_lines") or [] if isinstance(row, dict)]
    lines.sort(
        key=lambda row: (
            str(row.get("trading_currency") or "") != "EUR",
            str(row.get("exchange") or "") != "Xetra",
            str(row.get("exchange_ticker") or ""),
        )
    )
    return lines[0] if lines else {}


def wp09_identity_index(receipt: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(row.get("isin") or "").upper(): row
        for row in receipt.get("candidate_identity") or []
        if isinstance(row, dict) and row.get("isin")
    }


def blocker_text(code: str, language: str) -> str:
    normalized = code.split(":", 1)[-1]
    fallback = normalized.replace("_", " ")
    return BLOCKER_LABELS.get(normalized, {"nl": fallback, "en": fallback})[language]


def allocator_blockers(allocator_row: dict[str, Any]) -> list[str]:
    return sorted({str(value) for value in allocator_row.get("blockers") or [] if str(value)})


def stage_1_blockers(exposure_id: str, wp09: dict[str, Any]) -> list[str]:
    prefix = "VVSM:" if exposure_id == "ai_compute_infrastructure" else "LOCK:"
    blockers = [
        str(value)
        for value in wp09.get("decision_blockers") or []
        if str(value).startswith(prefix)
    ]
    if wp09.get("donor_reunderwriting", {}).get("fresh_add_direction_present") is not True:
        blockers.append("donor_fresh_add_direction_absent")
    return sorted(set(blockers))


def build(
    sync: dict[str, Any],
    allocator: dict[str, Any],
    wp09: dict[str, Any],
    portfolio: dict[str, Any],
    portfolio_path: Path,
    ledger_path: Path,
    donor_commit: str,
    run_id: str,
) -> dict[str, Any]:
    if sync.get("schema_version") != "etf_eu_strategy_sync_shadow_v2":
        raise RuntimeError("Unsupported synchronization schema")
    if allocator.get("schema_version") != "etf_eu_target_allocator_shadow_v3":
        raise RuntimeError("Unsupported allocator schema")
    if wp09.get("schema_version") != "etf_eu_wp09_fresh_cutover_evidence_receipt_v1":
        raise RuntimeError("Unsupported WP-SYNC-09 evidence receipt")
    if wp09.get("decision", {}).get("stage_1_activation_authorized") is not False:
        raise RuntimeError("WP-SYNC-09 authority boundary is not closed")
    if wp09.get("decision", {}).get("executable_trade_intents") != []:
        raise RuntimeError("WP-SYNC-09 contains executable trade intents")

    variant = preferred_variant(allocator)
    allocation_by_exposure = {
        str(row.get("exposure_id") or ""): row
        for row in variant.get("allocation_rows") or []
        if isinstance(row, dict)
    }
    alignment_by_exposure = {
        str(row.get("exposure_id") or ""): row
        for row in sync.get("portfolio_alignment_rows") or []
        if isinstance(row, dict)
    }
    promoted = [row for row in sync.get("promoted_exposure_comparison") or [] if isinstance(row, dict)]
    if len(promoted) != 6:
        raise RuntimeError(f"Expected six promoted exposures, found {len(promoted)}")
    promoted_by_exposure = {
        str(row.get("exposure_id") or ""): row
        for row in promoted
        if row.get("exposure_id")
    }

    exposure_rows: list[dict[str, Any]] = []
    mapped_count = 0
    for source in promoted:
        exposure_id = str(source.get("exposure_id") or "")
        candidate = source.get("preferred_ucits_candidate") if isinstance(source.get("preferred_ucits_candidate"), dict) else None
        line = candidate_line(candidate)
        allocator_row = allocation_by_exposure.get(exposure_id, {})
        alignment = alignment_by_exposure.get(exposure_id, {})
        if candidate:
            mapped_count += 1
        candidate_isin = str((candidate or {}).get("isin") or "").upper()
        exchange_symbol = str(line.get("exchange_ticker") or "")
        current_weight = number(source.get("current_eu_weight_pct"))
        shadow_target = number(allocator_row.get("variant_target_weight_pct"))
        donor_target = number(alignment.get("donor_target_weight_pct"))
        blockers = allocator_blockers(allocator_row)
        if current_weight > 0:
            action = "hold_current_position"
        elif exposure_id in STAGE_1_META:
            action = "reviewed_separately_stage_1"
        else:
            action = "monitor_not_currently_actionable"
        exposure_rows.append(
            {
                "exposure_id": exposure_id,
                "lane_name": source.get("lane_name"),
                "shared_rank": source.get("shared_rank"),
                "shared_score": source.get("shared_score"),
                "donor_target_weight_pct": round(donor_target, 6),
                "current_eu_weight_pct": round(current_weight, 6),
                "analytical_allocator_weight_pct": round(shadow_target, 6),
                "actionable_target_weight_pct": round(current_weight, 6),
                "client_action": action,
                "portfolio_label": exchange_symbol,
                "exchange_symbol": exchange_symbol,
                "fund_name": (candidate or {}).get("fund_name"),
                "isin": candidate_isin,
                "exchange": line.get("exchange"),
                "currency": line.get("trading_currency"),
                "implementation_status": source.get("implementation_status"),
                "blockers": blockers,
                "blockers_nl": [blocker_text(item, "nl") for item in blockers],
                "blockers_en": [blocker_text(item, "en") for item in blockers],
                "portfolio_mutation": False,
                "allocation_authority": False,
            }
        )

    identity_by_isin = wp09_identity_index(wp09)
    donor_review = wp09.get("donor_reunderwriting") if isinstance(wp09.get("donor_reunderwriting"), dict) else {}
    stage_1_rows: list[dict[str, Any]] = []
    for exposure_id, meta in STAGE_1_META.items():
        identity = identity_by_isin.get(str(meta["isin"]), {})
        if not identity:
            raise RuntimeError(f"WP-SYNC-09 identity missing for {meta['isin']}")
        allocator_row = allocation_by_exposure.get(exposure_id, {})
        alignment = alignment_by_exposure.get(exposure_id, {})
        promoted_row = promoted_by_exposure.get(exposure_id)
        blockers = stage_1_blockers(exposure_id, wp09)
        stage_1_rows.append(
            {
                "exposure_id": exposure_id,
                "portfolio_label": identity.get("portfolio_label") or meta["portfolio_label"],
                "exchange_symbol": identity.get("exchange_symbol") or meta["exchange_symbol"],
                "fund_name": meta["fund_name"],
                "isin": identity.get("isin") or meta["isin"],
                "wkn": identity.get("wkn"),
                "exchange": identity.get("exchange"),
                "currency": identity.get("currency"),
                "kid_date": identity.get("kid_date"),
                "exact_identity_pass": identity.get("exact_identity_pass"),
                "exact_current_issuer_kid_pass": identity.get("exact_current_issuer_kid_pass"),
                "currently_promoted": promoted_row is not None,
                "current_promotion_rank": promoted_row.get("shared_rank") if isinstance(promoted_row, dict) else None,
                "current_promotion_score": promoted_row.get("shared_score") if isinstance(promoted_row, dict) else None,
                "donor_target_weight_pct": round(number(alignment.get("donor_target_weight_pct")), 6),
                "analytical_allocator_weight_pct": round(number(allocator_row.get("variant_target_weight_pct")), 6),
                "actionable_target_weight_pct": 0.0,
                "donor_review_status": donor_review.get(str(meta["donor_status_field"])),
                "donor_fresh_add_direction": False,
                "client_action": "blocked_monitor",
                "blockers": blockers,
                "blockers_nl": [blocker_text(item, "nl") for item in blockers],
                "blockers_en": [blocker_text(item, "en") for item in blockers],
                "portfolio_mutation": False,
                "allocation_authority": False,
            }
        )

    positions = [dict(row) for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    official_tickers = [ticker(row) for row in positions]
    if set(official_tickers) != {"VWCE", "EUNA", "SXR8"}:
        raise RuntimeError(f"Unexpected official portfolio tickers: {official_tickers}")

    portfolio_sha = sha256_file(portfolio_path)
    ledger_sha = sha256_file(ledger_path)
    protected = wp09.get("protected_state") if isinstance(wp09.get("protected_state"), dict) else {}
    if portfolio_sha != protected.get("portfolio_state_sha256_after"):
        raise RuntimeError("Official portfolio hash differs from accepted WP-SYNC-09 boundary")
    if ledger_sha != protected.get("trade_ledger_sha256_after"):
        raise RuntimeError("Official ledger hash differs from accepted WP-SYNC-09 boundary")

    report_date = str(sync.get("shared_strategy", {}).get("report_date") or donor_review.get("report_date") or "")
    if not report_date:
        raise RuntimeError("Report date is missing")

    state = {
        "schema_version": "etf_eu_production_convergence_state_v1",
        "artifact_type": "etf_eu_production_convergence_state",
        "generated_at_utc": utc_now(),
        "run_id": run_id,
        "report_date": report_date,
        "donor": {
            "repository": "market-predictions/weekly-etf",
            "commit": donor_commit,
            "source_run_id": sync.get("shared_strategy", {}).get("source_run_id"),
            "fresh_add_direction_present": donor_review.get("fresh_add_direction_present"),
        },
        "official_portfolio": {
            "starting_capital_eur": portfolio.get("starting_capital_eur"),
            "nav_eur": portfolio.get("nav_eur"),
            "cash_eur": portfolio.get("cash_eur"),
            "invested_market_value_eur": portfolio.get("invested_market_value_eur"),
            "position_count": len(positions),
            "positions": positions,
            "portfolio_state_sha256": portfolio_sha,
            "trade_ledger_sha256": ledger_sha,
        },
        "strategy": {
            "regime": sync.get("shared_strategy", {}).get("regime"),
            "promoted_exposure_count": len(promoted),
            "mapped_promoted_exposure_count": mapped_count,
            "unmapped_promoted_exposure_count": len(promoted) - mapped_count,
            "portfolio_alignment_summary": sync.get("portfolio_alignment_summary"),
        },
        "promoted_exposures": exposure_rows,
        "stage_1_review_candidates": stage_1_rows,
        "allocator": {
            "preferred_variant": allocator.get("preferred_shadow_variant"),
            "analytical_summary": variant.get("summary"),
            "policy_checks": variant.get("policy_checks"),
            "non_actionable_context": True,
        },
        "stage_1_decision": {
            "value": wp09.get("decision", {}).get("value"),
            "status": wp09.get("decision", {}).get("status"),
            "blocker_count": wp09.get("decision", {}).get("decision_blocker_count"),
            "blockers": list(wp09.get("decision_blockers") or []),
            "stage_1_activation_authorized": False,
            "official_state_applied": False,
            "executable_trade_intents": [],
        },
        "client_contract": {
            "dutch_primary": True,
            "english_companion": True,
            "premium_surface_required": True,
            "shadow_language_allowed": False,
            "raw_internal_tokens_allowed": False,
            "show_allocator_as_non_actionable_context": True,
            "actionable_new_positions": [],
        },
        "authority": {
            "portfolio_mutation": False,
            "ledger_write": False,
            "funding_authority": False,
            "execution_authority": False,
            "activation_authority": False,
            "production_delivery_authority": False,
        },
        "validation": {
            "funded_position_count": len(positions),
            "funded_tickers": official_tickers,
            "promoted_exposure_count": len(promoted),
            "mapped_promoted_exposure_count": mapped_count,
            "unmapped_promoted_exposure_count": len(promoted) - mapped_count,
            "stage_1_review_candidate_count": len(stage_1_rows),
            "stage_1_blocked": wp09.get("decision", {}).get("value") == "blocked",
            "protected_state_unchanged": True,
        },
    }
    return state


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the Weekly ETF EU production-convergence report state")
    parser.add_argument("--sync-shadow", type=Path, required=True)
    parser.add_argument("--allocator", type=Path, required=True)
    parser.add_argument("--wp09-receipt", type=Path, required=True)
    parser.add_argument("--portfolio-state", type=Path, default=Path("output/etf_eu_portfolio_state.json"))
    parser.add_argument("--trade-ledger", type=Path, default=Path("output/etf_eu_trade_ledger.csv"))
    parser.add_argument("--donor-commit", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    state = build(
        sync=load_json(args.sync_shadow),
        allocator=load_json(args.allocator),
        wp09=load_json(args.wp09_receipt),
        portfolio=load_json(args.portfolio_state),
        portfolio_path=args.portfolio_state,
        ledger_path=args.trade_ledger,
        donor_commit=args.donor_commit,
        run_id=args.run_id,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
