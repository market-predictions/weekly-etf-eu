from __future__ import annotations

from typing import Any

from pricing.ucits_close_price_validation_contract_v2 import AUTHORIZED_EXACT_STATUSES


def _money(value: Any, language: str) -> str:
    raw = f"{float(value or 0):,.2f}"
    if language == "nl":
        raw = raw.replace(",", "X").replace(".", ",").replace("X", ".")
    return "EUR " + raw


def _num(value: Any, language: str, decimals: int = 2) -> str:
    try:
        raw = f"{float(value):,.{decimals}f}"
    except (TypeError, ValueError):
        return "n/a"
    if language == "nl":
        raw = raw.replace(",", "X").replace(".", ",").replace("X", ".")
    return raw


def _ticker(row: dict[str, Any]) -> str:
    ticker = str(row.get("exchange_ticker") or row.get("ticker") or "").strip().upper()
    return "L0CK" if ticker == "LOCK" else ticker


def _join_tickers(tickers: list[str], language: str) -> str:
    clean = [ticker for ticker in tickers if ticker]
    if not clean:
        return ""
    if len(clean) == 1:
        return clean[0]
    conjunction = " en " if language == "nl" else " and "
    return ", ".join(clean[:-1]) + conjunction + clean[-1]


def _authority_status(row: dict[str, Any]) -> str:
    for key in ("authority_status", "verification_status", "pricing_status", "source_agreement_status"):
        value = str(row.get(key) or "").strip()
        if value in AUTHORIZED_EXACT_STATUSES:
            return value
    return ""


def _current_additions(state: dict[str, Any], positions: list[dict[str, Any]]) -> list[str]:
    current = state.get("current_allocation_decision")
    if isinstance(current, dict):
        added = [str(value).strip().upper() for value in current.get("added_tickers") or [] if str(value).strip()]
        if added:
            return added
    portfolio = state.get("portfolio") if isinstance(state.get("portfolio"), dict) else {}
    activation = portfolio.get("last_model_capital_activation")
    run_id = str(activation.get("run_id") or "") if isinstance(activation, dict) else ""
    if not run_id:
        return []
    return [
        _ticker(row)
        for row in positions
        if _ticker(row)
        and str(row.get("source_run_id") or "") == run_id
        and str(row.get("action_executed_this_run") or "").casefold() == "model buy"
    ]


def _status_label(status: str, language: str) -> str:
    if language == "nl":
        return {
            "fresh_exact_verified": "Exacte slotkoers · onafhankelijk geverifieerd",
            "fresh_exact_unverified": "Exacte slotkoers · geen actuele onafhankelijke verifier",
        }.get(status, "Geen prijsautoriteit")
    return {
        "fresh_exact_verified": "Exact close · independently verified",
        "fresh_exact_unverified": "Exact close · no current independent verifier",
    }.get(status, "No pricing authority")


def _provider_text(row: dict[str, Any], language: str) -> str:
    primary = str(row.get("primary_provider") or "").strip() or "n/a"
    verifiers = [str(value).strip() for value in row.get("verification_providers") or [] if str(value).strip()]
    if verifiers:
        return primary + " + " + ", ".join(verifiers)
    return primary + (" (geen actuele verifier)" if language == "nl" else " (no current verifier)")


