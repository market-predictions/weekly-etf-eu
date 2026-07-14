from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATUS_LABELS = {
    "nl": {
        "verified_ucits_trading_line": "UCITS-handelslijn geverifieerd",
        "candidate_requires_verification": "Handelslijn nog te verifiëren",
        "fetch_failed": "Prijs niet beschikbaar",
        "priced_non_authoritative": "Marktprijs beschikbaar",
    },
    "en": {
        "verified_ucits_trading_line": "Verified UCITS trading line",
        "candidate_requires_verification": "Trading line requires verification",
        "fetch_failed": "Price unavailable",
        "priced_non_authoritative": "Market price available",
    },
}

PHRASE_REPLACEMENTS = {
    "nl": {
        "research proxy": "onderzoeksreferentie",
        "funding- of waarderingsautoriteit": "zelfstandige basis voor aankoop of waardering",
        "pricing-line bevestiging": "bevestiging van de handelslijn",
        "trading lines": "handelslijnen",
        "trading line": "handelslijn",
        "research candidates": "onderzoekskandidaten",
        "fundable geworden": "geschikt geworden voor opname in de portefeuille",
        "geen funding vóór volledige verificatie": "geen inzet van kapitaal vóór volledige verificatie",
        "Technologie/semiconductors": "Technologie en halfgeleiders",
        "kandidaat/research": "onderzoekskandidaat",
        "client-facing beslisclaim": "besluitvorming voor de cliënt",
        "valuation-grade ooit wordt overwogen": "de prijsinformatie als voldoende betrouwbaar voor waardering kan worden beschouwd",
        "UCITS-only beleid": "beleid dat uitsluitend UCITS-fondsen toestaat",
        "fundingbeslissing": "afzonderlijk besluit over inzet van kapitaal",
        "portfolio-mutatie": "portefeuillewijziging",
    },
    "en": {
        "pricing-line confirmation": "trading-line confirmation",
        "fundable": "eligible for portfolio inclusion",
        "candidate/research": "research candidate",
        "client-facing decision claim": "client decision",
        "valuation-grade is considered": "the pricing evidence is considered sufficiently reliable for valuation",
    },
}

FORBIDDEN_COMMON = [
    "candidate_requires_verification",
    "verified_ucits_trading_line",
    "priced_non_authoritative",
    "fetch_failed",
    "valuation_grade=",
    "ready_for_controlled_delivery=",
    "send_executed=",
    "transport_attempted=",
    "receipt_confirmed=",
    "funding_authority=",
    "portfolio_mutation=",
    "production_delivery_authority=",
    "8. Authority flags",
    "Authority flags",
]
FORBIDDEN_NL = [
    "research candidates",
    "fundable",
    "pricing-line",
    "client-facing",
    "candidate/research",
    "Technologie/semiconductors",
    "geen funding vóór volledige verificatie",
]
SNAKE_CASE_RE = re.compile(r"\b[a-z]+(?:_[a-z0-9]+){1,}\b")
AUTHORITY_SECTION_RE = re.compile(
    r"\n##\s+8\.\s+Authority flags\s*\n.*\Z",
    flags=re.IGNORECASE | re.DOTALL,
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _forbidden(text: str, language: str) -> list[str]:
    lowered = text.casefold()
    tokens = list(FORBIDDEN_COMMON)
    if language == "nl":
        tokens.extend(FORBIDDEN_NL)
    hits = [token for token in tokens if token.casefold() in lowered]
    hits.extend(sorted(set(SNAKE_CASE_RE.findall(text))))
    return sorted(set(hits))


def sanitize_text(text: str, *, language: str) -> tuple[str, dict[str, Any]]:
    if language not in STATUS_LABELS:
        raise ValueError("language must be nl or en")

    original = text
    authority_present = bool(AUTHORITY_SECTION_RE.search(text))
    text = AUTHORITY_SECTION_RE.sub("\n", text).rstrip() + "\n"

    normalized_labels: list[str] = []
    for source, target in STATUS_LABELS[language].items():
        if source in text:
            text = text.replace(source, target)
            normalized_labels.append(source)

    for source, target in PHRASE_REPLACEMENTS[language].items():
        text = text.replace(source, target)

    if language == "nl":
        text = text.replace(
            "Prijsdata is connectivity/reference evidence uit de huidige routine-run en blijft `valuation_grade=false`.",
            "De getoonde prijzen zijn marktobservaties uit de huidige routine-run en vormen geen zelfstandige basis voor waardering of aankoop.",
        )
    else:
        text = text.replace(
            "Pricing is connectivity/reference evidence from the current routine run and remains `valuation_grade=false`.",
            "The displayed prices are market observations from the current routine run and do not independently authorize valuation or purchase.",
        )

    forbidden = _forbidden(text, language)
    blockers = [f"Forbidden client-surface token remains: {token}" for token in forbidden]
    metadata = {
        "authority_section_removed": authority_present and "Authority flags" not in text,
        "status_labels_normalized": sorted(normalized_labels),
        "forbidden_tokens_detected": forbidden,
        "client_surface_sanitized": not blockers,
        "blockers": blockers,
        "warnings": [],
        "input_sha256": _sha256_text(original),
        "output_sha256": _sha256_text(text),
    }
    return text, metadata


def main() -> None:
    parser = argparse.ArgumentParser(description="Sanitize a Weekly ETF EU client-facing Markdown report.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--language", required=True, choices=["nl", "en"])
    parser.add_argument("--write-result", required=True)
    parser.add_argument("--source-run-id", default="20260712_125000")
    parser.add_argument("--sanitization-run-id", default="20260713_180000")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    source = input_path.read_text(encoding="utf-8")
    sanitized, metadata = sanitize_text(source, language=args.language)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(sanitized, encoding="utf-8")
    result = {
        "schema_version": "etf_eu_client_surface_sanitization_v1",
        "artifact_type": "etf_eu_client_surface_sanitization",
        "generated_at_utc": _utc_now(),
        "source_run_id": args.source_run_id,
        "sanitization_run_id": args.sanitization_run_id,
        "language": args.language,
        "input_path": str(input_path),
        "output_path": str(output_path),
        **metadata,
    }
    result_path = Path(args.write_result)
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["client_surface_sanitized"] is not True:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
