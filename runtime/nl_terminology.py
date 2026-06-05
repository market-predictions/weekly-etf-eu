from __future__ import annotations

"""Canonical Dutch terminology contract for ETF report surfaces.

This module is the source of truth for Dutch enum/status/client-surface labels.
It deliberately contains data and small deterministic lookup helpers only.
Renderers, markdown scrubbers, delivery HTML overrides, validators and any
runtime safety layer should import from here instead of carrying one-off maps.
"""

from collections.abc import Mapping
from typing import Any

DUTCH_DISCLAIMER = (
    "Dit rapport wordt uitsluitend verstrekt voor informatieve en educatieve doeleinden. "
    "Het is geen beleggingsadvies, juridisch advies, fiscaal advies of financieel advies, "
    "en vormt geen aanbeveling om effecten te kopen, te verkopen of aan te houden. "
    "Het rapport houdt geen rekening met individuele beleggingsdoelen, financiële situatie "
    "of specifieke behoeften van de ontvanger. Beleggen brengt risico’s met zich mee, "
    "waaronder het risico op verlies van inleg."
)

ALLOWED_ENGLISH_TERMS = {
    "ETF", "ETFs", "ticker", "tickers", "cash", "hedge", "drawdown", "beta", "capex",
    "small-cap", "large-cap", "risk-on", "risk-off", "AI", "semiconductor", "outperformance",
    "watchlist", "UCITS", "USD", "EUR", "NAV",
}

SECTION_LABELS_NL: dict[str, str] = {
    "Weekly ETF Review": "Wekelijkse ETF-review",
    "Weekly ETF Pro Review": "Wekelijkse ETF-review",
    "Investor Report": "Beleggersrapport",
    "Investment Report": "Beleggersrapport",
    "Analyst Report": "Analistenrapport",
    "Executive Summary": "Kernsamenvatting",
    "Portfolio Action Snapshot": "Portefeuille-acties",
    "Regime Dashboard": "Regime-dashboard",
    "Structural Opportunity Radar": "Structurele kansenradar",
    "Short Opportunity Radar": "Shortkansenradar",
    "Key Risks / Invalidators": "Belangrijkste risico’s / invalidaties",
    "Bottom Line": "Conclusie",
    "Equity Curve and Portfolio Development": "Portefeuillecurve en portefeuilleontwikkeling",
    "ETF Position Performance": "Rendement huidige ETF-posities",
    "Asset Allocation Map": "Allocatiekaart",
    "Second-Order Effects Map": "Tweede-orde-effectenkaart",
    "Current Position Review": "Review huidige posities",
    "Best New Opportunities": "Beste nieuwe kansen",
    "Replacement Duel Table": "Vervangingsanalyse",
    "Replacement Duel Table v2": "Vervangingsanalyse",
    "Portfolio Rotation Plan": "Rotatieplan portefeuille",
    "Final Action Table": "Definitieve actietabel",
    "Position Changes Executed This Run": "Positiewijzigingen in deze run",
    "Current Portfolio Holdings and Cash": "Huidige posities en cash",
    "Continuity Input for Next Run": "Input voor de volgende run",
    "Carry-forward input for next run": "Input voor de volgende run",
    "Disclaimer": "Disclaimer",
}

SUMMARY_LABELS_NL: dict[str, str] = {
    "Primary Regime": "Primair regime",
    "PRIMARY REGIME": "PRIMAIR REGIME",
    "Primary regime": "Primair regime",
    "Geopolitical Regime": "Geopolitiek regime",
    "GEOPOLITICAL REGIME": "GEOPOLITIEK REGIME",
    "Geopolitical regime": "Geopolitiek regime",
    "Main Takeaway": "Kernconclusie",
    "MAIN TAKEAWAY": "KERNCONCLUSIE",
    "Main takeaway": "Kernconclusie",
}

