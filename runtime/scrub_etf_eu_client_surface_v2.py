from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from runtime.scrub_etf_eu_client_surface import sanitize_text as sanitize_text_v1

FINAL_REPLACEMENTS = {
    "nl": {
        "| Trading line | ISIN | Markt | Slot | Valuta | Status |": "| Handelslijn | ISIN | Peildatum | Slot | Valuta | Status |",
        "voor verdere broker- en bevestiging van de handelslijn": "voor verdere bevestiging bij de broker en van de handelslijn",
        "Geen portefeuillewijziging zonder afzonderlijke afzonderlijk besluit over inzet van kapitaal.": "Geen portefeuillewijziging zonder een afzonderlijk besluit over inzet van kapitaal.",
        "Prijsobservatie is geen waarderingsautoriteit.": "Een prijsobservatie is geen zelfstandige waarderingsbasis.",
        "Core aandelen": "Kernaandelen",
        "Core-aandelen": "Kernaandelen",
        "EUNA/AGGH kunnen later stabiliteit leveren; huidige rol blijft onderzoekskandidaat.": "EUNA/AGGH kunnen later stabiliteit leveren; hun huidige rol blijft die van onderzoekskandidaat.",
        "Europese blootstelling betreft vaak ETC-structuren; geblokkeerd binnen beleid dat uitsluitend UCITS-fondsen toestaat totdat een expliciete beleidsbeslissing bestaat.": "Europese blootstelling betreft vaak ETC-structuren en blijft geblokkeerd binnen het beleid dat uitsluitend UCITS-fondsen toestaat, totdat een expliciete beleidsbeslissing bestaat.",
        "Verbeter bronovereenkomst": "Verbeter de bronovereenkomst",
    },
    "en": {
        "| Trading line | ISIN | Market | Close | Currency | Status |": "| Trading line | ISIN | Pricing date | Close | Currency | Status |",
        "U.S. ETF symbols are research proxies only": "U.S. ETF symbols are research references only",
        "not funding or valuation authority": "not an independent basis for purchase or valuation",
        "do not fund thematic or gold exposure": "do not allocate capital to thematic or gold exposure",
        "Technology/semiconductors": "Technology and semiconductors",
        "no funding before full verification": "no capital allocation before full verification",
        "their current role remains research candidate": "their current role remains that of research candidates",
        "A price observation is not valuation authority.": "A price observation is not an independent valuation basis.",
        "No portfolio mutation without a separate funding decision.": "No portfolio change without a separate capital-allocation decision.",
    },
}

REQUIRED_HEADER = {
    "nl": "| Handelslijn | ISIN | Peildatum | Slot | Valuta | Status |",
    "en": "| Trading line | ISIN | Pricing date | Close | Currency | Status |",
}

FORBIDDEN_FINAL = {
    "nl": [
        "Trading line",
        "broker- en bevestiging",
        "afzonderlijke afzonderlijk",
        "waarderingsautoriteit",
        "Core aandelen",
        "Core-aandelen",
    ],
    "en": [
        "not funding or valuation authority",
        "do not fund thematic or gold exposure",
        "no funding before full verification",
        "No portfolio mutation without a separate funding decision",
        "Technology/semiconductors",
    ],
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sanitize_text(text: str, *, language: str) -> tuple[str, dict[str, Any]]:
    if language not in {"nl", "en"}:
        raise ValueError("language must be nl or en")

    cleaned, metadata = sanitize_text_v1(text, language=language)
    repairs: list[str] = []
    for source, target in FINAL_REPLACEMENTS[language].items():
        if source in cleaned:
            cleaned = cleaned.replace(source, target)
            repairs.append(source)

    residual = [token for token in FORBIDDEN_FINAL[language] if token.casefold() in cleaned.casefold()]
    header_ok = REQUIRED_HEADER[language] in cleaned
    blockers = [blocker for blocker in metadata.get("blockers", []) if "Forbidden client-surface token remains" not in blocker]
    blockers.extend(f"Residual client-language defect: {token}" for token in residual)
    if not header_ok:
        blockers.append("Pricing table header is not client-safe or does not describe the pricing-date column")

    result = {
        **metadata,
        "schema_version": "etf_eu_client_surface_sanitization_v2",
        "client_language_contract_v2": True,
        "client_language_repairs": sorted(repairs),
        "semantic_pricing_header_passed": header_ok,
        "residual_client_language_defects": sorted(residual),
        "output_sha256": _sha256_text(cleaned),
        "client_surface_sanitized": not blockers,
        "blockers": blockers,
    }
    return cleaned, result


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply the Weekly ETF EU client-surface and client-language contract v2.")
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
    cleaned, metadata = sanitize_text(source, language=args.language)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(cleaned, encoding="utf-8")
    result = {
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
