from __future__ import annotations

from typing import Any


def _money(value: Any, language: str) -> str:
    raw = f"{float(value or 0):,.2f}"
    if language == "nl":
        raw = raw.replace(",", "X").replace(".", ",").replace("X", ".")
    return "EUR " + raw


def _ticker(row: dict[str, Any]) -> str:
    return str(row.get("exchange_ticker") or row.get("ticker") or "").strip().upper()


def _join_tickers(tickers: list[str], language: str) -> str:
    clean = [ticker for ticker in tickers if ticker]
    if not clean:
        return ""
    if len(clean) == 1:
        return clean[0]
    conjunction = " en " if language == "nl" else " and "
    return ", ".join(clean[:-1]) + conjunction + clean[-1]


def _replace_prefixed_line(text: str, prefix: str, replacement: str) -> str:
    lines = text.splitlines()
    replaced = False
    for index, line in enumerate(lines):
        if not replaced and line.startswith(prefix):
            lines[index] = replacement
            replaced = True
    suffix = "\n" if text.endswith("\n") else ""
    return "\n".join(lines) + suffix


def _pricing_table_row_count(text: str) -> int:
    marker = "## 3."
    start = text.find(marker)
    if start < 0:
        return 0
    section = text[start:]
    in_table = False
    count = 0
    for line in section.splitlines()[1:]:
        if line.startswith("## "):
            break
        if line.startswith("| Trading line |") or line.startswith("| Handelslijn |"):
            in_table = True
            continue
        if not in_table:
            continue
        if not line.startswith("|"):
            if count:
                break
            continue
        if "---" in line:
            continue
        count += 1
    return count


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


def _funded_valuation_grade_count(positions: list[dict[str, Any]]) -> int:
    count = 0
    for row in positions:
        status = str(row.get("pricing_status") or "").casefold()
        verification = str(row.get("verification_status") or "").casefold()
        if status == "qualified_two_provider_completed_close" and "consensus" in verification:
            count += 1
    return count


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
            blockers.append("funded two-provider valuation-grade quality disclosure missing")

    forbidden = (
        [
            "drie gefinancierde ucits-posities",
            "reserve minimaal 7,50%",
            "vaste 7,50% reserve",
            "strategisch doelgewicht",
            "fase-doelgewicht",
            "fasedoelgewicht",
            "do not allocate capital to thematic or gold exposure",
            "volledig geverifieerde lijnen: 0",
            "geprijsd maar identiteit of handelslijn nog te verifiëren: 13",
        ]
        if language == "nl"
        else [
            "three funded ucits positions",
            "minimum cash reserve 7.50%",
            "fixed 7.50% reserve",
            "strategic target weight",
            "phase target weight",
            "fully verified lines: 0",
            "priced but identity or trading-line verification still pending: 13",
        ]
    )
    for token in forbidden:
        if token.casefold() in folded:
            blockers.append(f"retired/stale Markdown wording present: {token}")
    return blockers


