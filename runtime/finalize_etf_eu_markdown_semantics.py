from __future__ import annotations

from typing import Any


def _replace_prefixed_line(text: str, prefix: str, replacement: str) -> tuple[str, bool]:
    lines = text.splitlines()
    replaced = False
    for index, line in enumerate(lines):
        if line.startswith(prefix):
            lines[index] = replacement
            replaced = True
            break
    suffix = "\n" if text.endswith("\n") else ""
    return "\n".join(lines) + suffix, replaced


def _insert_after_prefixed_line(text: str, prefix: str, addition: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.startswith(prefix):
            lines.insert(index + 1, addition)
            suffix = "\n" if text.endswith("\n") else ""
            return "\n".join(lines) + suffix
    raise RuntimeError(f"Cannot insert final ETF EU semantic line; anchor missing: {prefix}")


def _ensure_decision_line(
    text: str,
    *,
    candidate_prefixes: list[str],
    reason_prefix: str,
    replacement: str,
) -> str:
    for prefix in candidate_prefixes:
        updated, replaced = _replace_prefixed_line(text, prefix, replacement)
        if replaced:
            return updated
    if replacement in text:
        return text
    return _insert_after_prefixed_line(text, reason_prefix, replacement)


def finalize_markdown_semantics(text: str, state: dict[str, Any], *, language: str) -> str:
    decision = state.get("current_allocation_decision") if isinstance(state.get("current_allocation_decision"), dict) else {}
    additions = [str(value).strip().upper() for value in decision.get("added_tickers") or [] if str(value).strip()]
    required: list[str] = []
    if language == "nl":
        if additions:
            names = " en ".join(additions) if len(additions) <= 2 else ", ".join(additions[:-1]) + " en " + additions[-1]
            decision_line = f"- **Nieuwe funded implementaties:** {names} zijn deze run toegevoegd na EU-lokale re-underwriting, exact-line UCITS/KID-validatie en geautoriseerde completed-close pricing."
            text = _ensure_decision_line(
                text,
                candidate_prefixes=["- **Beste operationele kandidaat:**", "- **Meest volwassen operationele kandidaat:**"],
                reason_prefix="- **Reden:**",
                replacement=decision_line,
            )
            required.append(f"**Nieuwe funded implementaties:** {names}")
        replacements = {
            "1. Een prijsobservatie is geen zelfstandige waarderingsbasis.": "1. Een enkele marktprijs of research-only prijsobservatie is geen zelfstandige waarderingsbasis; actuele funded waardering vereist een geautoriseerde exact-line completed-close primary prijs. Een onafhankelijke verifier verhoogt de confidence; same-date disagreement blokkeert de waardering.",
            "Voor alle gefinancierde posities is een actuele koerscontrole met twee onafhankelijke bronnen beschikbaar; de spreads zijn verwaarloosbaar.": "Voor alle gefinancierde posities is een geautoriseerde exact-line completed-close primary prijs beschikbaar; onafhankelijke verificatie verhoogt de confidence en same-date disagreement blokkeert de waardering.",
            "Voor elke positie is de actuele koers gecontroleerd via twee bronnen (Alpha Vantage en Yahoo).": "Voor elke gefinancierde positie is de actuele koers gebonden aan de geautoriseerde primary completed-close bron; beschikbare onafhankelijke verificatie wordt afzonderlijk als confidence-evidence vastgelegd.",
            "Behoud kwaliteit en kasdiscipline; any allocation still requires a verified UCITS instrument, current pricing, re-underwriting and a separate capital decision.": "Behoud kwaliteit en kasdiscipline; iedere allocatie vereist een geverifieerd UCITS-instrument, actuele pricing, re-underwriting en een afzonderlijk kapitaalbesluit.",
            "Europese aandelen- of obligatieblootstelling blijft afhankelijk on UCITS identity, exact-line verification, current pricing, re-underwriting and a separate capital decision.": "Europese aandelen- of obligatieblootstelling blijft afhankelijk van UCITS-identiteit, exact-line verificatie, actuele pricing, re-underwriting en een afzonderlijk kapitaalbesluit.",
            "No material regime change was recorded versus the prior review; the Risk-on growth backdrop remained intact, market breadth is mixed, and cross-asset confirmation is mixed.": "Ten opzichte van de vorige review is geen materiële regimewijziging vastgesteld; de risk-on-groeiomgeving bleef intact, terwijl marktbreedte en cross-asset bevestiging gemengd zijn.",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        forbidden = [
            "Beste operationele kandidaat: de geverifieerde S&P 500",
            "Meest volwassen operationele kandidaat: de geverifieerde S&P 500",
            "Een prijsobservatie is geen zelfstandige waarderingsbasis.",
            "two-provider completed-close consensus",
            "twee onafhankelijke bronnen beschikbaar",
            "actuele koers gecontroleerd via twee bronnen",
            "any allocation still requires",
            "afhankelijk on UCITS identity",
            "No material regime change was recorded",
        ]
    else:
        if additions:
            names = " and ".join(additions) if len(additions) <= 2 else ", ".join(additions[:-1]) + " and " + additions[-1]
            decision_line = f"- **New funded implementations:** {names} were added this run after EU-local re-underwriting, exact-line UCITS/KID validation and authorized completed-close pricing."
            text = _ensure_decision_line(
                text,
                candidate_prefixes=["- **Best operational candidate:**", "- **Most advanced operational candidate:**", "- **Most mature operational candidate:**"],
                reason_prefix="- **Reason:**",
                replacement=decision_line,
            )
            required.append(f"**New funded implementations:** {names}")
        replacements = {
            "1. A price observation is not an independent valuation basis.": "1. A single market price or research-only observation is not an independent valuation basis; current funded valuation requires an authorized exact-line completed-close primary price. An independent verifier increases confidence; same-date disagreement blocks valuation.",
            "A current price verification with two independent sources is available for all funded positions; spreads are immaterial.": "An authorized exact-line completed-close primary price is available for every funded position; independent verification increases confidence and same-date disagreement blocks valuation.",
            "Each position's current price is checked through two sources (Alpha Vantage and Yahoo).": "Each funded position's current price is bound to the authorized primary completed-close source; available independent verification is recorded separately as confidence evidence.",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        forbidden = [
            "Best operational candidate: the verified S&P 500",
            "Most advanced operational candidate: the verified S&P 500",
            "Most mature operational candidate: the verified S&P 500",
            "A price observation is not an independent valuation basis.",
            "two-provider completed-close consensus",
            "two independent sources is available for all funded positions",
            "current price is checked through two sources",
        ]
    folded = text.casefold()
    residuals = [token for token in forbidden if token.casefold() in folded]
    missing = [token for token in required if token.casefold() not in folded]
    if residuals or missing:
        raise RuntimeError(
            "Final Markdown semantics invalid: "
            + f"residual_stale={residuals}; missing_current={missing}"
        )
    return text