def render_funded_markdown(state: dict[str, Any], *, language: str) -> str:
    """Render final client Markdown directly from normalized current state.

    No legacy client prose is consumed and no semantic post-processing is required.
    Pricing claims are projections of the canonical pricing authority carried by
    normalized state. Pricing authority remains separate from fundability,
    allocation, broker execution and delivery authority.
    """

    if language not in {"nl", "en"}:
        raise ValueError("language must be nl or en")

    portfolio = state.get("portfolio") if isinstance(state.get("portfolio"), dict) else {}
    positions = [row for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    if not positions:
        raise RuntimeError("Native funded Markdown requires funded model positions")

    tickers = [_ticker(row) for row in positions if _ticker(row)]
    additions = _current_additions(state, positions)
    verified = sum(_authority_status(row) == "fresh_exact_verified" for row in positions)
    primary_only = sum(_authority_status(row) == "fresh_exact_unverified" for row in positions)
    authorized = verified + primary_only
    count = len(positions)
    pricing_rows = [row for row in (state.get("pricing") or {}).get("rows") or [] if isinstance(row, dict)]
    current_review = state.get("current_reunderwriting") if isinstance(state.get("current_reunderwriting"), dict) else {}
    report_date = str(state.get("report_date") or current_review.get("report_date") or "")

    lines: list[str] = []
    if language == "nl":
        lines.extend(
            [
                "# Weekly ETF EU Review",
                "",
                f"**Rapportdatum:** {report_date}",
                "",
                "## 1. Beslissamenvatting",
                "",
                f"- **Huidige portefeuille:** {count} gefinancierde UCITS-posities ({_join_tickers(tickers, 'nl')}).",
                f"- **Kapitaal:** {_money(portfolio.get('invested_market_value_eur'), 'nl')} belegd en {_money(portfolio.get('cash_eur'), 'nl')} cash; geen echte brokeruitvoering.",
                f"- **Prijsautoriteit:** {authorized} van {count} gefinancierde lijnen hebben geautoriseerde exact-line completed-close pricing; {verified} onafhankelijk geverifieerd en {primary_only} primary-authoritative zonder actuele verifier.",
                "- **Beslisregel:** prijsautoriteit ondersteunt waardering, maar creëert geen funding-, allocatie-, broker- of delivery-authority.",
            ]
        )
        if additions:
            lines.append(f"- **Toegevoegd deze run:** {_join_tickers(additions, 'nl')}.")
        else:
            lines.append("- **Modelmutatie:** geen nieuwe modelportefeuillewijziging uit deze rapportgeneratie.")
        lines.extend(["", "## 2. Gefinancierde posities", ""])
        lines.append("| Handelslijn | ISIN | Stukken | Slotkoers | Peildatum | Marktwaarde | Gewicht | Prijsautoriteit | Bronbewijs | Actueel besluit |")
        lines.append("| --- | --- | ---: | ---: | --- | ---: | ---: | --- | --- | --- |")
        for row in positions:
            status = _authority_status(row)
            lines.append(
                "| "
                + " | ".join(
                    [
                        _ticker(row),
                        str(row.get("isin") or ""),
                        str(int(float(row.get("shares") or 0))),
                        _money(row.get("current_price_local"), "nl"),
                        str(row.get("price_date") or ""),
                        _money(row.get("market_value_eur"), "nl"),
                        _num(row.get("current_weight_pct"), "nl") + "%",
                        _status_label(status, "nl"),
                        _provider_text(row, "nl"),
                        str(row.get("current_allocation_decision") or "hold"),
                    ]
                )
                + " |"
            )
        lines.extend(["", "## 3. UCITS-kandidaten en prijsbewijs", ""])
        lines.append("| Handelslijn | Fonds | ISIN | Beurs | Datum | Slot | Valuta | Prijsautoriteit | Primary | Verifier |")
        lines.append("| --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- |")
        for row in pricing_rows:
            status = _authority_status(row)
            verifiers = ", ".join(str(value) for value in row.get("verification_providers") or []) or "geen actuele verifier"
            lines.append(
                "| "
                + " | ".join(
                    [
                        str(row.get("ticker") or ""),
                        str(row.get("fund_name") or ""),
                        str(row.get("isin") or ""),
                        str(row.get("exchange") or ""),
                        str(row.get("close_date") or ""),
                        _num(row.get("close_price"), "nl"),
                        str(row.get("currency") or ""),
                        _status_label(status, "nl"),
                        str(row.get("primary_provider") or "n/a"),
                        verifiers,
                    ]
                )
                + " |"
            )
        lines.extend(
            [
                "",
                "Exact primary pricing kan valuation-grade autoriteit dragen. Een actuele onafhankelijke verifier verhoogt confidence; same-date disagreement blijft fail-closed.",
                "",
                "## 4. Huidige re-underwriting",
                "",
            ]
        )
        for row in positions:
            lines.extend(
                [
                    f"### {_ticker(row)}",
                    f"- **Thesis:** {row.get('thesis_assessment') or 'n/a'}",
                    f"- **Implementation:** {row.get('implementation_assessment') or 'n/a'}",
                    f"- **Volgende actie:** {row.get('required_next_action') or 'n/a'}",
                    "",
                ]
            )
        lines.extend(
            [
                "## 5. Cash en volgende run",
                "",
                str(current_review.get("cash_after_explanation") or "Resterende cash blijft tactical reserve totdat een distincte lane alle huidige fundability-gates passeert."),
                "",
                "## Disclaimer",
                "",
                "Dit rapport is uitsluitend informatief en educatief en is geen beleggings-, juridisch, fiscaal of financieel advies. Geen echte brokeruitvoering of e-maildelivery is door deze rapportgeneratie geautoriseerd.",
            ]
        )
    else:
        lines.extend(
            [
                "# Weekly ETF EU Review",
                "",
                f"**Report date:** {report_date}",
                "",
                "## 1. Decision summary",
                "",
                f"- **Current portfolio:** {count} funded UCITS positions ({_join_tickers(tickers, 'en')}).",
                f"- **Capital:** {_money(portfolio.get('invested_market_value_eur'), 'en')} invested and {_money(portfolio.get('cash_eur'), 'en')} cash; no real broker execution.",
                f"- **Pricing authority:** {authorized} of {count} funded lines have authorized exact-line completed-close pricing; {verified} independently verified and {primary_only} primary-authoritative without a current verifier.",
                "- **Decision rule:** pricing authority supports valuation but creates no funding, allocation, broker or delivery authority.",
            ]
        )
        if additions:
            lines.append(f"- **Added this run:** {_join_tickers(additions, 'en')}.")
        else:
            lines.append("- **Model mutation:** no new model-portfolio change is authorized by this report generation.")
        lines.extend(["", "## 2. Funded positions", ""])
        lines.append("| Trading line | ISIN | Shares | Close | Pricing date | Market value | Weight | Pricing authority | Evidence | Current decision |")
        lines.append("| --- | --- | ---: | ---: | --- | ---: | ---: | --- | --- | --- |")
        for row in positions:
            status = _authority_status(row)
            lines.append(
                "| "
                + " | ".join(
                    [
                        _ticker(row),
                        str(row.get("isin") or ""),
                        str(int(float(row.get("shares") or 0))),
                        _money(row.get("current_price_local"), "en"),
                        str(row.get("price_date") or ""),
                        _money(row.get("market_value_eur"), "en"),
                        _num(row.get("current_weight_pct"), "en") + "%",
                        _status_label(status, "en"),
                        _provider_text(row, "en"),
                        str(row.get("current_allocation_decision") or "hold"),
                    ]
                )
                + " |"
            )
        lines.extend(["", "## 3. UCITS candidates and pricing evidence", ""])
        lines.append("| Trading line | Fund | ISIN | Exchange | Date | Close | Currency | Pricing authority | Primary | Verifier |")
        lines.append("| --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- |")
        for row in pricing_rows:
            status = _authority_status(row)
            verifiers = ", ".join(str(value) for value in row.get("verification_providers") or []) or "no current verifier"
            lines.append(
                "| "
                + " | ".join(
                    [
                        str(row.get("ticker") or ""),
                        str(row.get("fund_name") or ""),
                        str(row.get("isin") or ""),
                        str(row.get("exchange") or ""),
                        str(row.get("close_date") or ""),
                        _num(row.get("close_price"), "en"),
                        str(row.get("currency") or ""),
                        _status_label(status, "en"),
                        str(row.get("primary_provider") or "n/a"),
                        verifiers,
                    ]
                )
                + " |"
            )
        lines.extend(
            [
                "",
                "Exact primary pricing can carry valuation-grade authority. A current independent verifier increases confidence; same-date disagreement remains fail-closed.",
                "",
                "## 4. Current re-underwriting",
                "",
            ]
        )
        for row in positions:
            lines.extend(
                [
                    f"### {_ticker(row)}",
                    f"- **Thesis:** {row.get('thesis_assessment') or 'n/a'}",
                    f"- **Implementation:** {row.get('implementation_assessment') or 'n/a'}",
                    f"- **Next action:** {row.get('required_next_action') or 'n/a'}",
                    "",
                ]
            )
        lines.extend(
            [
                "## 5. Cash and next run",
                "",
                str(current_review.get("cash_after_explanation") or "Residual cash remains tactical reserve until a distinct lane passes every current fundability gate."),
                "",
                "## Disclaimer",
                "",
                "This report is for informational and educational purposes only and is not investment, legal, tax or financial advice. No real broker execution or email delivery is authorized by this report generation.",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def _funded_valuation_grade_count(positions: list[dict[str, Any]]) -> int:
    return sum(_authority_status(row) in AUTHORIZED_EXACT_STATUSES for row in positions)


def validate_funded_markdown(text: str, state: dict[str, Any], *, language: str) -> list[str]:
    portfolio = state.get("portfolio") if isinstance(state.get("portfolio"), dict) else {}
    positions = [row for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    if not positions:
        return []

    blockers: list[str] = []
    tickers = [_ticker(row) for row in positions if _ticker(row)]
    additions = _current_additions(state, positions)
    folded = text.casefold()

    count_token = (
        f"{len(positions)} gefinancierde ucits-posities"
        if language == "nl"
        else f"{len(positions)} funded ucits positions"
    )
    if count_token.casefold() not in folded:
        blockers.append("dynamic funded position count missing from Markdown")

    for ticker in tickers:
        if ticker.casefold() not in folded:
            blockers.append(f"funded ticker missing from Markdown: {ticker}")

    if additions:
        addition_token = "toegevoegd" if language == "nl" else "added"
        if addition_token not in folded:
            blockers.append("current-run funded additions are not explicitly disclosed")
        for ticker in additions:
            if ticker.casefold() not in folded:
                blockers.append(f"current-run added ticker missing from Markdown: {ticker}")

    funded_grade = _funded_valuation_grade_count(positions)
    if funded_grade == len(positions):
        required_quality = (
            f"{funded_grade} van {len(positions)} gefinancierde lijnen"
            if language == "nl"
            else f"{funded_grade} of {len(positions)} funded lines"
        )
        if required_quality.casefold() not in folded:
            blockers.append("funded valuation-grade quality disclosure missing")

    verified = sum(_authority_status(row) == "fresh_exact_verified" for row in positions)
    primary_only = sum(_authority_status(row) == "fresh_exact_unverified" for row in positions)
    if verified and ("onafhankelijk geverifieerd" if language == "nl" else "independently verified") not in folded:
        blockers.append("verified pricing confidence disclosure missing")
    if primary_only and ("geen actuele onafhankelijke verifier" if language == "nl" else "no current independent verifier") not in folded:
        blockers.append("primary-only pricing confidence disclosure missing")

    forbidden = [
        "qualified_development_consensus",
        "qualified_completed_close_primary_plus_verification",
        "qualified_two_provider_completed_close",
        "two-provider completed-close consensus",
        "two-provider exact-line consensus",
        "valuation-grade two-provider",
        "two independent sources",
        "checked through two sources",
        "single_source_only",
        "priced_non_authoritative",
        "verified_ucits_trading_line",
        "reserve minimaal 7,50%",
        "minimum cash reserve 7.50%",
        "strategic target weight",
        "phase target weight",
    ]
    for token in forbidden:
        if token.casefold() in folded:
            blockers.append(f"retired/stale Markdown wording present: {token}")
    return blockers


def reconcile_funded_markdown(text: str, state: dict[str, Any], *, language: str) -> str:
    """Compatibility alias for callers not yet migrated to native generation.

    The legacy input text is deliberately ignored. Final Markdown is generated
    from normalized state rather than semantically patching an already-rendered
    artifact.
    """

    _ = text
    return render_funded_markdown(state, language=language)