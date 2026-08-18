from __future__ import annotations

import json
from pathlib import Path
from typing import Any

AUTHORIZED_EXACT_STATUSES = {"fresh_exact_verified", "fresh_exact_unverified"}


def _text(value: Any) -> str:
    return str(value or "").strip()


def _sanitize_blocker(value: Any) -> str:
    text = _text(value)
    folded = text.casefold()
    if text.startswith("provider_message:"):
        if any(token in folded for token in ("rate limit", "spreading out", "quota", "standard api")):
            return "provider_rate_or_quota_limit"
        return "provider_error_message_redacted"
    return text


def _sanitize_provider_row(row: dict[str, Any]) -> None:
    row["blockers"] = sorted({_sanitize_blocker(item) for item in (row.get("blockers") or []) if _sanitize_blocker(item)})
    evidence = []
    for source in row.get("identity_evidence", []) or []:
        if not isinstance(source, dict):
            continue
        evidence.append(
            {
                key: value
                for key, value in source.items()
                if key.casefold() not in {"apikey", "api_key", "api_token", "access_key", "token", "secret"}
            }
        )
    row["identity_evidence"] = evidence


def _symbol_match(row: dict[str, Any]) -> bool | None:
    returned = _text(row.get("returned_symbol")).upper()
    requested = _text(row.get("provider_symbol")).upper()
    if not returned:
        return None
    return returned == requested


def _live_metadata_anchor(row: dict[str, Any]) -> bool:
    return (
        row.get("pricing_status") == "priced"
        and _symbol_match(row) is True
        and row.get("venue_match") is True
        and row.get("currency_match") is True
    )


def _provider_price_accepted(row: dict[str, Any]) -> bool:
    if row.get("pricing_status") != "priced":
        return False
    if row.get("close_price") in (None, "") or not _text(row.get("close_date")):
        return False
    symbol_match = _symbol_match(row)
    if symbol_match is False:
        return False
    if row.get("venue_match") is False or row.get("currency_match") is False:
        return False
    return True


def _binding_map(identity_binding: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        _text(row.get("basket_id")): row
        for row in identity_binding.get("rows") or []
        if isinstance(row, dict) and _text(row.get("basket_id"))
    }