TABLE_LABELS_NL: dict[str, str] = {
    "Theme": "Thema",
    "Primary ETF": "Primaire ETF",
    "Alternative ETF": "Alternatieve ETF",
    "Why it matters": "Waarom relevant",
    "Structural fit": "Structurele fit",
    "Macro timing": "Macro-timing",
    "Status": "Status",
    "What needs to happen": "Benodigde bevestiging",
    "Time horizon": "Tijdshorizon",
    "Short theme": "Shortthema",
    "Candidate ETF": "Kandidaat-ETF",
    "Short thesis": "Shortthese",
    "Trigger": "Trigger",
    "Invalidation": "Invalidering",
    "Confidence": "Vertrouwen",
    "Bucket": "Segment",
    "Stance": "Positionering",
    "Reason": "Toelichting",
    "Driver": "Drijver",
    "First-order effect": "Eerste-orde-effect",
    "Second-order effect": "Tweede-orde-effect",
    "Likely beneficiaries": "Waarschijnlijke winnaars",
    "Likely losers": "Kwetsbare segmenten",
    "ETF implication": "ETF-implicatie",
    "Timing": "Timing",
    "Ticker": "Ticker",
    "Action": "Actie",
    "Score": "Score",
    "Fresh cash": "Nieuw kapitaal",
    "Role": "Rol",
    "Next test": "Volgende toets",
    "Current holding": "Huidige positie",
    "Challenger": "Alternatief",
    "Alternative": "Alternatief",
    "1m edge": "1m relatieve sterkte",
    "3m edge": "3m relatieve sterkte",
    "1m relative strength": "1m relatieve sterkte",
    "3m relative strength": "3m relatieve sterkte",
    "Pricing basis": "Prijsbasis",
    "Decision": "Beoordeling",
    "Required trigger": "Benodigde bevestiging",
    "Current status": "Status",
    "Why I’m considering it": "Waarom op de radar",
    "Why I'm considering it": "Waarom op de radar",
    "Suggested Action": "Advies",
    "Conviction Tier": "Convictieniveau",
    "Total Score": "Totaalscore",
    "Portfolio Role": "Portefeuillerol",
    "Better Alternative Exists?": "Sterker alternatief beschikbaar?",
    "Short Reason": "Korte toelichting",
    "Existing/New": "Bestaand/nieuw",
    "Weight Inherited": "Vorig gewicht",
    "Target Weight": "Doelgewicht",
    "Previous weight %": "Vorig gewicht %",
    "New weight %": "Nieuw gewicht %",
    "Weight change %": "Gewichtswijziging %",
    "Shares delta": "Wijziging aantal stukken",
    "Action executed": "Uitgevoerde actie",
    "Funding source / note": "Financieringsbron / toelichting",
    "Starting capital": "Startkapitaal",
    "Invested market value": "Belegde marktwaarde",
    "Total portfolio value": "Totale portefeuillewaarde",
    "Since inception return": "Rendement sinds start",
    "EUR/USD used": "EUR/USD gebruikt",
    "Equity-curve state": "Status portefeuillecurve",
    "Notes": "Toelichting",
    "Date": "Datum",
    "Portfolio value (EUR)": "Portefeuillewaarde (EUR)",
    "Comment": "Opmerking",
    "Shares": "Aantal aandelen",
    "Price (local)": "Prijs (lokaal)",
    "Currency": "Valuta",
    "Market value (local)": "Marktwaarde (lokaal)",
    "Market value (EUR)": "Marktwaarde (EUR)",
    "Weight %": "Gewicht %",
    "ETF Name": "ETF-naam",
    "Direction": "Richting",
    "Avg Entry": "Gem. instap",
    "Current Price": "Huidige prijs",
    "P/L %": "P/L %",
    "Original Thesis": "Oorspronkelijke thesis",
}

ACTION_STATUS_LABELS_NL: dict[str, str] = {
    "Hold under review": "Aanhouden, onder herbeoordeling",
    "hold under review": "Aanhouden, onder herbeoordeling",
    "Hold / replaceable": "Aanhouden, maar vervangbaar",
    "Hold but replaceable": "Aanhouden, maar vervangbaar",
    "hold but replaceable": "Aanhouden, maar vervangbaar",
    "Hold": "Aanhouden",
    "hold": "Aanhouden",
    "Hold / monitor": "Aanhouden / monitoren",
    "hold / monitor": "Aanhouden / monitoren",
    "Add": "Toevoegen",
    "add": "Toevoegen",
    "Buy": "Kopen",
    "buy": "Kopen",
    "Increase": "Toevoegen",
    "increase": "Toevoegen",
    "Reduce": "Verlagen",
    "reduce": "Verlagen",
    "Decrease": "Verlagen",
    "decrease": "Verlagen",
    "Close": "Sluiten",
    "close": "Sluiten",
    "Sell": "Verkopen",
    "sell": "Verkopen",
    "None": "Geen",
    "none": "Geen",
    "null": "Geen",
    "nan": "Geen",
    "Existing": "Bestaand",
    "New": "Nieuw",
    "Yes": "Ja",
    "No": "Nee",
    "Active": "Actief",
    "Duel required": "Vervangingsanalyse vereist",
    "Under review": "Onder herbeoordeling",
    "under review": "onder herbeoordeling",
    "Watchlist / under review": "Volglijst / onder herbeoordeling",
    "Actionable now": "Nu actiegericht",
    "Neutral": "Neutraal",
    "Overweight": "Overwogen",
    "Underweight": "Onderwogen",
    "Watchlist": "Volglijst",
    "Immediate": "Direct",
    "Medium": "Gemiddeld",
    "High": "Hoog",
    "Low": "Laag",
    "Smaller / under review": "Kleiner / onder herbeoordeling",
    "smaller / under review": "Kleiner / onder herbeoordeling",
    "smaller": "Kleiner",
    "already reflected": "Al verwerkt",
}

