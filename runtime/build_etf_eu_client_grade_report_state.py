from __future__ import annotations

import argparse
import csv
import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import yaml


LANE_DEFINITIONS: list[dict[str, Any]] = [
    {
        "lane_id": "core_us_equity",
        "name_nl": "Amerikaanse kernaandelen via UCITS",
        "name_en": "Core U.S. equity through UCITS",
        "tickers": ["CSPX", "SXR8"],
        "research_reference": "SPY",
        "structural_score": 5,
        "horizon": "3–12 months",
        "why_nl": "Brede Amerikaanse winstgroei en liquiditeit maken dit de meest volwassen implementatielijn.",
        "why_en": "Broad U.S. earnings exposure and liquidity make this the most mature implementation lane.",
    },
    {
        "lane_id": "global_equity",
        "name_nl": "Wereldwijde aandelen",
        "name_en": "Global equity",
        "tickers": ["IWDA", "EUNL", "VWCE"],
        "research_reference": "VT",
        "structural_score": 4,
        "horizon": "3–12 months",
        "why_nl": "Brede wereldwijde spreiding verlaagt de afhankelijkheid van één regio of factor.",
        "why_en": "Broad global diversification reduces dependence on one region or factor.",
    },
    {
        "lane_id": "emerging_equity",
        "name_nl": "Opkomende markten",
        "name_en": "Emerging-market equity",
        "tickers": ["EMIM"],
        "research_reference": "EEM",
        "structural_score": 3,
        "horizon": "6–18 months",
        "why_nl": "Aanvullende groeibronnen en waarderingsspreiding, maar met hogere valuta- en beleidsrisico’s.",
        "why_en": "Additional growth and valuation diversification, with higher currency and policy risk.",
    },
    {
        "lane_id": "technology_semiconductors",
        "name_nl": "Technologie en halfgeleiders",
        "name_en": "Technology and semiconductors",
        "tickers": ["CNDX", "SXRV", "SMH"],
        "research_reference": "QQQ / SMH",
        "structural_score": 5,
        "horizon": "3–12 months",
        "why_nl": "AI-infrastructuur en rekenkracht blijven structurele groeidrijvers, maar concentratierisico is hoog.",
        "why_en": "AI infrastructure and compute remain structural growth drivers, but concentration risk is high.",
    },
    {
        "lane_id": "aggregate_bonds",
        "name_nl": "Wereldwijde obligaties",
        "name_en": "Global aggregate bonds",
        "tickers": ["EUNA", "AGGH"],
        "research_reference": "AGG",
        "structural_score": 3,
        "horizon": "3–12 months",
        "why_nl": "Kan later stabiliteit en renterisicospreiding bieden zodra handelslijnen en prijsbasis zijn bevestigd.",
        "why_en": "May later add stability and duration diversification once trading lines and pricing are confirmed.",
    },
    {
        "lane_id": "infrastructure",
        "name_nl": "Infrastructuur en elektrificatie",
        "name_en": "Infrastructure and electrification",
        "tickers": ["INFR"],
        "research_reference": "PAVE / GRID",
        "structural_score": 4,
        "horizon": "6–18 months",
        "why_nl": "Netuitbreiding, datacenters en elektrificatie ondersteunen de structurele investeringscase.",
        "why_en": "Grid investment, data centres and electrification support the structural case.",
    },
    {
        "lane_id": "gold_policy",
        "name_nl": "Goud en harde activa",
        "name_en": "Gold and hard assets",
        "tickers": ["SGLN"],
        "research_reference": "GLD",
        "structural_score": 2,
        "horizon": "6–18 months",
        "why_nl": "Diversificatiepotentieel bestaat, maar de Europese ETC-structuur vereist een expliciete beleidsbeslissing.",
        "why_en": "Diversification potential exists, but the European ETC structure requires an explicit policy decision.",
    },
]

REGIME_NL = {
    "Risk-on growth": "Risk-on groei",
    "Risk-on narrow leadership": "Risk-on met smal marktleiderschap",
    "Policy Transition / Mixed Regime": "Beleidstransitie / gemengd regime",
    "Policy transition / mixed regime": "Beleidstransitie / gemengd regime",
    "Unknown": "Onbekend",
}