def apply_primary_verification_policy_payload(
    payload: dict[str, Any],
    identity_binding: dict[str, Any],
) -> dict[str, Any]:
    """Apply donor-aligned primary-close + optional verification authority.

    Stable instrument identity comes from the canonical UCITS symbol registry.
    A second live price source increases confidence but is not a universal
    liveness dependency. Genuine same-date disagreement still fails closed.
    """

    provider_order = [_text(item) for item in payload.get("provider_order") or [] if _text(item)]
    report_date = _text(payload.get("report_date"))
    tolerance_pct = float(payload.get("agreement_tolerance_pct") or 0.0)
    bindings = _binding_map(identity_binding)
    lines = [row for row in payload.get("lines") or [] if isinstance(row, dict)]

    for line in lines:
        basket_id = _text(line.get("basket_id"))
        binding = bindings.get(basket_id, {})
        static_bound = binding.get("static_identity_binding") is True
        provider_rows = [row for row in line.get("provider_results") or [] if isinstance(row, dict)]

        live_anchor_providers: list[str] = []
        accepted_exact: list[dict[str, Any]] = []
        stale_or_other_date: list[str] = []
        rejected_providers: list[str] = []

        for provider_row in provider_rows:
            _sanitize_provider_row(provider_row)
            provider_row["symbol_match"] = _symbol_match(provider_row)
            provider_row["live_metadata_identity_anchor"] = _live_metadata_anchor(provider_row)
            provider_row["primary_verification_accepted"] = _provider_price_accepted(provider_row)
            provider = _text(provider_row.get("provider"))
            if provider_row["live_metadata_identity_anchor"]:
                live_anchor_providers.append(provider)
            if not provider_row["primary_verification_accepted"]:
                if provider_row.get("pricing_status") == "priced":
                    rejected_providers.append(provider)
                continue
            if _text(provider_row.get("close_date")) == report_date:
                accepted_exact.append(provider_row)
            else:
                stale_or_other_date.append(provider)

        order_index = {provider: index for index, provider in enumerate(provider_order)}
        accepted_exact.sort(key=lambda row: order_index.get(_text(row.get("provider")), len(order_index) + 1))
        primary = accepted_exact[0] if accepted_exact else None
        primary_provider = _text((primary or {}).get("provider")) or None
        primary_price = float(primary["close_price"]) if primary is not None else None
        exact_prices = [float(row["close_price"]) for row in accepted_exact]
        spread_pct = None
        if primary_price and exact_prices:
            spread_pct = (max(exact_prices) - min(exact_prices)) / primary_price * 100.0

        if not static_bound:
            status = "identity_binding_failed"
            selected_price = None
            verification_status = "blocked_static_identity_not_bound"
            verification_providers: list[str] = []
        elif not accepted_exact:
            status = "no_exact_close"
            selected_price = None
            verification_status = "blocked_no_exact_requested_date_close"
            verification_providers = []
        elif len(accepted_exact) >= 2 and spread_pct is not None and spread_pct > tolerance_pct:
            status = "provider_disagreement"
            selected_price = None
            verification_status = "blocked_same_date_provider_disagreement"
            verification_providers = [_text(row.get("provider")) for row in accepted_exact[1:]]
        elif len(accepted_exact) >= 2:
            status = "fresh_exact_verified"
            selected_price = primary_price
            verification_status = "verified_same_date_within_tolerance"
            verification_providers = [_text(row.get("provider")) for row in accepted_exact[1:]]
        else:
            status = "fresh_exact_unverified"
            selected_price = primary_price
            verification_status = "unverified_no_same_date_verifier"
            verification_providers = []

        line["qualification_status"] = status
        line["selected_close_date"] = report_date if status in AUTHORIZED_EXACT_STATUSES else None
        line["selected_close_price"] = round(selected_price, 8) if selected_price is not None else None
        # Compatibility field consumed by the legacy validation artifact builder.
        # Under primary+verification this is the selected primary close, not a blend.
        line["consensus_close_price"] = line["selected_close_price"]
        line["primary_provider"] = primary_provider
        line["primary_close_price"] = round(primary_price, 8) if primary_price is not None else None
        line["verification_status"] = verification_status
        line["verification_providers"] = verification_providers
        line["same_date_provider_count"] = len(accepted_exact)
        line["agreeing_providers"] = (
            [_text(row.get("provider")) for row in accepted_exact]
            if status in AUTHORIZED_EXACT_STATUSES
            else []
        )
        line["agreement_spread_pct"] = round(float(spread_pct), 6) if spread_pct is not None else None
        line["static_identity_binding"] = static_bound
        line["static_identity_binding_status"] = binding.get("binding_status")
        line["static_identity_registry_id"] = binding.get("registry_id")
        line["static_identity_blockers"] = list(binding.get("blockers") or [])
        line["identity_assurance_status"] = (
            "static_registry_verified_exact_line" if static_bound else "static_registry_identity_failed"
        )
        line["identity_anchor_providers"] = sorted(set(live_anchor_providers))
        line["identity_anchor_provider_count"] = len(set(live_anchor_providers))
        line["stale_or_other_date_providers"] = sorted(set(stale_or_other_date))
        line["rejected_provider_prices"] = sorted(set(rejected_providers))
        line["valuation_grade"] = status in AUTHORIZED_EXACT_STATUSES and static_bound

    funded = [line for line in lines if line.get("funded")]
    authorized = [line for line in funded if line.get("qualification_status") in AUTHORIZED_EXACT_STATUSES]
    verified = [line for line in funded if line.get("qualification_status") == "fresh_exact_verified"]
    unverified = [line for line in funded if line.get("qualification_status") == "fresh_exact_unverified"]
    static_bound_funded = [line for line in funded if line.get("static_identity_binding") is True]

    payload["qualified_line_count"] = sum(
        line.get("qualification_status") in AUTHORIZED_EXACT_STATUSES for line in lines
    )
    payload["funded_pricing_authorized_count"] = len(authorized)
    payload["funded_verified_count"] = len(verified)
    payload["funded_unverified_count"] = len(unverified)
    # Historical field retained with its literal meaning: verified multi-source lines.
    payload["funded_consensus_count"] = len(verified)
    payload["funded_static_identity_bound_count"] = len(static_bound_funded)
    # Compatibility summary: identity authority is now static registry identity.
    payload["funded_identity_anchor_count"] = len(static_bound_funded)
    payload["report_pricing_gate_passed"] = bool(funded) and len(authorized) == len(funded)
    payload["pricing_authority_policy"] = {
        "mode": "donor_aligned_primary_plus_verification_v1",
        "static_identity_authority": "config/ucits_symbol_registry.yml",
        "exact_requested_date_primary_required": True,
        "second_provider_required_for_liveness": False,
        "same_date_verifier_within_tolerance_upgrades_confidence": True,
        "same_date_disagreement_blocks": True,
        "stale_verifier_blocks": False,
        "selected_price_semantics": "primary_provider_close_not_median_blend",
        "authorized_statuses": sorted(AUTHORIZED_EXACT_STATUSES),
    }
    payload["identity_policy"] = {
        "static_exact_line_binding_required": True,
        "binding_identity": "isin+ticker+exchange+mic+currency+provider_symbol",
        "live_metadata_anchor_required_each_run": False,
        "returned_symbol_mismatch_rejects_provider": True,
        "returned_venue_mismatch_rejects_provider": True,
        "returned_currency_mismatch_rejects_provider": True,
        "live_metadata_identity_anchors": "supplemental_verification_only",
    }
    payload["static_identity_binding"] = identity_binding
    payload["secret_redaction_applied"] = True
    payload["provider_message_storage_policy"] = "classification_only_no_response_body"
    return payload


def apply_primary_verification_policy(path: Path, identity_binding: dict[str, Any]) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload = apply_primary_verification_policy_payload(payload, identity_binding)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


# Backward-compatible import name. Callers should migrate to
# apply_primary_verification_policy with explicit static identity evidence.
def apply_identity_anchor_policy(path: Path) -> dict[str, Any]:
    raise RuntimeError(
        "apply_identity_anchor_policy is retired; static UCITS identity binding is required by primary+verification policy"
    )