ROTATION_ACTION_LABELS: dict[str, dict[str, str]] = {
    "en": {
        "hold": "Hold",
        "hold_with_override": "Hold with override",
        "reduce": "Reduce",
        "replace_partial": "Replace partial",
        "replace_full": "Replace full",
        "close": "Close",
        "add_from_cash": "Add from cash",
    },
    "nl": {
        "hold": "Aanhouden",
        "hold_with_override": "Aanhouden met override",
        "reduce": "Verlagen",
        "replace_partial": "Gedeeltelijk vervangen",
        "replace_full": "Volledig vervangen",
        "close": "Sluiten",
        "add_from_cash": "Toevoegen vanuit cash",
    },
}

DECISION_TRANSLATIONS_NL: dict[str, str] = {
    "Not fundable — close proof incomplete.": "Niet geschikt voor allocatie — sluitkoersbevestiging is onvolledig.",
    "Not fundable - close proof incomplete.": "Niet geschikt voor allocatie — sluitkoersbevestiging is onvolledig.",
    "Not fundable — close proof incomplete": "Niet geschikt voor allocatie — sluitkoersbevestiging is onvolledig",
    "Not fundable - close proof incomplete": "Niet geschikt voor allocatie — sluitkoersbevestiging is onvolledig",
    "Not fundable - valuation-grade challenger pricing required.": "Niet geschikt voor allocatie — waarderingswaardige prijsbevestiging voor het alternatief is vereist.",
    "Not fundable - valuation-grade challenger pricing required": "Niet geschikt voor allocatie — waarderingswaardige prijsbevestiging voor het alternatief is vereist",
    "Priced, but direct RS duel incomplete.": "Geprijsd, maar de directe relatieve-sterkteanalyse is onvolledig.",
    "Priced, but direct RS duel incomplete": "Geprijsd, maar de directe relatieve-sterkteanalyse is onvolledig",
    "Priced valuation-grade, but direct RS duel incomplete.": "Waarderingswaardig geprijsd, maar de directe relatieve-sterkteanalyse is onvolledig.",
    "Priced valuation-grade, but direct RS duel incomplete": "Waarderingswaardig geprijsd, maar de directe relatieve-sterkteanalyse is onvolledig",
    "Replacement trigger watch — challenger leading over 3m.": "Vervangingskandidaat blijft op de volglijst — het alternatief leidt over drie maanden.",
    "Replacement trigger watch - challenger leading over 3m.": "Vervangingskandidaat blijft op de volglijst — het alternatief leidt over drie maanden.",
    "Replacement trigger watch — challenger leading over 3m": "Vervangingskandidaat blijft op de volglijst — het alternatief leidt over drie maanden",
    "Replacement trigger watch - challenger leading over 3m": "Vervangingskandidaat blijft op de volglijst — het alternatief leidt over drie maanden",
    "Challenger improving; keep duel active.": "Het alternatief verbetert; houd de vervangingsanalyse actief.",
    "Challenger improving; keep duel active": "Het alternatief verbetert; houd de vervangingsanalyse actief",
    "Early 1m improvement only; wait for 3m confirmation.": "Alleen vroege 1-maands verbetering; wacht op 3-maands bevestiging.",
    "Early 1m improvement only; wait for 3m confirmation": "Alleen vroege 1-maands verbetering; wacht op 3-maands bevestiging",
    "Current holding still leads; no replacement.": "Huidige positie blijft sterker; geen vervanging.",
    "Current holding still leads; no replacement": "Huidige positie blijft sterker; geen vervanging",
}

