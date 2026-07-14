from __future__ import annotations

import argparse
import html as html_lib
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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
]
SAFE_LABELS = {
    "nl": ["UCITS-handelslijn geverifieerd", "Handelslijn nog te verifiëren", "Prijs niet beschikbaar"],
    "en": ["Verified UCITS trading line", "Trading line requires verification", "Price unavailable"],
}
SNAKE_CASE_RE = re.compile(r"\b[a-z]+(?:_[a-z0-9]+){1,}\b")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _visible_html(raw: str) -> str:
    raw = re.sub(r"<head\b.*?</head>", " ", raw, flags=re.IGNORECASE | re.DOTALL)
    raw = re.sub(r"<(style|script)\b.*?</\1>", " ", raw, flags=re.IGNORECASE | re.DOTALL)
    raw = re.sub(r"<[^>]+>", " ", raw)
    return re.sub(r"\s+", " ", html_lib.unescape(raw)).strip()


def _pdf_text(path: Path) -> str:
    if not shutil.which("pdftotext"):
        raise RuntimeError("pdftotext is required when --pdf is supplied")
    completed = subprocess.run(["pdftotext", "-layout", str(path), "-"], check=True, text=True, capture_output=True)
    return completed.stdout


def validate_surface(*, markdown: Path, language: str, html: Path | None = None, pdf: Path | None = None) -> dict[str, Any]:
    if language not in {"nl", "en"}:
        raise ValueError("language must be nl or en")
    parts = [markdown.read_text(encoding="utf-8")]
    if html is not None:
        parts.append(_visible_html(html.read_text(encoding="utf-8")))
    if pdf is not None:
        parts.append(_pdf_text(pdf))
    combined = "\n".join(parts)
    lowered = combined.casefold()

    forbidden = list(FORBIDDEN_COMMON)
    if language == "nl":
        forbidden.extend(FORBIDDEN_NL)
    forbidden_hits = sorted({token for token in forbidden if token.casefold() in lowered})
    snake_hits = sorted(set(SNAKE_CASE_RE.findall(combined)))
    authority_metadata_visible = any(
        token.casefold() in lowered
        for token in FORBIDDEN_COMMON
        if token.endswith("=") or "Authority flags" in token
    )
    status_labels_client_safe = any(label.casefold() in lowered for label in SAFE_LABELS[language]) and not any(
        token in forbidden_hits
        for token in (
            "candidate_requires_verification",
            "verified_ucits_trading_line",
            "priced_non_authoritative",
            "fetch_failed",
        )
    )

    blockers: list[str] = []
    if forbidden_hits:
        blockers.append("Forbidden client-surface tokens: " + ", ".join(forbidden_hits))
    if snake_hits:
        blockers.append("Snake-case implementation labels: " + ", ".join(snake_hits))
    if authority_metadata_visible:
        blockers.append("Authority or transport metadata is visible on the client surface")
    if not status_labels_client_safe:
        blockers.append("Client-safe status labels were not found or raw status enums remain")

    return {
        "schema_version": "etf_eu_client_surface_clean_v1",
        "artifact_type": "etf_eu_client_surface_clean",
        "generated_at_utc": _utc_now(),
        "language": language,
        "markdown": str(markdown),
        "html": str(html) if html else None,
        "pdf": str(pdf) if pdf else None,
        "client_surface_clean": not blockers,
        "forbidden_tokens": forbidden_hits,
        "snake_case_tokens": snake_hits,
        "authority_metadata_visible": authority_metadata_visible,
        "authority_metadata_absent": not authority_metadata_visible,
        "raw_status_enums_absent": not any("_" in token for token in forbidden_hits + snake_hits),
        "status_labels_client_safe": status_labels_client_safe,
        "blockers": blockers,
        "warnings": [],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a clean Weekly ETF EU client surface.")
    parser.add_argument("--markdown", required=True)
    parser.add_argument("--html", default=None)
    parser.add_argument("--pdf", default=None)
    parser.add_argument("--language", required=True, choices=["nl", "en"])
    parser.add_argument("--write-result", default=None)
    args = parser.parse_args()

    result = validate_surface(
        markdown=Path(args.markdown),
        html=Path(args.html) if args.html else None,
        pdf=Path(args.pdf) if args.pdf else None,
        language=args.language,
    )
    if args.write_result:
        output = Path(args.write_result)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["client_surface_clean"] is not True:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