STANCE_NL = {
    "Restrictive / data-dependent": "Restrictief / datagedreven",
    "Neutral / transition": "Neutraal / overgangsfase",
    "Tightening / inflation-sensitive": "Verkrappend / inflatiegevoelig",
    "Gradual normalization risk": "Risico van geleidelijke normalisatie",
    "Supportive but credibility-sensitive": "Ondersteunend maar geloofwaardigheidsgevoelig",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Required JSON input not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Required YAML input not found: {path}")
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _load_history(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            try:
                nav = float(row.get("nav_eur") or 0)
                cash = float(row.get("cash_eur") or 0)
                invested = float(row.get("invested_market_value_eur") or 0)
            except (TypeError, ValueError):
                continue
            rows.append(
                {
                    "date": str(row.get("date") or "").strip(),
                    "nav_eur": nav,
                    "cash_eur": cash,
                    "invested_market_value_eur": invested,
                    "since_inception_return_pct": _float_or_none(row.get("since_inception_return_pct")),
                    "drawdown_pct": _float_or_none(row.get("drawdown_pct")),
                    "comment": str(row.get("comment") or "").strip(),
                    "source_report": str(row.get("source_report") or "").strip(),
                }
            )
    return [row for row in rows if row["date"]]


def _float_or_none(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(str(value).replace(",", "").replace("%", ""))
    except (TypeError, ValueError):
        return None


def _parse_date(value: Any) -> date | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        return date.fromisoformat(raw[:10])
    except ValueError:
        return None


def _portfolio_summary(state: dict[str, Any]) -> dict[str, Any]:
    positions = state.get("positions") if isinstance(state.get("positions"), list) else []
    starting = float(state.get("starting_capital_eur") or 0)
    cash = float(state.get("cash_eur") or 0)
    invested = float(state.get("invested_market_value_eur") or 0)
    nav = float(state.get("nav_eur") or (cash + invested))
    since = ((nav / starting) - 1.0) * 100.0 if starting else 0.0
    return {
        "portfolio_mode": state.get("portfolio_mode"),
        "base_currency": state.get("base_currency") or "EUR",
        "inception_date": state.get("inception_date"),
        "starting_capital_eur": starting,
        "cash_eur": cash,
        "invested_market_value_eur": invested,
        "nav_eur": nav,
        "since_inception_return_pct": since,
        "position_count": len(positions),
        "positions": positions,
        "cash_weight_pct": (cash / nav * 100.0) if nav else 0.0,
    }


def _macro_surface(pack: dict[str, Any], report_date: str) -> dict[str, Any]:
    pack_date = _parse_date(pack.get("report_date") or pack.get("generated_at_utc"))
    current_date = _parse_date(report_date)
    age_days = (current_date - pack_date).days if pack_date and current_date else None
    fresh = age_days is not None and age_days <= 14
    regime = pack.get("regime") if isinstance(pack.get("regime"), dict) else {}
    memory = pack.get("regime_memory") if isinstance(pack.get("regime_memory"), dict) else {}
    banks = pack.get("central_banks") if isinstance(pack.get("central_banks"), dict) else {}
    fed = banks.get("fed") if isinstance(banks.get("fed"), dict) else {}
    ecb = banks.get("ecb") if isinstance(banks.get("ecb"), dict) else {}
    catalysts = []
    for item in pack.get("policy_catalysts") or []:
        if isinstance(item, dict) and item.get("transfer_to_report") is True:
            catalysts.append(
                {
                    "area": item.get("policy_area"),
                    "signal": item.get("latest_signal"),
                    "direction": item.get("direction"),
                    "confidence": item.get("confidence"),
                    "horizon": item.get("time_horizon"),
                }
            )
    confidence = _float_or_none(regime.get("confidence"))
    return {
        "source_report_date": pack.get("report_date"),
        "source_generated_at_utc": pack.get("generated_at_utc"),
        "age_days": age_days,
        "fresh_for_report": fresh,
        "freshness_status": "current" if fresh else "historical_context_refresh_required",
        "regime": regime.get("current") or "Unknown",
        "regime_nl": REGIME_NL.get(str(regime.get("current") or "Unknown"), str(regime.get("current") or "Onbekend")),
        "confidence_pct": round((confidence or 0) * 100.0, 0) if confidence is not None and confidence <= 1 else confidence,
        "what_changed": list(regime.get("what_changed") or [])[:3],
        "memory_summary": ((memory.get("report_transfer") or {}).get("summary") if isinstance(memory.get("report_transfer"), dict) else None),
        "decision_rule": memory.get("decision_rule"),
        "fed": {
            "stance": fed.get("stance"),
            "stance_nl": STANCE_NL.get(str(fed.get("stance") or ""), str(fed.get("stance") or "Niet beschikbaar")),
            "implication": fed.get("etf_implication"),
            "main_risk": fed.get("main_risk"),
        },
        "ecb": {
            "stance": ecb.get("stance"),
            "stance_nl": STANCE_NL.get(str(ecb.get("stance") or ""), str(ecb.get("stance") or "Niet beschikbaar")),
            "implication": ecb.get("etf_implication"),
            "main_risk": ecb.get("main_risk"),
        },
        "portfolio_implications": list(pack.get("portfolio_implications") or [])[:3],
        "catalysts": catalysts[:3],
    }


def _registry_index(registry: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    by_isin: dict[str, dict[str, Any]] = {}
    by_ticker: dict[str, dict[str, Any]] = {}
    for fund in registry.get("funds") or []:
        if not isinstance(fund, dict):
            continue
        isin = str(fund.get("isin") or "").strip().upper()
        if isin and isin != "TBD":
            by_isin[isin] = fund
        for line in fund.get("trading_lines") or []:
            if not isinstance(line, dict):
                continue
            ticker = str(line.get("exchange_ticker") or "").strip().upper()
            if ticker:
                by_ticker[ticker] = fund
    return by_isin, by_ticker


def _pricing_rows(pricing: dict[str, Any], registry: dict[str, Any]) -> list[dict[str, Any]]:
    by_isin, by_ticker = _registry_index(registry)
    rows: list[dict[str, Any]] = []
    for row in pricing.get("rows") or []:
        if not isinstance(row, dict):
            continue
        ticker = str(row.get("ticker") or "").strip().upper()
        isin = str(row.get("isin") or "").strip().upper()
        fund = by_isin.get(isin) or by_ticker.get(ticker) or {}
        proxy = fund.get("us_research_proxy")
        verified = row.get("verification_status") == "verified_ucits_trading_line"
        priced = row.get("pricing_status") == "priced_non_authoritative" and row.get("close_price") is not None
        rows.append(
            {
                "ticker": ticker,
                "isin": isin,
                "fund_name": row.get("fund_name"),
                "exchange": row.get("exchange"),
                "venue_code": row.get("venue_code"),
                "currency": row.get("currency"),
                "close_date": row.get("close_date"),
                "close_price": row.get("close_price"),
                "pricing_status": row.get("pricing_status"),
                "verification_status": row.get("verification_status"),
                "priced": priced,
                "verified": verified,
                "research_reference": proxy,
                "instrument_type": row.get("instrument_type"),
                "source_name": row.get("source_name"),
                "source_quality_status": row.get("source_quality_status"),
                "blockers": list(row.get("blockers") or []),
            }
        )
    return sorted(rows, key=lambda item: (item["fund_name"] or "", item["ticker"]))


def _lane_rows(pricing_rows: list[dict[str, Any]], registry: dict[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    registry_funds = [fund for fund in registry.get("funds") or [] if isinstance(fund, dict)]
    for definition in LANE_DEFINITIONS:
        tickers = set(definition["tickers"])
        members = [row for row in pricing_rows if row["ticker"] in tickers]
        priced = [row for row in members if row["priced"]]
        verified = [row for row in members if row["verified"]]
        policy_blocked = definition["lane_id"] == "gold_policy"
        if policy_blocked:
            status = "policy_blocked"
            implementation_score = 1
            next_nl = "Beslis expliciet of ETC-structuren binnen het productbeleid zijn toegestaan."
            next_en = "Decide explicitly whether ETC structures are permitted by product policy."
        elif verified:
            status = "operationally_mature_not_funded"
            implementation_score = 5 if len(verified) == len(members) and members else 4
            next_nl = "Bevestig brokerbeschikbaarheid, actuele prijsbasis en afzonderlijk allocatiebesluit."
            next_en = "Confirm broker availability, current pricing basis and a separate allocation decision."
        elif priced:
            status = "watchlist_verification_required"
            implementation_score = 3
            next_nl = "Rond identiteit, KID, handelslijn en bronovereenkomst af."
            next_en = "Complete identity, KID, trading-line and source-agreement checks."
        else:
            status = "research_only_not_priced"
            implementation_score = 1
            next_nl = "Voltooi register- en prijsdekking voordat vergelijking zinvol is."
            next_en = "Complete registry and pricing coverage before comparison is decision-useful."
        # Registry-only lane candidates remain visible even when not in the current pricing basket.
        registry_matches = []
        for fund in registry_funds:
            proxy = str(fund.get("us_research_proxy") or "").upper()
            if proxy and proxy in str(definition["research_reference"]).upper():
                registry_matches.append(fund.get("fund_name"))
        result.append(
            {
                **definition,
                "members": members,
                "member_count": len(members),
                "priced_count": len(priced),
                "verified_count": len(verified),
                "candidate_tickers": [row["ticker"] for row in members] or definition["tickers"],
                "registry_candidates": [value for value in registry_matches if value],
                "implementation_score": implementation_score,
                "status": status,
                "next_confirmation_nl": next_nl,
                "next_confirmation_en": next_en,
                "allocation_authority": False,
            }
        )
    return result


def _verification_funnel(pricing_rows: list[dict[str, Any]], portfolio: dict[str, Any]) -> dict[str, Any]:
    priced = [row for row in pricing_rows if row["priced"]]
    verified = [row for row in pricing_rows if row["verified"]]
    unresolved = [row for row in pricing_rows if not row["priced"]]
    return {
        "observed_lines": len(pricing_rows),
        "priced_lines": len(priced),
        "verified_lines": len(verified),
        "unresolved_lines": len(unresolved),
        "funded_positions": portfolio["position_count"],
        "cash_eur": portfolio["cash_eur"],
        "decision": "retain_cash_pending_separate_allocation_decision",
    }


def _allocation_map(portfolio: dict[str, Any], lanes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    lane_by_id = {lane["lane_id"]: lane for lane in lanes}
    return [
        {"segment_nl": "Cash", "segment_en": "Cash", "stance_nl": "Overwogen / huidig 100%", "stance_en": "Overweight / currently 100%", "note_nl": "Beschermt kapitaal zolang verificatie en allocatiebesluit ontbreken.", "note_en": "Protects capital while verification and an allocation decision remain incomplete."},
        {"segment_nl": "Amerikaanse kernaandelen", "segment_en": "Core U.S. equity", "stance_nl": "Eerstvolgende validatiekandidaat", "stance_en": "Next validation candidate", "note_nl": f"{lane_by_id['core_us_equity']['verified_count']} geverifieerde handelslijnen; nog niet gefinancierd.", "note_en": f"{lane_by_id['core_us_equity']['verified_count']} verified trading lines; not funded."},
        {"segment_nl": "Wereldwijde aandelen", "segment_en": "Global equity", "stance_nl": "Volglijst", "stance_en": "Watchlist", "note_nl": "Brede spreiding, maar lijn- en bronverificatie is nog niet volledig.", "note_en": "Broad diversification, but trading-line and source verification is incomplete."},
        {"segment_nl": "Technologie en halfgeleiders", "segment_en": "Technology and semiconductors", "stance_nl": "Volglijst / concentratiebewaking", "stance_en": "Watchlist / concentration review", "note_nl": "Sterke structurele case; geen inzet vóór volledige verificatie en portefeuillekader.", "note_en": "Strong structural case; no allocation before full verification and portfolio framing."},
        {"segment_nl": "Obligaties", "segment_en": "Bonds", "stance_nl": "Volglijst", "stance_en": "Watchlist", "note_nl": "Potentiële stabilisator; handelslijn- en prijsdekking nog onvolledig.", "note_en": "Potential stabiliser; trading-line and pricing coverage remain incomplete."},
        {"segment_nl": "Goud / harde activa", "segment_en": "Gold / hard assets", "stance_nl": "Beleidsmatig geblokkeerd", "stance_en": "Policy blocked", "note_nl": "ETC-structuur valt buiten het huidige UCITS-only beleid.", "note_en": "ETC structure falls outside the current UCITS-only policy."},
    ]


def _second_order_effects() -> list[dict[str, str]]:
    return [
        {
            "driver_nl": "Cash-only startpositie",
            "driver_en": "Cash-only starting position",
            "first_nl": "Geen marktdrawdown uit gefinancierde posities.",
            "first_en": "No funded-position market drawdown.",
            "second_nl": "Opportunitykosten lopen op wanneer validatie te lang duurt.",
            "second_en": "Opportunity cost rises if verification takes too long.",
            "implication_nl": "Versnel verificatie, maar houd een afzonderlijk allocatiebesluit verplicht.",
            "implication_en": "Accelerate verification while retaining a separate allocation decision.",
        },
        {
            "driver_nl": "Twee geverifieerde S&P 500-handelslijnen",
            "driver_en": "Two verified S&P 500 trading lines",
            "first_nl": "Implementatierisico daalt voor de kernblootstelling.",
            "first_en": "Implementation risk falls for core exposure.",
            "second_nl": "Keuze tussen USD- en EUR-handelslijn beïnvloedt broker, valuta en operationele eenvoud.",
            "second_en": "Choosing USD versus EUR trading lines affects broker access, currency and operational simplicity.",
            "implication_nl": "Vergelijk brokerbeschikbaarheid en totale uitvoeringskosten vóór allocatie.",
            "implication_en": "Compare broker availability and total execution cost before allocation.",
        },
        {
            "driver_nl": "Meerdere lijnen per ISIN",
            "driver_en": "Multiple lines per ISIN",
            "first_nl": "Fondsidentiteit is duidelijker dan tickeridentiteit.",
            "first_en": "Fund identity is clearer than ticker identity.",
            "second_nl": "Een verkeerde lijnkeuze kan liquiditeits-, valuta- of prijsverschillen introduceren.",
            "second_en": "Selecting the wrong line can introduce liquidity, currency or pricing differences.",
            "implication_nl": "Behoud ISIN-first en maak de handelslijn een expliciete beslisvariabele.",
            "implication_en": "Remain ISIN-first and treat the trading line as an explicit decision variable.",
        },
        {
            "driver_nl": "Technologie- en halfgeleiderkandidaten",
            "driver_en": "Technology and semiconductor candidates",
            "first_nl": "Hogere structurele groeiblootstelling.",
            "first_en": "Higher structural growth exposure.",
            "second_nl": "Meer factorconcentratie en hogere volatiliteit dan brede kernblootstelling.",
            "second_en": "Greater factor concentration and volatility than broad core exposure.",
            "implication_nl": "Behandel als satellietblootstelling, niet als automatische kernpositie.",
            "implication_en": "Treat as satellite exposure, not an automatic core holding.",
        },
    ]


def _risks(macro: dict[str, Any], pricing_rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    unresolved = len([row for row in pricing_rows if not row["priced"]])
    pending = len([row for row in pricing_rows if not row["verified"]])
    risks = [
        {
            "risk_nl": "Prijsobservaties zijn nog niet waarderingswaardig.",
            "risk_en": "Price observations are not yet valuation-grade.",
            "invalidation_nl": "Promoveer pas wanneer bronovereenkomst en prijslineage voldoende sterk zijn.",
            "invalidation_en": "Promote only after source agreement and pricing lineage are sufficiently strong.",
        },
        {
            "risk_nl": f"{pending} handelslijnen wachten nog op volledige verificatie.",
            "risk_en": f"{pending} trading lines still require full verification.",
            "invalidation_nl": "Geen financiering vóór identiteit, KID, handelslijn en brokerbeschikbaarheid zijn bevestigd.",
            "invalidation_en": "No funding before identity, KID, trading line and broker availability are confirmed.",
        },
        {
            "risk_nl": f"{unresolved} lijn heeft geen bruikbare prijs in deze run.",
            "risk_en": f"{unresolved} line has no usable price in this run.",
            "invalidation_nl": "Laat onopgeloste lijnen buiten vergelijking en allocatie.",
            "invalidation_en": "Keep unresolved lines outside comparison and allocation.",
        },
        {
            "risk_nl": "Technologiekandidaten kunnen een te smalle factorblootstelling creëren.",
            "risk_en": "Technology candidates may create overly narrow factor exposure.",
            "invalidation_nl": "Beperk satellietgewicht en vergelijk altijd met brede kernblootstelling.",
            "invalidation_en": "Cap satellite weight and always compare with broad core exposure.",
        },
        {
            "risk_nl": "Goudblootstelling gebruikt vaak ETC-structuren buiten het huidige beleid.",
            "risk_en": "Gold exposure often uses ETC structures outside the current policy.",
            "invalidation_nl": "Geen opname zonder expliciete productbeleidsbeslissing.",
            "invalidation_en": "No inclusion without an explicit product-policy decision.",
        },
    ]
    if not macro["fresh_for_report"]:
        risks.insert(
            0,
            {
                "risk_nl": "Het beschikbare macrobeleidspakket is verouderd voor een actuele productieclaim.",
                "risk_en": "The available macro policy pack is stale for a current production claim.",
                "invalidation_nl": "Ververs macrodata vóór productiepromotie; gebruik de huidige waarden uitsluitend als historische context.",
                "invalidation_en": "Refresh macro data before production promotion; use current values as historical context only.",
            },
        )
    return risks


def _equity_curve(history: list[dict[str, Any]], portfolio: dict[str, Any]) -> dict[str, Any]:
    points = [{"date": row["date"], "nav_eur": row["nav_eur"]} for row in history]
    meaningful = len(points) >= 2 and (portfolio["position_count"] > 0 or len({round(row["nav_eur"], 2) for row in points}) > 1)
    latest_matches = bool(points) and abs(points[-1]["nav_eur"] - portfolio["nav_eur"]) <= 0.05
    return {
        "show_chart": meaningful,
        "points": points,
        "point_count": len(points),
        "latest_nav_matches_state": latest_matches,
        "fallback_nl": "De EU-modelportefeuille staat sinds de start volledig in cash; er is nog geen beleggingsrendement opgebouwd.",
        "fallback_en": "The EU model portfolio has remained fully in cash since inception; no investment return has been generated yet.",
        "activation_rule": "show after at least two meaningful validated NAV observations or a funded position",
    }


def build_state(args: argparse.Namespace) -> dict[str, Any]:
    portfolio_raw = _load_json(Path(args.portfolio_state))
    pricing_raw = _load_json(Path(args.pricing_artifact))
    macro_raw = _load_json(Path(args.macro_pack)) if Path(args.macro_pack).exists() else {}
    registry = _load_yaml(Path(args.registry))
    history = _load_history(Path(args.valuation_history))

    portfolio = _portfolio_summary(portfolio_raw)
    pricing_rows = _pricing_rows(pricing_raw, registry)
    lanes = _lane_rows(pricing_rows, registry)
    macro = _macro_surface(macro_raw, args.report_date)
    curve = _equity_curve(history, portfolio)

    blockers: list[str] = []
    if not pricing_raw.get("min_threshold_met"):
        blockers.append("pricing coverage threshold not met")
    if portfolio["position_count"] == 0 and portfolio["invested_market_value_eur"] != 0:
        blockers.append("cash-only position count conflicts with invested market value")
    if history and not curve["latest_nav_matches_state"]:
        blockers.append("latest valuation-history NAV does not reconcile to current portfolio state")

    state = {
        "schema_version": "etf_eu_client_grade_report_state_v1",
        "artifact_type": "etf_eu_client_grade_report_state",
        "generated_at_utc": _utc_now(),
        "run_id": args.run_id,
        "source_run_id": args.source_run_id,
        "report_date": args.report_date,
        "report_suffix": args.report_suffix,
        "source_of_truth_repo": "market-predictions/weekly-etf-eu",
        "reference_architecture_repo": "market-predictions/weekly-etf",
        "upstream_pattern_adapted": "normalized runtime report state, macro client surface, deterministic conditional equity curve and component renderer",
        "sources": {
            "portfolio_state": args.portfolio_state,
            "valuation_history": args.valuation_history,
            "pricing_artifact": args.pricing_artifact,
            "macro_pack": args.macro_pack,
            "ucits_registry": args.registry,
        },
        "authority": {
            "canonical_identity": "isin_first",
            "us_etfs_research_only": True,
            "valuation_grade": False,
            "funding_authority": False,
            "portfolio_mutation": False,
            "production_delivery_authority": False,
        },
        "portfolio": portfolio,
        "valuation_history": history,
        "equity_curve": curve,
        "macro": macro,
        "pricing": {
            "line_count": len(pricing_rows),
            "priced_line_count": len([row for row in pricing_rows if row["priced"]]),
            "verified_line_count": len([row for row in pricing_rows if row["verified"]]),
            "unresolved_line_count": len([row for row in pricing_rows if not row["priced"]]),
            "as_of": max((str(row["close_date"]) for row in pricing_rows if row["close_date"]), default=None),
            "rows": pricing_rows,
        },
        "opportunity_radar": lanes,
        "allocation_map": _allocation_map(portfolio, lanes),
        "second_order_effects": _second_order_effects(),
        "risks": _risks(macro, pricing_rows),
        "verification_funnel": _verification_funnel(pricing_rows, portfolio),
        "conditional_sections": {
            "portfolio_curve": curve["show_chart"],
            "current_positions": portfolio["position_count"] > 0,
            "replacement_analysis": portfolio["position_count"] > 0,
            "rotation_plan": portfolio["position_count"] > 0,
            "cash_preservation_callout": not curve["show_chart"],
        },
        "next_run_input": {
            "portfolio_state": args.portfolio_state,
            "valuation_history": args.valuation_history,
            "pricing_artifact": args.pricing_artifact,
            "macro_refresh_required": not macro["fresh_for_report"],
            "priority_candidates": ["SXR8", "CSPX", "IWDA", "EUNL", "VWCE"],
            "required_actions": [
                "refresh macro policy pack",
                "verify broker availability and preferred EUR trading lines",
                "strengthen pricing source agreement",
                "take a separate allocation decision before funding",
            ],
        },
        "report_contract": {
            "investor_sections": [1, 2, 3, 4, 5, 6, 7],
            "analyst_sections": [8, 9, 10, 11, 12, 13, 14, 15],
            "target_page_range": [6, 12],
            "client_grade_v2": True,
        },
        "state_valid": not blockers,
        "blockers": blockers,
        "warnings": (["macro pack is stale and must be refreshed before production promotion"] if not macro["fresh_for_report"] else []),
    }
    return state


def main() -> None:
    parser = argparse.ArgumentParser(description="Build normalized Weekly ETF EU client-grade report state.")
    parser.add_argument("--portfolio-state", default="output/etf_eu_portfolio_state.json")
    parser.add_argument("--valuation-history", default="output/etf_eu_valuation_history.csv")
    parser.add_argument("--pricing-artifact", required=True)
    parser.add_argument("--macro-pack", default="output/macro/latest.json")
    parser.add_argument("--registry", default="config/ucits_symbol_registry.yml")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--source-run-id", required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--report-suffix", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    state = build_state(args)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(state, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"state_valid": state["state_valid"], "output": str(output), "blockers": state["blockers"], "warnings": state["warnings"]}, indent=2))
    if state["state_valid"] is not True:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