TRIGGER_TRANSLATIONS_NL: dict[str, str] = {
    "Resolve both close prices before decision.": "Los beide slotkoersen op vóór een besluit.",
    "Resolve both close prices before decision": "Los beide slotkoersen op vóór een besluit",
    "Confirm thesis fit, liquidity and funding source.": "Bevestig aansluiting op de beleggingscase, liquiditeit en financieringsbron.",
    "Confirm thesis fit, liquidity and funding source": "Bevestig aansluiting op de beleggingscase, liquiditeit en financieringsbron",
    "Needs repeat 3m edge and capital source.": "Vereist herhaalde 3-maands voorsprong en duidelijke financieringsbron.",
    "Needs repeat 3m edge and capital source": "Vereist herhaalde 3-maands voorsprong en duidelijke financieringsbron",
    "Needs 3m confirmation.": "Vereist 3-maands bevestiging.",
    "Needs 3m confirmation": "Vereist 3-maands bevestiging",
    "Needs sustained relative outperformance.": "Vereist aanhoudende relatieve outperformance.",
    "Needs sustained relative outperformance": "Vereist aanhoudende relatieve outperformance",
    "Upgrade challenger to valuation-grade pricing before any funding decision.": "Verbeter de prijsbevestiging van het alternatief tot waarderingskwaliteit vóór een allocatiebesluit.",
    "Upgrade challenger to valuation-grade pricing before any funding decision": "Verbeter de prijsbevestiging van het alternatief tot waarderingskwaliteit vóór een allocatiebesluit",
}

PHRASE_REPLACEMENTS_NL: dict[str, str] = {
    "This report is for informational and educational purposes only; please see the disclaimer at the end.": "Dit rapport wordt uitsluitend verstrekt voor informatieve en educatieve doeleinden; zie de disclaimer aan het einde.",
    "Mixed / not yet decisive": "Gemengd / nog niet doorslaggevend",
    "Keep the current allocation disciplined.": "Houd de huidige allocatie gedisciplineerd.",
    "Keep the current allocation": "Houd de huidige allocatie",
    "Risk-on narrow US mega-cap leadership": "Risk-on met smal Amerikaans mega-capleiderschap",
    "Risk-on narrow U.S. mega-cap leadership": "Risk-on met smal Amerikaans mega-capleiderschap",
    "Risk-on narrow leadership": "Risk-on met smal marktleiderschap",
    "confidence": "vertrouwen",
    "Equity Curve (EUR)": "Portefeuillecurve (EUR)",
    "Portfolio value (EUR)": "Portefeuillewaarde (EUR)",
    "Performance is calculated": "Rendement wordt berekend",
    "with full valuation history": "met volledige waarderingshistorie",
    "Non-U.S.": "Niet-Amerikaanse",
    "non-U.S.": "niet-Amerikaanse",
    "No / under review": "Nee / onder herbeoordeling",
    "No / Under review": "Nee / onder herbeoordeling",
    "None / under review": "Geen / onder herbeoordeling",
    "None / Under review": "Geen / onder herbeoordeling",
    "Smaller / under review": "Kleiner / onder herbeoordeling",
    "Hold but replaceable": "Aanhouden, maar vervangbaar",
    "Aanhouden but replaceable": "Aanhouden, maar vervangbaar",
    "Aanhouden maar replaceable": "Aanhouden, maar vervangbaar",
    "Hold maar vervangbaar": "Aanhouden, maar vervangbaar",
    "Force alternative duel; upgrade, reduce, replace, or close": "Vervangingsanalyse vereist; verhoog, verlaag, vervang of sluit de positie",
    "Run hedge validity test and compare with alternatives": "Voer een hedge-validiteitstest uit en vergelijk met alternatieven",
    "Fresh capital only after review or at smaller size": "Nieuw kapitaal alleen kleiner of na herbeoordeling inzetten",
    "Position does not pass the fresh-capital test": "Positie voldoet niet aan de nieuw-kapitaaltoets",
    "Position is under replacement review": "Positie staat onder vervangingsreview",
    "Review has persisted for multiple report cycles": "Review loopt al meerdere rapportcycli",
    "Review has persisted for several report cycles": "Review loopt al meerdere rapportcycli",
    "Portfolio role is impaired": "Portefeuillerol is verzwakt",
    "Proposed destination from the rotation plan": "Voorgestelde bestemming uit het rotatieplan",
    "Decision rationale": "Toelichting",
}