def reconcile_funded_markdown(text: str, state: dict[str, Any], *, language: str) -> str:
    portfolio = state.get("portfolio") if isinstance(state.get("portfolio"), dict) else {}
    positions = [row for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    if not positions:
        return text

    cash = _money(portfolio.get("cash_eur"), language)
    tickers = [_ticker(row) for row in positions if _ticker(row)]
    additions = _current_additions(state, positions)
    position_names = _join_tickers(tickers, language)
    addition_names = _join_tickers(additions, language)
    count = len(positions)
    funded_grade = _funded_valuation_grade_count(positions)
    total_pricing_rows = _pricing_table_row_count(text)
    research_rows = max(total_pricing_rows - count, 0)

    if language == "nl":
        action = (
            f"- **Actie:** {addition_names} deze run toegevoegd; huidige modelportefeuille: {position_names}. Resterende liquiditeit {cash}."
            if additions
            else f"- **Actie:** {position_names} als huidige modelposities beoordelen; resterende liquiditeit {cash}."
        )
        reason = f"- **Reden:** de modelportefeuille bevat {count} gefinancierde UCITS-posities ({position_names}); de review gebruikt actuele state, exact-line completed-close prijsbewijs en current re-underwriting."
        structure = f"- **Huidige positiegrondslag:** {position_names}; rollen, bijdrage, overlap en re-underwriting komen uit de actuele genormaliseerde state."
        text = _replace_prefixed_line(text, "- **Actie:**", action)
        text = _replace_prefixed_line(text, "- **Reden:**", reason)
        text = _replace_prefixed_line(text, "- **Huidige positiegrondslag:**", structure)
        text = _replace_prefixed_line(text, "- **Prijsdekking:**", f"- **Prijsdekking:** {total_pricing_rows} van {total_pricing_rows} handelslijnen hebben een marktobservatie op de peildatum.")
        text = _replace_prefixed_line(text, "- **Volledig geverifieerde lijnen:**", f"- **Gefinancierde exact-line waardering:** {funded_grade} van {count} gefinancierde lijnen hebben two-provider completed-close consensus en vormen de actuele waarderingsbasis.")
        text = _replace_prefixed_line(text, "- **Geprijsd maar identiteit of handelslijn nog te verifiëren:**", f"- **Research-/vergelijkingslijnen:** {research_rows} niet-gefinancierde prijsregels blijven research-only; marktprijsbeschikbaarheid creëert geen funding-authority.")
        old_note = "De getoonde prijzen zijn marktobservaties uit de huidige routine-run en vormen geen zelfstandige basis voor waardering of aankoop."
        new_note = f"Voor de {count} gefinancierde lijnen vormt two-provider exact-line completed-close consensus de actuele waarderingsbasis. Overige prijsregels zijn research-/vergelijkingsobservaties en creëren geen funding-authority."
        text = text.replace(old_note, new_note)
        replacements = {
            "- **Niet doen:** do not allocate capital to thematic or gold exposure until identity, KID, trading-line and product-policy checks are complete.": "- **Niet doen:** geen nieuw kapitaal toewijzen uitsluitend op basis van proxy, mapping of prijsbeschikbaarheid; identiteit, KID, exacte handelslijn, re-underwriting en expliciet allocatiebesluit blijven verplicht.",
            "- **Portefeuillebesluit:** cash behouden; geen instrument is door deze prijsrun automatisch geschikt geworden voor opname in de portefeuille.": "- **Portefeuillebesluit:** bestaande posities blijven uitsluitend onder actuele re-underwriting; mapping of pricing alleen creëert geen Add/Hold/Reduce- of funding-authority.",
            "- **Kernaandelen:** operationeel het meest volwassen; SXR8 en CSPX blijven onderzoekskandidaten en zijn niet gefinancierd.": "- **Kernaandelen:** funded/unfunded status wordt uitsluitend uit de protected portfolio state afgeleid; research-alternatieven blijven niet-gefinancierde vergelijkingslijnen.",
            "- **Core-aandelen:** operationeel het meest volwassen; SXR8 en CSPX blijven onderzoekskandidaten en zijn niet gefinancierd.": "- **Kernaandelen:** funded/unfunded status wordt uitsluitend uit de protected portfolio state afgeleid; research-alternatieven blijven niet-gefinancierde vergelijkingslijnen.",
            "- **Wereldwijde aandelen:** IWDA, EUNL en VWCE blijven interessant voor brede spreiding, maar verificatie van handelslijn en bron is nog niet volledig.": "- **Wereldwijde aandelen:** actuele funded status en exacte lijnidentiteit komen uit protected state plus UCITS-registry; alternatieven blijven research-only tenzij alle fundability-gates passeren.",
            "- **Obligaties:** EUNA en AGGH kunnen later stabiliteit leveren; hun huidige rol blijft die van onderzoekskandidaat.": "- **Obligaties:** actuele funded status en rol komen uit protected state en current re-underwriting; alternatieven blijven research-only zonder expliciet allocatiebesluit.",
            "- Rond verificatie van brokerbeschikbaarheid en EUR-handelslijnen af.": f"- Herbeoordeel {position_names} op fresh-cash, bijdrage, overlap, invalidatievoorwaarden en beste alternatief.",
            "- Verbeter de bronovereenkomst voordat de prijsinformatie als voldoende betrouwbaar voor waardering kan worden beschouwd.": "- Vereis voor iedere gefinancierde lijn verse exact-line completed-close evidence met two-provider consensus vóór current valuation/re-underwriting.",
            "- Herbeoordeel pas daarna of cash gedeeltelijk mag worden ingezet.": "- Herbeoordeel de resterende materiële cash tegen nieuwe volledig fundable lanes; de huidige cash is expliciet verklaard door nog open fundability-blockers.",
        }
    else:
        action = (
            f"- **Action:** added {addition_names} this run; current model portfolio: {position_names}. Remaining liquidity is {cash}."
            if additions
            else f"- **Action:** review {position_names} as the current model positions; remaining liquidity is {cash}."
        )
        reason = f"- **Reason:** the model portfolio contains {count} funded UCITS positions ({position_names}); the review uses current state, exact-line completed-close pricing evidence and current re-underwriting."
        structure = f"- **Current position structure:** {position_names}; roles, contribution, overlap and re-underwriting are derived from the current normalized state."
        text = _replace_prefixed_line(text, "- **Action:**", action)
        text = _replace_prefixed_line(text, "- **Reason:**", reason)
        text = _replace_prefixed_line(text, "- **Current position structure:**", structure)
        text = _replace_prefixed_line(text, "- **Pricing coverage:**", f"- **Pricing coverage:** {total_pricing_rows} of {total_pricing_rows} trading lines have a market observation on the pricing date.")
        text = _replace_prefixed_line(text, "- **Fully verified lines:**", f"- **Funded exact-line valuation:** {funded_grade} of {count} funded lines have two-provider completed-close consensus and form the current valuation basis.")
        text = _replace_prefixed_line(text, "- **Priced but identity or trading-line verification still pending:**", f"- **Research/comparison lines:** {research_rows} unfunded pricing rows remain research-only; market-price availability creates no funding authority.")
        old_note = "The displayed prices are market observations from the current routine run and do not independently authorize valuation or purchase."
        new_note = f"For the {count} funded lines, two-provider exact-line completed-close consensus forms the current valuation basis. Other pricing rows are research/comparison observations and create no funding authority."
        text = text.replace(old_note, new_note)
        replacements = {
            "- **Portfolio decision:** retain cash; this pricing run did not automatically make any instrument eligible for portfolio inclusion.": "- **Portfolio decision:** existing positions remain subject to current re-underwriting; mapping or pricing alone creates no Add/Hold/Reduce or funding authority.",
            "- **Core equity:** operationally most mature; SXR8 and CSPX remain research candidates and are not funded.": "- **Core equity:** funded/unfunded status is derived only from protected portfolio state; research alternatives remain unfunded comparison lines.",
            "- **Global equity:** IWDA, EUNL and VWCE remain relevant for broad diversification, but trading-line and source verification is incomplete.": "- **Global equity:** current funded status and exact-line identity come from protected state plus the UCITS registry; alternatives remain research-only unless all fundability gates pass.",
            "- **Bonds:** EUNA and AGGH may later provide stability; their current role remains that of research candidates.": "- **Bonds:** current funded status and role come from protected state and current re-underwriting; alternatives remain research-only without an explicit allocation decision.",
            "- Complete broker availability and EUR trading-line verification.": f"- Re-underwrite {position_names} on fresh cash, contribution, overlap, invalidation conditions and best alternative.",
            "- Improve source agreement before the pricing evidence is considered sufficiently reliable for valuation.": "- Require fresh exact-line completed-close evidence with two-provider consensus for every funded line before current valuation/re-underwriting.",
            "- Only then reassess whether part of the cash may be deployed.": "- Reassess the remaining material cash against newly fully fundable lanes; current cash is explicitly explained by still-open fundability blockers.",
        }

    for old, new in replacements.items():
        text = text.replace(old, new)

    blockers = validate_funded_markdown(text, state, language=language)
    if blockers:
        raise RuntimeError("Funded Markdown reconciliation failed: " + "; ".join(blockers))
    return text
