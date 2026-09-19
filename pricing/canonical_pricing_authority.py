from __future__ import annotations

from typing import Any

from pricing.ucits_close_price_validation_contract_v2 import AUTHORIZED_EXACT_STATUSES


NO_PRICING_AUTHORITY = "no_pricing_authority"
CANONICAL_PRICING_AUTHORITY_STATUSES = frozenset(
    {*AUTHORIZED_EXACT_STATUSES, NO_PRICING_AUTHORITY}
)


def canonical_pricing_authority(row: dict[str, Any] | None) -> tuple[str, list[str]]:
    """Project a raw pricing row onto the single client/business authority vocabulary.

    Raw provider/qualification statuses remain evidence only. Downstream business
    state gets exactly one of the two authorized statuses or no_pricing_authority.
    The fail-closed state always carries explicit machine-readable blockers.
    """

    if not isinstance(row, dict):
        return NO_PRICING_AUTHORITY, ["pricing_row_missing"]

    raw_status = str(row.get("source_agreement_status") or "").strip()
    primary_provider = str(row.get("primary_provider") or "").strip()
    verification_providers = [
        str(value).strip()
        for value in row.get("verification_providers") or []
        if str(value).strip()
    ]

    authorized = (
        raw_status in AUTHORIZED_EXACT_STATUSES
        and row.get("valuation_grade") is True
        and row.get("completed_close_on_requested_report_date") is True
        and row.get("static_identity_binding") is True
        and row.get("static_primary_provider_symbol_binding") is True
        and row.get("close_price") not in (None, "")
        and bool(primary_provider)
        and (
            raw_status != "fresh_exact_verified"
            or bool(verification_providers)
        )
    )
    if authorized:
        return raw_status, []

    blockers: list[str] = []
    if raw_status not in AUTHORIZED_EXACT_STATUSES:
        blockers.append(
            "source_authority_status:" + (raw_status or "missing")
        )
    if row.get("valuation_grade") is not True:
        blockers.append("not_valuation_grade")
    if row.get("completed_close_on_requested_report_date") is not True:
        blockers.append("exact_requested_date_close_missing")
    if row.get("static_identity_binding") is not True:
        blockers.append("exact_line_identity_not_bound")
    if row.get("static_primary_provider_symbol_binding") is not True:
        blockers.append("primary_provider_symbol_not_bound")
    if row.get("close_price") in (None, ""):
        blockers.append("close_price_missing")
    if not primary_provider:
        blockers.append("primary_provider_missing")
    if raw_status == "fresh_exact_verified" and not verification_providers:
        blockers.append("verification_provider_missing")

    for blocker in row.get("blockers") or []:
        value = str(blocker).strip()
        if value and value not in blockers:
            blockers.append(value)

    if not blockers:
        blockers.append("pricing_authority_not_granted")
    return NO_PRICING_AUTHORITY, blockers
