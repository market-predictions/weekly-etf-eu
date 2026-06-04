from __future__ import annotations

from typing import Any


def _fmt(value: Any) -> str:
    return str(value if value is not None else "-").strip() or "-"


def _bool_text(value: Any) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    return _fmt(value)


def _blocker_summary(blockers: list[Any]) -> str:
    if not blockers:
        return "-"
    return ", ".join(_fmt(item) for item in blockers[:6])


def _gate_status_summary(gates: dict[str, Any]) -> str:
    if not gates:
        return "-"
    parts: list[str] = []
    for gate_name, gate in gates.items():
        if isinstance(gate, dict):
            parts.append(f"{gate_name}={_fmt(gate.get('status'))}")
        else:
            parts.append(f"{gate_name}=-")
    return "; ".join(parts)


def fundability_surface_table(payload: dict[str, Any], *, language: str) -> str:
    rows = payload.get("rows") or []
    if language == "nl":
        lines = [
            "| Instrument | ISIN | Fundability gate status | Gate blockers | Gates | Authority |",
            "|---|---|---|---|---|---|",
        ]
        if not rows:
            lines.append(
                "| Geen fundabilityregels | - | niet beschikbaar | geen artifact beschikbaar | - | candidate_promotion=false; funding_authority=false; portfolio_mutation=false; production_delivery=false |"
            )
            return "\n".join(lines)
        for row in rows:
            lines.append(
                "| "
                + " | ".join([
                    _fmt(row.get("fund_name")),
                    _fmt(row.get("isin")),
                    _fmt(row.get("fundability_gate_status")),
                    _blocker_summary(row.get("gate_blockers") or []),
                    _gate_status_summary(row.get("gates") or {}),
                    "candidate_promotion=false; funding_authority=false; portfolio_mutation=false; production_delivery=false",
                ])
                + " |"
            )
        return "\n".join(lines)

    lines = [
        "| Instrument | ISIN | Fundability gate status | Gate blockers | Gates | Authority |",
        "|---|---|---|---|---|---|",
    ]
    if not rows:
        lines.append(
            "| No fundability rows | - | unavailable | no artifact available | - | candidate_promotion=false; funding_authority=false; portfolio_mutation=false; production_delivery=false |"
        )
        return "\n".join(lines)
    for row in rows:
        lines.append(
            "| "
            + " | ".join([
                _fmt(row.get("fund_name")),
                _fmt(row.get("isin")),
                _fmt(row.get("fundability_gate_status")),
                _blocker_summary(row.get("gate_blockers") or []),
                _gate_status_summary(row.get("gates") or {}),
                "candidate_promotion=false; funding_authority=false; portfolio_mutation=false; production_delivery=false",
            ])
            + " |"
        )
    return "\n".join(lines)


def fundability_surface_section(payload: dict[str, Any] | None, *, language: str) -> str:
    payload = payload or {"rows": []}
    candidate_promotion = _bool_text(payload.get("candidate_promotion", False))
    funding_authority = _bool_text(payload.get("funding_authority", False))
    portfolio_mutation = _bool_text(payload.get("portfolio_mutation", False))
    production_delivery = _bool_text(payload.get("production_delivery", False))
    candidate_count = _fmt(payload.get("candidate_count", len(payload.get("rows") or [])))
    not_fundable_count = _fmt(payload.get("not_fundable_count", "-"))

    if language == "nl":
        return (
            "## Fundability gate status\n\n"
            "De fundability gate status is zichtbaar als rapportbewijs. Deze sectie promoveert geen kandidaat naar fundable en creëert geen funding authority.\n\n"
            f"- **Kandidaten:** {candidate_count}.\n"
            f"- **Niet fundable / geblokkeerd:** {not_fundable_count}.\n"
            f"- **candidate_promotion={candidate_promotion}**.\n"
            f"- **funding_authority={funding_authority}**.\n"
            f"- **portfolio_mutation={portfolio_mutation}**.\n"
            f"- **production_delivery={production_delivery}**.\n\n"
            + fundability_surface_table(payload, language="nl")
        )

    return (
        "## Fundability gate status\n\n"
        "The fundability gate status is visible as report evidence. This section does not promote any candidate to fundable and creates no funding authority.\n\n"
        f"- **Candidates:** {candidate_count}.\n"
        f"- **Not fundable / blocked:** {not_fundable_count}.\n"
        f"- **candidate_promotion={candidate_promotion}**.\n"
        f"- **funding_authority={funding_authority}**.\n"
        f"- **portfolio_mutation={portfolio_mutation}**.\n"
        f"- **production_delivery={production_delivery}**.\n\n"
        + fundability_surface_table(payload, language="en")
    )
