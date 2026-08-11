from __future__ import annotations

from typing import Any


def _replace_prefixed_line(text: str, prefix: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.startswith(prefix):
            lines[index] = replacement
            break
    suffix = "\n" if text.endswith("\n") else ""
    return "\n".join(lines) + suffix


def finalize_markdown_semantics(text: str, state: dict[str, Any], *, language: str) -> str:
    decision = state.get("current_allocation_decision") if isinstance(state.get("current_allocation_decision"), dict) else {}
    additions = [str(value).strip().upper() for value in decision.get("added_tickers") or [] if str(value).strip()]
    if language == "nl":
        if additions:
            names = " en ".join(additions) if len(additions) <= 2 else ", ".join(additions[:-1]) + " en " + additions[-1]
            text = _replace_prefixed_line(
                text,
                "- **Beste operationele kandidaat:**",
                f"- **Nieuwe funded implementaties:** {names} zijn deze run toegevoegd na EU-lokale re-underwriting, exact-line UCITS/KID-validatie en two-provider completed-close consensus.",
            )
        text = text.replace(
            "1. Een prijsobservatie is geen zelfstandige waarderingsbasis.",
            "1. Een enkele marktprijs of research-only prijsobservatie is geen zelfstandige waarderingsbasis; actuele funded waardering vereist exact-line completed-close consensus uit minimaal twee providers.",
        )
        forbidden = [
            "Beste operationele kandidaat: de geverifieerde S&P 500",
            "Een prijsobservatie is geen zelfstandige waarderingsbasis.",
        ]
    else:
        if additions:
            names = " and ".join(additions) if len(additions) <= 2 else ", ".join(additions[:-1]) + " and " + additions[-1]
            text = _replace_prefixed_line(
                text,
                "- **Best operational candidate:**",
                f"- **New funded implementations:** {names} were added this run after EU-local re-underwriting, exact-line UCITS/KID validation and two-provider completed-close consensus.",
            )
        text = text.replace(
            "1. A price observation is not an independent valuation basis.",
            "1. A single market price or research-only observation is not an independent valuation basis; current funded valuation requires exact-line completed-close consensus from at least two providers.",
        )
        forbidden = [
            "Best operational candidate: the verified S&P 500",
            "A price observation is not an independent valuation basis.",
        ]
    folded = text.casefold()
    residuals = [token for token in forbidden if token.casefold() in folded]
    if residuals:
        raise RuntimeError("Final Markdown semantics contain stale decision wording: " + ", ".join(residuals))
    return text
