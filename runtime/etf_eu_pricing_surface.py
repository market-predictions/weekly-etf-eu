from __future__ import annotations

from typing import Any


def _fmt(value: Any) -> str:
    return str(value if value is not None else "-").strip() or "-"


def _price_summary(row: dict[str, Any], *, language: str) -> str:
    gate = row.get("agreement_gate_evidence") or {}
    status = _fmt(gate.get("status"))
    observed = _fmt(gate.get("agreed_observed_date"))
    close = _fmt(gate.get("agreed_close"))
    currency = _fmt(gate.get("agreed_currency"))
    sources = ", ".join(gate.get("agreement_source_ids") or []) or "-"
    if language == "nl":
        return f"status={status}; datum={observed}; slot={close}; valuta={currency}; bronnen={sources}"
    return f"status={status}; date={observed}; close={close}; currency={currency}; sources={sources}"


def pricing_surface_table(payload: dict[str, Any], *, language: str) -> str:
    """Render agreement-aware pricing evidence without funding authority.

    The table is intentionally candidate/evidence-only. It must not be read as a
    funded portfolio, buy recommendation, or valuation-authority promotion.
    """

    rows = payload.get("rows") or []
    if language == "nl":
        lines = [
            "| Instrument | ISIN | Handelslijn | Agreement-gate pricing | Portefeuille-status |",
            "|---|---|---|---|---|",
        ]
        if not rows:
            lines.append("| Geen pricingregels | - | - | geen agreement-gate bewijs | niet gefinancierd; geen waarderingsautoriteit |")
            return "\n".join(lines)
        for row in rows:
            line = f"{_fmt(row.get('exchange_ticker'))} / {_fmt(row.get('trading_currency'))} / {_fmt(row.get('exchange'))}"
            lines.append(
                "| "
                + " | ".join([
                    _fmt(row.get("fund_name")),
                    _fmt(row.get("isin")),
                    line,
                    _price_summary(row, language="nl"),
                    "niet gefinancierd; geen waarderingsautoriteit",
                ])
                + " |"
            )
        return "\n".join(lines)

    lines = [
        "| Instrument | ISIN | Trading line | Agreement-gate pricing | Portfolio status |",
        "|---|---|---|---|---|",
    ]
    if not rows:
        lines.append("| No pricing rows | - | - | no agreement-gate evidence | not funded; no valuation authority |")
        return "\n".join(lines)
    for row in rows:
        line = f"{_fmt(row.get('exchange_ticker'))} / {_fmt(row.get('trading_currency'))} / {_fmt(row.get('exchange'))}"
        lines.append(
            "| "
            + " | ".join([
                _fmt(row.get("fund_name")),
                _fmt(row.get("isin")),
                line,
                _price_summary(row, language="en"),
                "not funded; no valuation authority",
            ])
            + " |"
        )
    return "\n".join(lines)


def pricing_surface_section(payload: dict[str, Any], *, language: str) -> str:
    if language == "nl":
        return (
            "## Agreement-gate pricing oppervlak\n\n"
            "Onderstaande pricingregels zijn bewijsregels voor kandidaten. Deze sectie is **geen portefeuille**, "
            "**geen koopadvies** en **geen waarderingsautoriteit**.\n\n"
            + pricing_surface_table(payload, language="nl")
        )
    return (
        "## Agreement-gate pricing surface\n\n"
        "The pricing rows below are candidate evidence rows. This section is **not a portfolio**, "
        "**not a buy recommendation** and **not valuation authority**.\n\n"
        + pricing_surface_table(payload, language="en")
    )
