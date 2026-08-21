#!/usr/bin/env python3
"""
Deterministic Markdown semantic regression validator for ETF EU.

Fails when retired universal two-provider liveness wording reappears.
Passes when corrected NL/EN artifacts match the primary-close-plus-optional-verification authority.
"""

from __future__ import annotations

import re
from typing import Any


def validate_semantic_regression(text: str, *, language: str) -> list[str]:
    """
    Validate that Markdown text does not contain retired universal two-provider liveness wording.

    Args:
        text: Markdown text to validate.
        language: Language of the text ('nl' or 'en').

    Returns:
        List of validation errors. Empty list means pass.
    """
    errors: list[str] = []

    # Retired universal two-provider liveness wording (old)
    retired_two_provider_phrases = {
        "nl": [
            "actuele funded waardering vereist exact-line completed-close consensus uit minimaal twee providers",
            "exact-line completed-close consensus uit minimaal twee providers",
            "minimaal twee providers",
            "exact-line completed-close consensus uit twee providers",
        ],
        "en": [
            "current funded valuation requires exact-line completed-close consensus from at least two providers",
            "exact-line completed-close consensus from at least two providers",
            "at least two providers",
            "exact-line completed-close consensus from two providers",
        ],
    }

    # Corrected primary-close-plus-optional-verification wording (new)
    corrected_phrases = {
        "nl": [
            "een correct geïdentificeerde exacte completed-close van een gekwalificeerde primary provider kan waardering-grade zijn",
            "onafhankelijke verificatie verhoogt de vertrouwenswaardigheid",
            "Same-date provider disagreement blijft expliciet fail-closed",
            "stale/no-exact/broken-primary gevallen blijven geblokkeerd",
        ],
        "en": [
            "a correctly identified exact completed-close from a qualified primary provider can be valuation-grade",
            "independent verification improves confidence",
            "Same-date provider disagreement remains explicitly fail-closed",
            "stale/no-exact/broken-primary cases remain blocked",
        ],
    }

    # Check for retired phrases
    retired = retired_two_provider_phrases.get(language, [])
    for phrase in retired:
        if phrase in text:
            errors.append(
                f"Retired universal two-provider liveness wording found in {language} Markdown: '{phrase}'"
            )

    # Check that corrected phrases are present (at least one)
    corrected = corrected_phrases.get(language, [])
    found_corrected = any(phrase in text for phrase in corrected)
    if not found_corrected:
        errors.append(
            f"Corrected primary-close-plus-optional-verification wording not found in {language} Markdown"
        )

    return errors


def validate_semantic_regression_from_file(path: str, *, language: str) -> list[str]:
    """
    Validate semantic regression from a file path.

    Args:
        path: Path to Markdown file.
        language: Language of the text ('nl' or 'en').

    Returns:
        List of validation errors. Empty list means pass.
    """
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    return validate_semantic_regression(text, language=language)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: validate_etf_eu_markdown_semantic_regression.py <path> <language>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    language = sys.argv[2].lower()

    errors = validate_semantic_regression_from_file(path, language=language)

    if errors:
        print("Semantic regression validation FAILED:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)
    else:
        print("Semantic regression validation PASSED")
        sys.exit(0)