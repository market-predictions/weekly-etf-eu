from __future__ import annotations

from runtime.scrub_etf_eu_client_surface_v2 import sanitize_text


def test_dutch_v2_repairs_visible_language_and_semantic_header() -> None:
    source = """# Weekly ETF EU Review | Nederlands | 2026-07-12

| Trading line | ISIN | Markt | Slot | Valuta | Status |
|---|---|---|---:|---|---|
| SXR8 · Xetra | IE00B5BMR087 | 2026-07-10 | 711.48 | EUR | verified_ucits_trading_line |

- De lijnen blijven het verst gevorderd voor verdere broker- en pricing-line bevestiging.
- **Core aandelen:** operationeel volwassen.

1. Prijsobservatie is geen waarderingsautoriteit.
2. Geen portefeuillewijziging zonder afzonderlijke fundingbeslissing.

- Verbeter bronovereenkomst voordat valuation-grade ooit wordt overwogen.
"""
    cleaned, result = sanitize_text(source, language="nl")

    assert result["client_surface_sanitized"] is True
    assert result["semantic_pricing_header_passed"] is True
    assert result["residual_client_language_defects"] == []
    assert "| Handelslijn | ISIN | Peildatum | Slot | Valuta | Status |" in cleaned
    assert "bevestiging bij de broker en van de handelslijn" in cleaned
    assert "Kernaandelen" in cleaned
    assert "Een prijsobservatie is geen zelfstandige waarderingsbasis." in cleaned
    assert "Geen portefeuillewijziging zonder een afzonderlijk besluit over inzet van kapitaal." in cleaned
    assert "Verbeter de bronovereenkomst" in cleaned
    assert "Trading line" not in cleaned
    assert "afzonderlijke afzonderlijk" not in cleaned


def test_english_v2_repairs_operational_jargon_and_header() -> None:
    source = """# Weekly ETF EU Review | English Companion | 2026-07-12

| Trading line | ISIN | Market | Close | Currency | Status |
|---|---|---|---:|---|---|
| SXR8 · Xetra | IE00B5BMR087 | 2026-07-10 | 711.48 | EUR | verified_ucits_trading_line |

U.S. ETF symbols are research proxies only.
The pricing run provides observations, not funding or valuation authority.
Do not fund thematic or gold exposure.
Technology/semiconductors: no funding before full verification.
A price observation is not valuation authority.
No portfolio mutation without a separate funding decision.
"""
    cleaned, result = sanitize_text(source, language="en")

    assert result["client_surface_sanitized"] is True
    assert result["semantic_pricing_header_passed"] is True
    assert result["residual_client_language_defects"] == []
    assert "| Trading line | ISIN | Pricing date | Close | Currency | Status |" in cleaned
    assert "research references only" in cleaned
    assert "not an independent basis for purchase or valuation" in cleaned
    assert "do not allocate capital to thematic or gold exposure" in cleaned
    assert "Technology and semiconductors" in cleaned
    assert "no capital allocation before full verification" in cleaned
    assert "A price observation is not an independent valuation basis." in cleaned
    assert "No portfolio change without a separate capital-allocation decision." in cleaned