RUNTIME_ARTIFACT_REPLACEMENTS_NL: dict[str, str] = {
    "portfolio_state_pricing_audit": "gevalideerde prijsbasis",
    "pricing_audit": "gevalideerde prijsbasis",
    "twelve_data": "externe slotkoersbron",
    "output/etf_valuation_history.csv": "de waarderingshistorie",
    "output/": "",
    "1-3 months": "1-3 maanden",
    "3-12 months": "3-12 maanden",
    "Tier 1": "Niveau 1",
    "Tier 2": "Niveau 2",
    "Tier 3": "Niveau 3",
}

DUTCH_FORBIDDEN_CLIENT_TOKENS = [
    "Do not ask the user",
    "Portfolio implication",
    "Main takeaway",
    "What changed this week",
    "WAT VERANDERDE THIS WEEK",
    "Current holding still leads",
    "Needs sustained relative outperformance",
    "Replacement trigger watch",
    "Confirm thesis fit",
    "and it is not a recommendation",
    "portfolio_state_pricing_audit",
    "pricing_audit",
    "runtime rebuild required",
    "Pending classification",
    "Placeholder for runtime replacement",
    "state-led",
    "workflow",
    "manifest",
    "artifact",
    "output/",
    "runtime NAV",
    "Section 7 uses",
    "Section 15",
    "Keep SMH",
    "Require replacement",
    "Force alternative",
    "but vers kapitaal",
    "but treat",
    "earned leader",
    "price proof",
    "thesisfit",
    "actiebias",
    "reviewpositie",
    "verdiende leider",
    "prijsbewijs",
    "vers kapitaal",
]

DUTCH_DELIVERY_FORBIDDEN_TOKENS = [
    "Wednesday,", "Thursday,", "Friday,", "Saturday,", "Sunday,", "Monday,", "Tuesday,",
    "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December",
    "PRIMARY REGIME", "GEOPOLITICAL REGIME", "MAIN TAKEAWAY",
    "Investor Report", "Investment Report", "Analyst Report",
    "Mixed / not yet decisive", "Keep the current allocation", "confidence",
    "Equity Curve (EUR)", "Portfolio value (EUR)",
    "fresh_cash_smaller_or_review", "failed_fresh_cash_test", "replaceable_status", "review_age_ge_2", "review_age_ge_3",
    "churn_budget_used", "trade_intents", "target_weights", "rotation_decisions",
]

LABELS_NL: dict[str, str] = {
    **SECTION_LABELS_NL,
    **SUMMARY_LABELS_NL,
}

ALL_TEXT_REPLACEMENTS_NL: dict[str, str] = {
    **SECTION_LABELS_NL,
    **SUMMARY_LABELS_NL,
    **TABLE_LABELS_NL,
    **ACTION_STATUS_LABELS_NL,
    **PHRASE_REPLACEMENTS_NL,
    **DECISION_TRANSLATIONS_NL,
    **TRIGGER_TRANSLATIONS_NL,
    **RUNTIME_ARTIFACT_REPLACEMENTS_NL,
}


def lookup_nl(value: Any, mapping: Mapping[str, str], *, default: str | None = None) -> str:
    text = str(value or "").strip()
    if text in mapping:
        return mapping[text]
    lowered = text.lower()
    if lowered in mapping:
        return mapping[lowered]
    return default if default is not None else text


def localize_action_status(value: Any, *, default: str | None = None) -> str:
    return lookup_nl(value, ACTION_STATUS_LABELS_NL, default=default)


def localize_decision_status(value: Any) -> str:
    return lookup_nl(value, DECISION_TRANSLATIONS_NL)


def localize_trigger_status(value: Any) -> str:
    return lookup_nl(value, TRIGGER_TRANSLATIONS_NL)


def localize_label(value: Any) -> str:
    return lookup_nl(value, {**LABELS_NL, **TABLE_LABELS_NL})


def localize_text_aliases(text: Any) -> str:
    out = str(text or "")
    for source, target in sorted(ALL_TEXT_REPLACEMENTS_NL.items(), key=lambda item: len(item[0]), reverse=True):
        out = out.replace(source, target)
    return out
